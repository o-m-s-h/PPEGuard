"""HTTP-only connection to PPEGuard; no model or backend imports."""
import os

import requests

API_URL = os.getenv("PPEGUARD_API_URL", "http://127.0.0.1:8000").rstrip("/")


def run_detection(upload, media_type):
    with requests.Session() as session:
        response = session.post(
            f"{API_URL}/detect/{media_type}",
            files={"file": (upload.name, upload.getvalue(), upload.type or "application/octet-stream")},
            timeout=(10, 1800),
        )
        if not response.ok:
            try:
                detail = response.json().get("detail", "Detection failed.")
            except ValueError:
                detail = "Detection failed. Please try again."
            raise ValueError(str(detail))
        result = response.json()
        # Use the configured backend host, including when it runs behind a proxy.
        job_id = result["job_id"]
        if len(job_id) != 32 or any(c not in "0123456789abcdef" for c in job_id):
            raise ValueError("The service returned an invalid result identifier.")
        extension = "jpg" if media_type == "image" else "mp4"
        artifacts = {}
        for key, filename in {
            "annotated": f"annotated.{extension}",
            "json": "report.json",
            "csv": "report.csv",
        }.items():
            download = session.get(f"{API_URL}/files/{job_id}/{filename}", timeout=(10, 300))
            download.raise_for_status()
            artifacts[key] = download.content
        return {"media_type": media_type, "report": result["report"], "artifacts": artifacts}
