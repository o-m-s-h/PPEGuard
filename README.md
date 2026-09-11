# PPEGuard API

FastAPI uploads backed by the same YOLO inference and reporting services as the CLI.
Requires Python 3.10+ and trained weights at `models/best.pt`.

## Run locally (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/docs. Expand either POST endpoint, click **Try it out**,
choose a file in the `file` field, and execute. The response includes the report
and three URLs in `files`: `annotated`, `json_report`, and `csv_report`.
Open those URLs to download the results. No frontend is required.

Alternatively, upload directly with curl (use `curl.exe` in PowerShell):

```powershell
curl.exe -f -X POST "http://127.0.0.1:8000/detect/image?conf=0.25" -F "file=@inputs/images/sample1.jpg"
curl.exe -f -X POST "http://127.0.0.1:8000/detect/video?conf=0.25" -F "file=@inputs/videos/sample_video.mp4"
```

Postman: select POST, enter either URL, select Body > form-data, add a key named
`file` with type File, choose your image/video, then Send. Let Postman set the
multipart Content-Type including its boundary.

## Behavior and architecture

- `app/main.py` loads YOLO once during FastAPI lifespan startup and stores it in
  application state. Every request reuses it. Each Uvicorn worker has its own model;
  start with one worker to avoid duplicating model memory.
- Synchronous routes run in FastAPI's thread pool. A lock serializes calls to the
  shared YOLO predictor. Video processing is synchronous from the client's perspective;
  long videos may require longer client/proxy timeouts.
- `app/services/` owns image/video inference, annotation, severity rules, and JSON/CSV
  reporting. The CLI delegates to these services too.
- Each upload gets a unique directory under `outputs/api`. Original uploads are
  removed after processing; failed jobs are removed. Successful artifacts persist
  until you remove them. Download routes serve only the four allowed artifact names.
- Images produce annotated JPEGs; videos produce MPEG-4 MP4s without audio.
  Download videos for playback in a compatible player; browser codec support varies.
- Video reports merge consecutive occupied seconds by violation class, preserving
  the prior aggregation behavior. These events are not unique people or tracked incidents.
  Frame timestamps start at zero. Empty reports still include correct CSV headers.
- Upload limit: 100 MiB. Unsupported extensions return 415; empty/undecodable media
  return 400; missing files/invalid confidence return 422; oversized files return 413.
  The size check happens while copying the parsed upload, so use a reverse-proxy
  body limit if deploying beyond localhost. This local API has no authentication.
- Set `PPEGUARD_MODEL` or `PPEGUARD_OUTPUTS` before startup to override defaults.
  Missing model weights fail startup rather than failing on the first upload.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
$env:PPEGUARD_REAL_MODEL_TEST = "1"
.\.venv\Scripts\python.exe -m pytest -q tests/test_api.py
```

Default API tests exercise multipart uploads, downloadable/decodable media, reports,
validation, unique jobs, and one startup load using a lightweight detector stub.
The opt-in test uses `models/best.pt`, a sample image, and a generated three-frame video.

The CLI remains available:

```powershell
.\.venv\Scripts\python.exe scripts/detect.py --image inputs/images/sample1.jpg
.\.venv\Scripts\python.exe scripts/detect.py --video inputs/videos/sample_video.mp4
```

CLI results now use unique folders under `outputs/cli` to avoid overwriting prior runs.
