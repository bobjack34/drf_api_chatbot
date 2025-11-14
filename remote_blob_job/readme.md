# FastAPI Blob Processor

Dieser Microservice nimmt einen Base64-Blob entgegen und verarbeitet ihn
über ein CLI-Tool (`cli_tool.py`).



## Starten

```sh
uv add uvicorn fastapi
uv run uvicorn service:app --port 8080 --reload
````

Service läuft unter:

```
http://127.0.0.1:8080/docs
```

## Beispiel-Request

POST `/process`:

```json
{
  "payload": "aGVsbG8gd29ybGQ=",
  "job_id": "42",
  "name": "TestJob"
}
``` 
