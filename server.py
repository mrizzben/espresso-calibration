import http.server
import json
import sqlite3
import urllib.parse
import os

DB_PATH = "shots.db"

# ponytail: zero external deps — http.server + sqlite3 are stdlib
# ponytail: synchronous server — single-user, fine for this
# ponytail: auto-creates .db file on first run, ALTER TABLE for existing DBs
# ponytail: serves static files too, one process for everything

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS shots ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "grind REAL NOT NULL,"
        "dose REAL NOT NULL,"
        "yield REAL NOT NULL,"
        "time REAL NOT NULL,"
        "machine TEXT NOT NULL DEFAULT 'La Marzocco GS3 MP',"
        "grinder TEXT NOT NULL DEFAULT 'Mahlkönig EK43',"
        "created_at TEXT DEFAULT (datetime('now')),"
        "notes TEXT DEFAULT ''"
        ")"
    )
    conn.commit()
    # ponytail: migrate existing DBs that lack machine/grinder columns
    try:
        conn.execute("ALTER TABLE shots ADD COLUMN machine TEXT NOT NULL DEFAULT 'La Marzocco GS3 MP'")
    except sqlite3.OperationalError:
        pass  # column already exists
    try:
        conn.execute("ALTER TABLE shots ADD COLUMN grinder TEXT NOT NULL DEFAULT 'Mahlkönig EK43'")
    except sqlite3.OperationalError:
        pass  # column already exists
    conn.commit()
    try:
        conn.execute("ALTER TABLE shots ADD COLUMN notes TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass  # column already exists
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class Handler(http.server.BaseHTTPRequestHandler):
    def _json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _error(self, msg, status=400):
        self._json({"error": msg}, status)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path.startswith("/api/"):
            self._handle_api_get()
        else:
            self._serve_static()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self._handle_api_post()
        else:
            self._error("Not found", 404)

    def do_DELETE(self):
        if self.path.startswith("/api/"):
            self._handle_api_delete()
        else:
            self._error("Not found", 404)

    def _handle_api_get(self):
        conn = get_db()
        rows = conn.execute("SELECT * FROM shots ORDER BY created_at DESC").fetchall()
        conn.close()
        self._json([dict(r) for r in rows])

    def _handle_api_post(self):
        try:
            data = self._read_body()
        except (json.JSONDecodeError, ValueError):
            self._error("Invalid JSON body")
            return
        for field in ("grind", "dose", "yield", "time"):
            if field not in data:
                self._error(f"Missing field: {field}")
                return
            if not isinstance(data[field], (int, float)):
                self._error(f"{field} must be a number")
                return
        machine = data.get("machine", "La Marzocco GS3 MP")
        grinder = data.get("grinder", "Mahlkönig EK43")
        notes = data.get("notes", "")
        if not isinstance(machine, str) or not isinstance(grinder, str):
            self._error("machine and grinder must be strings")
            return
        conn = get_db()
        cur = conn.execute(
            "INSERT INTO shots (grind, dose, yield, time, machine, grinder, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (data["grind"], data["dose"], data["yield"], data["time"], machine, grinder, notes),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM shots WHERE id = ?", (cur.lastrowid,)).fetchone()
        conn.close()
        self._json({"id": row["id"], "created_at": row["created_at"]}, 201)

    def _handle_api_delete(self):
        parsed = urllib.parse.urlparse(self.path)
        parts = parsed.path.strip("/").split("/")
        conn = get_db()
        if len(parts) == 2:
            conn.execute("DELETE FROM shots WHERE id = ?", (parts[1],))
        else:
            conn.execute("DELETE FROM shots")
        conn.commit()
        conn.close()
        self._json({"ok": True})

    def _serve_static(self):
        path = self.path.lstrip("/") or "index.html"
        if not os.path.isfile(path):
            self._error("Not found", 404)
            return
        with open(path, "rb") as f:
            body = f.read()
        self.send_response(200)
        ct = "text/html" if path.endswith(".html") else "application/octet-stream"
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # ponytail: quiet logs

if __name__ == "__main__":
    init_db()
    server = http.server.HTTPServer(("0.0.0.0", 8080), Handler)
    print("Serving at http://localhost:8080")
    server.serve_forever()