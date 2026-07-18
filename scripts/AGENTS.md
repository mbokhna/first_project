# Scripts

Start/stop the app's Docker container.

- `start.sh` (Mac/Linux) / `start.bat` (Windows) — builds the `pm-app` image from the root `Dockerfile` and runs it as container `pm-app`, publishing port 8000, loading env vars from the root `.env`.
- `stop.sh` / `stop.bat` — removes the running `pm-app` container.

Usage:

```bash
./scripts/start.sh
./scripts/stop.sh
```

App is then available at http://localhost:8000.
