# mango_app.py
import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import colorsys
from datetime import datetime
import base64

# --- Helper to load local images as CSS-friendly URLs ---
def local_image_to_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- Page config & custom CSS ---
st.set_page_config(
    page_title="🥭 Mango Ripeness Detector",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Convert your images to base64
bg_b64 = local_image_to_base64("bg.jpg")       # your page background
hdr_b64 = local_image_to_base64("header.png")  # your header logo

# Inject custom CSS
st.markdown(f"""
<style>
/* Page background */
[data-testid="stAppViewContainer"] {{
  background: url("data:image/jpg;base64,{bg_b64}") no-repeat center center fixed;
  background-size: cover;
}}

/* Header bar */
.header {{
  display: flex;
  align-items: center;
  padding: 10px 20px;
  background-color: rgba(255,255,255,0.8);
  border-radius: 8px;
  margin-bottom: 20px;
}}
.header img {{
  height: 50px;
  margin-right: 15px;
}}
.header h1 {{
  font-size: 2rem;
  margin: 0;
}}
</style>
<div class="header">
  <img src="data:image/png;base64,{hdr_b64}" />
  <h1>🥭 Mango Ripeness Detector</h1>
</div>
""", unsafe_allow_html=True)

# --- Initialize log ---
if "log" not in st.session_state:
    st.session_state.log = []

# --- Sidebar controls ---
st.sidebar.title("📋 Settings")
upload = st.sidebar.file_uploader("Upload Mango Image", type=["jpg","jpeg","png"])
cam = st.sidebar.camera_input("Or take a photo")
zoom_pct = st.sidebar.slider("Crop zoom (%)", 10, 50, 40)
image_source = upload if upload is not None else cam

# --- Ripeness classification ---
def classify_ripeness_by_hue(hue):
    if   80 <= hue < 180:   return "Unripe"
    elif 60 <= hue < 80:    return "Partially Ripe"
    elif 40 <= hue < 60:    return "Ripe"
    elif 0 <= hue < 40 or hue >= 330:
        return "Overripe"
    else:
        return "Can't detect"

# --- Analyze image ---
def analyze_image(img, zoom):
    w,h = img.size
    z = zoom/100
    crop = img.crop((w*z, h*z, w*(1-z), h*(1-z)))
    arr = np.array(crop)
    avg = arr.mean(axis=(0,1))
    avg_py = [int(round(x)) for x in avg]

    rn,gn,bn = [c/255 for c in avg_py]
    h_norm,_,_ = colorsys.rgb_to_hsv(rn,gn,bn)
    hue_deg = h_norm*360
    ripeness = classify_ripeness_by_hue(hue_deg)
    return crop, avg_py, hue_deg, ripeness

# --- Main content (after custom header) ---
if image_source:
    img = Image.open(image_source).convert("RGB")
    cropped, avg_color, hue, ripeness = analyze_image(img, zoom_pct)

    col1, col2 = st.columns([2,1])
    with col1:
        st.image(cropped, caption="Cropped Mango", use_container_width=True)
    with col2:
        st.subheader("🍃 Results")
        st.markdown(f"**Average RGB:** {tuple(avg_color)}")
        st.markdown(f"**Hue:** {hue:.1f}°")
        st.markdown(f"### Predicted: {ripeness}")
        swatch = np.ones((100,100,3),dtype=np.uint8)*np.array(avg_color,dtype=np.uint8)
        st.image(swatch, caption="Color Swatch", use_container_width=True)

    # log it
    st.session_state.log.append({
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Avg_R": avg_color[0], "Avg_G": avg_color[1], "Avg_B": avg_color[2],
        "Hue": round(hue,1), "Ripeness": ripeness
    })

# --- Results Log ---
if st.session_state.log:
    st.markdown("---")
    st.subheader("📑 Results Log")
    df = pd.DataFrame(st.session_state.log)
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download log as CSV", csv, "mango_log.csv", "text/csv")
else:
    st.info("Please upload or snap a mango image from the sidebar.")
