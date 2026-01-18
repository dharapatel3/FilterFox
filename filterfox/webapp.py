from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json

from flask import Flask, render_template, request, redirect, url_for, flash

from .config import FilterFoxConfig
from .engine import run_filterfox

APP_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = APP_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_PATH = DATA_DIR / "history.json"


def load_history():
    if HISTORY_PATH.exists():
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    return []


def save_history(items):
    HISTORY_PATH.write_text(json.dumps(items, indent=2), encoding="utf-8")


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "filterfox-dev-secret"  # ok for local MVP

    @app.get("/")
    def index():
        cfg = FilterFoxConfig()
        return render_template("index.html", defaults=cfg)

    @app.post("/preview")
    def preview():
        cfg = FilterFoxConfig(
            gmail_query=request.form.get("gmail_query", "").strip() or "newer_than:30d in:inbox",
            max_results=int(request.form.get("max_results", "200")),
            dry_run=True,
            label_prefix=request.form.get("label_prefix", "").strip() or "FilterFox",
        )

        try:
            run = run_filterfox(cfg)
        except Exception as e:
            import traceback
            traceback.print_exc() #this SHOULD print the full traceback for any errors in the terminal
            flash(f"Error: {e}", "error")
            return redirect(url_for("index"))

        hist = load_history()
        hist.insert(0, {
            "ts": datetime.utcnow().isoformat() + "Z",
            "mode": "preview",
            "query": cfg.gmail_query,
            "max": cfg.max_results,
            "prefix": cfg.label_prefix,
            "stats": {k: run[k] for k in ["found", "classified", "skipped", "applied"]},
        })
        save_history(hist[:50])

        return render_template("results.html", mode="Preview", run=run, cfg=cfg)

    @app.post("/apply")
    def apply():
        cfg = FilterFoxConfig(
            gmail_query=request.form.get("gmail_query", "").strip() or "newer_than:30d in:inbox",
            max_results=int(request.form.get("max_results", "200")),
            dry_run=False,
            label_prefix=request.form.get("label_prefix", "").strip() or "FilterFox",
        )

        try:
            run = run_filterfox(cfg)
        except Exception as e:
            flash(f"Error: {e}", "error")
            return redirect(url_for("index"))

        hist = load_history()
        hist.insert(0, {
            "ts": datetime.utcnow().isoformat() + "Z",
            "mode": "apply",
            "query": cfg.gmail_query,
            "max": cfg.max_results,
            "prefix": cfg.label_prefix,
            "stats": {k: run[k] for k in ["found", "classified", "skipped", "applied"]},
        })
        save_history(hist[:50])

        return render_template("results.html", mode="Applied", run=run, cfg=cfg)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5055)