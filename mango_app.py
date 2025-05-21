# mango_app.py
import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import colorsys
from datetime import datetime

# --- Page config & Mango Theme CSS ---
st.set_page_config(
    page_title="🥭 Mango Ripeness Detector",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* App background: pale mango flesh */
[data-testid="stAppViewContainer"] {
  background-color: #FFF8E1;
}
/* Header bar */
.header {
  display: flex;
  align-items: center;
  padding: 12px 24px;
  background-color: #FFC107;
  border-radius: 8px;
  margin-bottom: 20px;
}
.header img {
  height: 48px;
  margin-right: 12px;
}
.header h1 {
  margin: 0;
  font-size: 2.2rem;
  color: #4E342E;
}
/* Sidebar look */
[data-testid="stSidebar"] {
  background-color: #FFF3E0;
  padding: 16px;
}
.stSidebar .css-1v3fvcr { /* section headers */
  color: #4E342E;
  font-weight: 600;
}
/* Cards around images and tables */
.stImage, .stDataFrame {
  border: 2px solid #FFB300 !important;
  border-radius: 8px !important;
  padding: 8px !important;
  background-color: #FFFFFF !important;
}
</style>

<div class="header">
  <h1>🥭 Mango Ripeness Detector</h1>
</div>

""", unsafe_allow_html=True)


# --- Initialize in‐session log ---
if "log" not in st.session_state:
    st.session_state.log = []


# --- Sidebar controls ---
st.sidebar.title("📋 Settings")
use_camera = st.sidebar.checkbox("Use camera", value=False)

if use_camera:
    image_source = st.sidebar.camera_input("Take a photo")
else:
    image_source = st.sidebar.file_uploader("Upload Image of Mango", type=["jpg","jpeg","png"])

zoom_pct = st.sidebar.slider("Crop Zoom (%)", 10, 50, 40)


# --- Ripeness classification & analysis funcs ---
def classify_ripeness_by_hue(hue):
    if   90 <= hue < 180:   return "Unripe"
    elif 50 <= hue < 90:    return "Partially Ripe"
    elif 40 <= hue < 50:    return "Ripe"
    elif 0 <= hue < 40 or hue >= 330:
        return "Overripe"
    else:
        return "Can't detect"


def analyze_image(img, zoom):
    w, h = img.size
    z = zoom / 100
    crop = img.crop((w*z, h*z, w*(1-z), h*(1-z)))
    arr = np.array(crop)
    avg = arr.mean(axis=(0,1))
    avg_py = [int(round(x)) for x in avg]

    # Convert to HSV for hue
    rn, gn, bn = [c/255 for c in avg_py]
    h_norm, _, _ = colorsys.rgb_to_hsv(rn, gn, bn)
    hue_deg = h_norm * 360
    ripeness = classify_ripeness_by_hue(hue_deg)
    return crop, avg_py, hue_deg, ripeness



# --- Main content ---
if image_source:
    img = Image.open(image_source).convert("RGB")
    cropped, avg_color, hue, ripeness = analyze_image(img, zoom_pct)

    left, right = st.columns([2,1])
    with left:
        st.image(cropped, caption="Cropped Mango", use_container_width=True)
    with right:
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


# --- Results Log with Delete Buttons ---
if st.session_state.log:
    st.markdown("---")
    st.subheader("📑 Results Log")

    df = pd.DataFrame(st.session_state.log)
    cols = df.columns.tolist()

    # Header row
    header_cols = st.columns(len(cols) + 1)
    for i, c in enumerate(cols):
        header_cols[i].markdown(f"**{c}**")
    header_cols[-1].markdown("")

   # Data rows with delete button
    for idx, entry in enumerate(st.session_state.log):
        row_cols = st.columns(len(cols) + 1)
        for i, c in enumerate(cols):
            row_cols[i].write(entry[c])
        if row_cols[-1].button("Delete", key=f"del_{idx}"):
            st.session_state.log.pop(idx)
            st.rerun()

    # CSV download
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download log as CSV", csv, "mango_log.csv", "text/csv")

else:
    if use_camera:
        st.info("Enable 'Use camera' then snap a photo above, or uncheck to close it.")
    else:
        st.info("Please upload a mango image from the sidebar.")
