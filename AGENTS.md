<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->

# Espresso Calibration — AGENTS.md

## Stack

- **Backend:** one-file Python (`server.py`), stdlib only (`http.server` + `sqlite3`). No dependencies, no virtualenv, no `requirements.txt`. No test runner, no CI.
- **Frontend:** one-file vanilla HTML/JS/CSS (`index.html`). No frameworks, no build step, no bundler.
- **Prediction:** ordinary least squares linear regression, computed client-side in the browser JS.
- **DB:** `shots.db` auto-created by `server.py` on first run (gitignored).

## Run

```bash
python3 server.py
# → Serving at http://localhost:8080
```

## API

All endpoints under `/api/`. CORS open (`Access-Control-Allow-Origin: *`).

| Method | Path | Body | Action |
|--------|------|------|--------|
| `GET` | `/api/shots` | — | List all shots (newest first) |
| `POST` | `/api/shots` | `{grind, dose, yield, time}` | Log a shot (returns `{id, created_at}`) |
| `DELETE` | `/api/shots` | — | Delete all shots |
| `DELETE` | `/api/shots/:id` | — | Delete one shot |

Required POST fields: `grind` (REAL), `dose` (REAL), `yield` (REAL), `time` (REAL). Optional: `machine` (str, default `"La Marzocco GS3 MP"`), `grinder` (str, default `"Mahlkönig EK43"`).

## Conventions

- **Ponytail style** — this repo was built with the ponytail philosophy (lazy, minimal, no abstractions). Keep changes small, prefer stdlib, avoid adding dependencies or abstractions.
- **No generated code** — everything is hand-written. No codegen, no migrations, no build artifacts.
- **Prediction is client-side** — the JS in `index.html` does the linear regression. The server is just a CRUD API.

## Speckit / OpenCode

- This file is the Speckit context file (`init-options.json: context_file: "AGENTS.md"`).
- Speckit commands follow the pattern `speckit.<command>` (e.g. `speckit.plan`, `speckit.implement`).
- The `.specify/` and `.opencode/` directories are gitignored — local tooling only.