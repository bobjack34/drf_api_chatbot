import json
from pathlib import Path
import subprocess

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class PayloadRequest(BaseModel):
    payload: str
    job_id: str | None = None
    name: str | None = None


@app.post("/process")
def process_blob(data: PayloadRequest):
    # CLI direkt mit Base64-Payload aufrufen

    tool_path = Path(__file__).parent / "cli_tool.py"
    result = subprocess.run(
        ["python", tool_path, f"--payload={data.payload}"],
        capture_output=True,
        text=True,
    )

    try:
        cli_json = json.loads(result.stdout)
    except json.JSONDecodeError:
        cli_json = {"raw_stdout": result.stdout}

    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "blob_size": len(data.payload),
        "calculation_time": cli_json.get("calculation_time"),
        "processed_bytes": cli_json.get("processed_bytes"),
    }
