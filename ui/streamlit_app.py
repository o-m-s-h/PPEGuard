"""Run with: python -m streamlit run ui/streamlit_app.py"""
from pathlib import Path

import requests
import streamlit as st

from api_client import run_detection

st.set_page_config(page_title="PPEGuard", page_icon="🦺", layout="centered")


def clear_result():
    st.session_state.pop("result", None)


st.title("🦺 PPEGuard")
st.write("Check an image or video for missing safety equipment.")

upload = st.file_uploader(
    "Choose an image or video",
    type=["jpg", "jpeg", "png", "bmp", "webp", "mp4", "avi", "mov", "mkv", "webm", "m4v"],
    on_change=clear_result,
    help="Maximum file size: 100 MB. Short videos process faster.",
)

valid = upload is not None and 0 < upload.size <= 100 * 1024 * 1024
if upload is not None:
    if not upload.size:
        st.error("This file is empty. Please choose another file.")
    elif not valid:
        st.error("Please choose a file smaller than 100 MB.")

if st.button("Check safety equipment", type="primary", disabled=not valid):
    clear_result()
    media_type = "image" if Path(upload.name).suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"} else "video"
    try:
        with st.spinner("Checking your file… Videos may take a few minutes."):
            st.session_state.result = run_detection(upload, media_type)
    except requests.Timeout:
        st.error("Processing took too long. Please try a shorter video or a smaller image.")
    except requests.ConnectionError:
        st.error("The detection service is unavailable. Please ask the app operator to start it, then try again.")
    except requests.RequestException:
        st.error("We couldn't retrieve the result. Please try again.")
    except (ValueError, KeyError, TypeError) as exc:
        st.error(str(exc) if isinstance(exc, ValueError) else "The service returned an incomplete result. Please try again.")

result = st.session_state.get("result")
if result:
    st.success("Your result is ready.")
    artifacts = result["artifacts"]
    is_image = result["media_type"] == "image"
    if is_image:
        st.image(artifacts["annotated"], caption="Annotated image", use_container_width=True)
    else:
        st.video(artifacts["annotated"], format="video/mp4")
        st.caption("Annotated video · audio is not included.")

    report = result["report"]
    count = report.get("total_violations", 0) if is_image else report.get("total_violation_events", 0)
    st.metric("Violations detected" if is_image else "Violation events", count)
    if not is_image:
        st.caption("Events group consecutive seconds of the same violation type; they do not count individual people.")

    stem = Path(report.get("input_file", "result")).stem
    columns = st.columns(3)
    for column, label, key, filename, mime in [
        (columns[0], "Download image" if is_image else "Download video", "annotated", f"{stem}_annotated.{'jpg' if is_image else 'mp4'}", "image/jpeg" if is_image else "video/mp4"),
        (columns[1], "Download JSON", "json", f"{stem}_report.json", "application/json"),
        (columns[2], "Download CSV", "csv", f"{stem}_report.csv", "text/csv"),
    ]:
        column.download_button(label, artifacts[key], file_name=filename, mime=mime, on_click="ignore")

    with st.expander("View report"):
        if report.get("violations"):
            st.dataframe(report["violations"], hide_index=True, use_container_width=True)
        else:
            st.write("No safety equipment violations were detected.")
