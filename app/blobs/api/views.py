import json
from pathlib import Path
import subprocess

import requests
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import BlobModelSerializer


class BlobAPIView(APIView):
    """Aufruf nach INTERN."""

    permission_classes = []
    authentication_classes = []

    def post(self, request):
        # 1) Validieren
        serializer = BlobModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = request.data.get("payload")
        if not payload:
            return Response({"error": "payload missing"}, status=400)

        # 2) CLI-Tool aufrufen (liegt in local_blob_job/)
        tool = Path(__file__).resolve().parent.parent.parent.parent
        tool = tool / "local_blob_job" / "cli_tool.py"

        result = subprocess.run(
            ["python", str(tool), f"--payload={payload}"],
            capture_output=True,
            text=True,
        )

        # 3) CLI-JSON einlesen
        raw = result.stdout.strip()
        last_line = raw.splitlines()[-1] if raw else ""

        try:
            cli_json = json.loads(last_line)
        except json.JSONDecodeError:
            return Response(
                {
                    "error": "CLI output was not valid JSON",
                    "stdout": raw,
                    "stderr": result.stderr,
                },
                status=500,
            )

        calculation_time = cli_json.get("calculation_time")
        processed_bytes = cli_json.get("processed_bytes")

        # eigene Zusatzinfo
        blob_size = len(payload)  # Base64 Länge

        return_code = result.returncode

        # 4) BlobJob speichern
        job = serializer.save(
            status="done"
        )  # funktioniert, Feld muss im Model existieren

        # 5) Response zurückgeben
        return Response(
            {
                "job_id": job.id,
                "status": job.status,
                "return_code": return_code,
                "calculation_time": calculation_time,
                "processed_bytes": processed_bytes,
                "blob_size": blob_size,
            }
        )


class BlobModelForwardAPIView(APIView):
    """Aufruf nach EXTERN (Fastapi remote)"""

    # keine Authentifizierung nötig
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = BlobModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # erstellt DB-Eintrag ohne payload
        # siehe serializers/BlobModelSerializer -> create()
        job = serializer.save()

        # Den BLOB aus den Request Daten holen.
        payload = request.data["payload"]

        # Die URL eines entfernten Services (hier der remote_blob_job,
        # der mit uvicorn und FastAPI betrieben wird)
        remote_url = "http://127.0.0.1:8080/process"

        try:
            resp = requests.post(remote_url, json={"payload": payload}, timeout=60)
            data = resp.json()
        except Exception as exc:
            job.status = "error"
            job.save(update_fields=["status"])
            return Response({"error": str(exc)}, status=500)

        # neue Daten aus FastAPI
        calculation_time = data.get("calculation_time")
        processed_bytes = data.get("processed_bytes")
        blob_size = data.get("blob_size")
        return_code = data.get("returncode")

        # Job Status setzen und neu speichern
        job.status = "done"
        job.save()

        return Response(
            {
                "job_id": job.id,
                "status": job.status,
                "return_code": return_code,
                "calculation_time": calculation_time,
                "processed_bytes": processed_bytes,
                "blob_size": blob_size,
            }
        )
