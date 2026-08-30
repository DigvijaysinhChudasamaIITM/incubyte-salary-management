import importlib.util
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_vercel_entrypoint_exports_app_with_probe_aliases() -> None:
    entrypoint = Path(__file__).parents[2] / "api" / "index.py"
    spec = importlib.util.spec_from_file_location("vercel_entrypoint", entrypoint)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    assert isinstance(module.app, FastAPI)
    client = TestClient(module.app)
    documented_paths = client.get("/openapi.json").json()["paths"]
    assert "/api/employees" in documented_paths
    assert "/api/health" in documented_paths
    assert "/api/ready" in documented_paths
    assert client.get("/api/health").json() == {"status": "ok"}
    assert client.get("/api/ready").json() == {"status": "ready"}
