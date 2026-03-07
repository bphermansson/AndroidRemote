from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
STATIC_DIR = BASE_DIR / "static"
CONFIG_PATH = BASE_DIR / "commands.json"


class CommandRequest(BaseModel):
    command_id: str


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise RuntimeError(f"Missing config file: {CONFIG_PATH}")
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def verify_token(authorization: str | None) -> None:
    config = load_config()
    expected = str(config.get("api_token", "")).strip()
    if not expected:
        raise HTTPException(status_code=500, detail="api_token is not configured")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    got = authorization.replace("Bearer ", "", 1).strip()
    if got != expected:
        raise HTTPException(status_code=401, detail="Invalid token")


app = FastAPI(title="Android Remote Commands")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(APP_DIR / "index.html")


@app.get("/api/commands")
def list_commands(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    verify_token(authorization)
    config = load_config()
    commands = config.get("commands", [])
    safe = [{"id": c["id"], "title": c["title"]} for c in commands]
    return {"commands": safe}


@app.post("/api/run")
def run_command(
    request: CommandRequest, authorization: str | None = Header(default=None)
) -> dict[str, Any]:
    verify_token(authorization)
    config = load_config()
    command = next((c for c in config.get("commands", []) if c["id"] == request.command_id), None)
    if command is None:
        raise HTTPException(status_code=404, detail="Unknown command_id")

    cmd = command.get("command")
    timeout = int(command.get("timeout_seconds", 20))
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail=f"Command timed out after {timeout}s")

    return {
        "ok": result.returncode == 0,
        "return_code": result.returncode,
        "stdout": result.stdout[-5000:],
        "stderr": result.stderr[-5000:],
    }
