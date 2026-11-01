"""Isolated local PostgreSQL configuration; never creates an application account."""

import os
from pathlib import Path
import secrets
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".local/development.env"


def main():
    command, *args = sys.argv[1:] or ["help"]
    if command == "init":
        ENV_FILE.parent.mkdir(exist_ok=True, mode=0o700)
        if ENV_FILE.exists():
            print("Local configuration already exists; preserved.")
            return
        password = secrets.token_hex(32)
        with open(ENV_FILE, "x", opener=lambda p, f: os.open(p, f, 0o600)) as stream:
            stream.write(
                f"NAKRE_LOCAL_DB_PASSWORD={password}\nDATABASE_URL=postgresql://nakre_local:{password}@127.0.0.1:55432/nakre_local\nDJANGO_SECRET_KEY={secrets.token_urlsafe(64)}\nDJANGO_SETTINGS_MODULE=config.settings.development\n"
            )
        print("Created ignored local configuration (no application account).")
        return
    if command not in ("up", "down", "manage"):
        raise SystemExit(
            "Usage: python scripts/dev.py init|up|down|manage <Django arguments>"
        )
    env = os.environ.copy()
    for line in ENV_FILE.read_text().splitlines():
        key, value = line.split("=", 1)
        env[key] = value
    if command in ("up", "down"):
        cmd = [
            "docker",
            "compose",
            "--project-name",
            "nakre-lot1",
            "--env-file",
            str(ENV_FILE),
        ]
        cmd += ["up", "-d", "--wait", "db"] if command == "up" else ["down"]
    else:
        cmd = [str(ROOT / ".venv/bin/python"), "manage.py", *args]
    raise SystemExit(subprocess.call(cmd, cwd=ROOT, env=env))


if __name__ == "__main__":
    main()
