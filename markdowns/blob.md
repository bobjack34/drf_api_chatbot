# Tutorial: Django-View ruft ein CLI-Tool auf und gibt die Ergebnisse strukturiert zurück

Dieses Tutorial zeigt:

1. Wie ein DRF-Serializer ein Modell + zusätzliches Payload-Feld verarbeitet
2. Wie eine Django-View ein externes CLI-Python-Tool ausführt
3. Wie man stdout robust einliest (auch wenn Debug-Lines enthalten sind)
4. Wie das Ergebnis in ein Job-Modell gespeichert wird
5. Wie die API eine klare, saubere Antwort zurückgibt


# 1. Zielarchitektur

Request an `/api/blobs/process`:

```json
{
  "name": "testjob",
  "payload": "BASE64..."
}
```

Ablauf:

1. DRF validiert Metadaten
2. View ruft `cli_tool.py` auf
3. CLI verarbeitet die Base64-Daten
4. CLI gibt JSON zurück
5. View parst CLI-JSON robust
6. Ein BlobJob wird erstellt → Status "done"
7. Response gibt Job-Infos + CLI-Ergebnis zurück

---

# 2. Serializer: Metadaten + extra Feld "payload"

```python
# blobs/api/serializers.py
from rest_framework import serializers
from blobs import models

class BlobModelSerializer(serializers.ModelSerializer):
    payload = serializers.CharField(write_only=True)

    class Meta:
        model = models.BlobJob
        fields = ["id", "name", "created_at", "payload"]

    def create(self, validated_data):
        # Payload nicht speichern
        validated_data.pop("payload", None)
        return super().create(validated_data)
```

`payload` ist write_only → kommt rein, wird validiert, aber NICHT gespeichert.

---

# 3. Das CLI-Tool (cli_tool.py)

```python
import argparse
import base64
import json
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload", required=True)
    args = parser.parse_args()

    t0 = time.perf_counter()
    binary = base64.b64decode(args.payload)
    time.sleep(1.1)
    t1 = time.perf_counter()

    result = {
        "processed_bytes": len(binary),
        "calculation_time": t1 - t0,
    }

    print(json.dumps(result))
```

Wichtig: Gibt ein **JSON-Objekt auf stdout** aus.

---

# 4. URL-Routing

```python
# blobs/api/urls.py
from django.urls import path
from .views import BlobForwardAPIView

urlpatterns = [
    path("process", BlobForwardAPIView.as_view()),
]
```

---

# 5. Die View: CLI ausführen + JSON robust einlesen

```python
# blobs/api/views.py
import json
import subprocess
from pathlib import Path

from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import BlobModelSerializer
from blobs import models


class BlobForwardAPIView(APIView):
    """Aufruf nach INTERN."""

    def post(self, request):
        # 1) Metadaten validieren
        serializer = BlobModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = request.data.get("payload")
        if not payload:
            return Response({"error": "payload missing"}, status=400)

        # 2) Pfad zum CLI-Tool
        tool = Path(__file__).resolve().parent.parent.parent.parent / "cli_tool.py"

        # 3) CLI aufrufen
        result = subprocess.run(
            ["python", str(tool), f"--payload={payload}"],
            capture_output=True,
            text=True,
        )

        raw = result.stdout.strip()

        # 4) Robust: letzte Zeile als JSON interpretieren
        last_line = raw.splitlines()[-1] if raw else ""

        try:
            cli_json = json.loads(last_line)
        except json.JSONDecodeError:
            return Response(
                {
                    "error": "CLI returned invalid JSON",
                    "stdout": raw,
                    "stderr": result.stderr,
                },
                status=500,
            )

        # CLI Felder
        calculation_time = cli_json.get("calculation_time")
        processed_bytes = cli_json.get("processed_bytes")

        # eigene Zusatzinfo: Länge des Base64 Strings
        blob_size = len(payload)
        return_code = result.returncode

        # 5) Job speichern
        job = serializer.save(status="done")

        # 6) Finale API-Antwort
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
```

---

# 6. Typischer Response

```json
{
  "job_id": 42,
  "status": "done",
  "return_code": 0,
  "calculation_time": 1.1039,
  "processed_bytes": 4096,
  "blob_size": 5500
}
```


# 8. Optional: Noch besseres JSON-Parsing

Falls du sicherstellen willst, dass auch *irgendwo in stdout* JSON vorkommt:

```python
cli_json = {}
for line in raw.splitlines():
    try:
        cli_json = json.loads(line)
        break
    except json.JSONDecodeError:
        continue
```
