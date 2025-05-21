# mango_app.py
import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import colorsys
from datetime import datetime

# --- Page config & theme CSS (omitted for brevity) ---
st.set_page_config(
    page_title="🥭 Mango Ripeness Detector",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize log
if "log" not in st.session_state:
    st.session_state.log = []

# --- Sidebar controls ---
st.sidebar.title("📋 Settings")

use_camera = st.sidebar.checkbox("Use camera", value=False)
if use_camera:
    image_source = st.sidebar.camera_input("Take a photo")
else:
    image_source = st.sidebar.file_uploader("Upload Mango Image", type=["jpg","jpeg","png"])

zoom_pct = st.sidebar.slider("Crop Zoom (%)", 10, 50, 40)

# Ripeness classification
def classify_ripeness_by_hue(hue):
    if   80 <= hue < 180:   return "Unripe"
    elif 60 <= hue < 80:    return "Partially Ripe"
    elif 40 <= hue < 60:    return "Ripe"
    elif 0 <= hue < 40 or hue >= 330:
        return "Overripe"
    else:
        return "Can't detect"

# Analyze image
def analyze_image(img, zoom):
    w, h = img.size
    z = zoom / 100
    crop = img.crop((w*z, h*z, w*(1-z), h*(1-z)))
    arr = np.array(crop)
    avg = arr.mean(axis=(0,1))
    avg_py = [int(round(x)) for x in avg]
    rn, gn, bn = [c/255 for c in avg_py]
    h_norm, _, _ = colorsys.rgb_to_hsv(rn, gn, bn)
    hue_deg = h_norm * 360
    ripeness = classify_ripeness_by_hue(hue_deg)
    return crop, avg_py, hue_deg, ripeness

st.title("🥭 Mango Ripeness Detector")

# Process a new image if provided
if image_source is not None:
    img = Image.open(image_source).convert("RGB")
    cropped, avg_color, hue, ripeness = analyze_image(img, zoom_pct)

    col1, col2 = st.columns([2,1])
    with col1:
        st.image(cropped, caption="Cropped Mango", use_container_width=True)
    with col2:
        st.subheader("🍃 Results")
        st.markdown(f"**Avg RGB:** {tuple(avg_color)}")
        st.markdown(f"**Hue:** {hue:.1f}°")
        st.markdown(f"### Predicted: {ripeness}")
        swatch = np.ones((100,100,3), dtype=np.uint8) * np.array(avg_color, dtype=np.uint8)
        st.image(swatch, caption="Color Swatch", use_container_width=True)

    # Append to log
    st.session_state.log.append({
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Avg_R": avg_color[0],
        "Avg_G": avg_color[1],
        "Avg_B": avg_color[2],
        "Hue": round(hue,1),
        "Ripeness": ripeness
    })

# Show Results Log as a table with Delete buttons
if st.session_state.log:
    st.markdown("---")
    st.subheader("📑 Results Log")

    # Build DataFrame just for header labels
    df = pd.DataFrame(st.session_state.log)
    cols = df.columns.tolist()
    # Show header row
    header_cols = st.columns(len(cols) + 1)
    for i, c in enumerate(cols):
        header_cols[i].write(f"**{c}**")
    header_cols[-1].write("")

    # Show each row with a Delete button
    for idx, entry in enumerate(st.session_state.log):
        row_cols = st.columns(len(cols) + 1)
        for i, c in enumerate(cols):
            row_cols[i].write(entry[c])
        if row_cols[-1].button("Delete", key=f"del_{idx}"):
            st.session_state.log.pop(idx)
            st.experimental_rerun()

    # Download CSV
    csv = pd.DataFrame(st.session_state.log).to_csv(index=False).encode("utf-8")
    st.download_button("Download log as CSV", csv, "mango_log.csv", "text/csv")

else:
    if use_camera:
        st.info("Enable 'Use camera' and snap a photo above, or uncheck to close.")
    else:
        st.info("Please upload a mango image from the sidebar.")
