# mango_app.py
import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import colorsys
from datetime import datetime

# --- Page config & theme CSS omitted for brevity ---

# Initialize log
if "log" not in st.session_state:
    st.session_state.log = []

# --- Sidebar controls ---
st.sidebar.title("📋 Settings")

# 1) Ask whether to use camera or upload
use_camera = st.sidebar.checkbox("📷 Use camera", value=False)

if use_camera:
    image_source = st.sidebar.camera_input("Take a photo")
else:
    image_source = st.sidebar.file_uploader("Upload Mango Image", type=["jpg","jpeg","png"])

zoom_pct = st.sidebar.slider("Crop Zoom (%)", 10, 50, 40)

# ... classification and analyze_image() remain unchanged ...

st.title("🥭 Mango Ripeness Detector")

if image_source:
    # Process exactly as before
    img = Image.open(image_source).convert("RGB")
    cropped, avg_color, hue, ripeness = analyze_image(img, zoom_pct)

    c1, c2 = st.columns([2,1])
    with c1:
        st.image(cropped, caption="Cropped Mango", use_container_width=True)
    with c2:
        st.subheader("🍃 Results")
        st.markdown(f"**Avg RGB:** {tuple(avg_color)}")
        st.markdown(f"**Hue:** {hue:.1f}°")
        st.markdown(f"### Predicted: {ripeness}")
        sw = np.ones((100,100,3),dtype=np.uint8)*np.array(avg_color,dtype=np.uint8)
        st.image(sw, caption="Color Swatch", use_container_width=True)

    # log it
    st.session_state.log.append({
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Avg_R": avg_color[0], "Avg_G": avg_color[1], "Avg_B": avg_color[2],
        "Hue": round(hue,1), "Ripeness": ripeness
    })
else:
    if use_camera:
        st.info("✅ Flip on Use camera then snap a photo above. Uncheck to close camera.")
    else:
        st.info("Please upload a mango image from the sidebar.")

# ... Results Log code unchanged ...
