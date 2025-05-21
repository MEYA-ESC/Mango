# mango_app.py
import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import colorsys
from datetime import datetime

# Page config
st.set_page_config(
    page_title="🥭 Mango Ripeness Detector",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize log
if "log" not in st.session_state:
    st.session_state.log = []

# Sidebar controls
st.sidebar.title("📋 Settings")
upload = st.sidebar.file_uploader("Upload Mango Image", type=["jpg", "jpeg", "png"])
cam = st.sidebar.camera_input("Or take a photo")
zoom_pct = st.sidebar.slider("Crop zoom (%)", 10, 50, 40)

# Choose source
image_source = upload if upload is not None else cam

# Ripeness classification
def classify_ripeness_by_hue(hue):
    if 80 <= hue < 180:      return "Unripe"
    elif 60 <= hue < 80:     return "Partially Ripe"
    elif 40 <= hue < 60:     return "Ripe"
    elif 0 <= hue < 40 or hue >= 330: return "Overripe"
    else:                    return "Can't detect"

# Analyze image
def analyze_image(img, zoom):
    w, h = img.size
    z = zoom / 100
    crop = img.crop((w*z, h*z, w*(1-z), h*(1-z)))

    arr = np.array(crop)
    avg = arr.mean(axis=(0,1))
    avg_py = [int(round(x)) for x in avg]

    # RGB→HSV
    rn, gn, bn = [c/255 for c in avg_py]
    h_norm, s, v = colorsys.rgb_to_hsv(rn, gn, bn)
    hue_deg = h_norm * 360

    ripeness = classify_ripeness_by_hue(hue_deg)
    return crop, avg_py, hue_deg, ripeness

# App title
st.title("🥭 Mango Ripeness Detector")

if image_source is not None:
    # load via PIL
    img = Image.open(image_source).convert("RGB")
    cropped, avg_color, hue, ripeness = analyze_image(img, zoom_pct)

    # display
    col1, col2 = st.columns([2,1])
    with col1:
        st.image(cropped, caption="Cropped Mango", use_container_width=True)
    with col2:
        st.subheader("🍃 Results")
        st.markdown(f"**Average RGB:** {tuple(avg_color)}")
        st.markdown(f"**Hue:** {hue:.1f}°")
        st.markdown(f"### Predicted: {ripeness}")
        sw = np.ones((100,100,3), dtype=np.uint8)*np.array(avg_color, dtype=np.uint8)
        st.image(sw, caption="Color Swatch", use_container_width=True)

    # log it
    st.session_state.log.append({
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Avg_R": avg_color[0], "Avg_G": avg_color[1], "Avg_B": avg_color[2],
        "Hue": round(hue,1), "Ripeness": ripeness
    })

# show log
if st.session_state.log:
    st.markdown("---")
    st.subheader("📑 Results Log")
    df = pd.DataFrame(st.session_state.log)
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode()
    st.download_button("Download log as CSV", csv, "mango_log.csv", "text/csv")
else:
    st.info("Please upload or snap a mango image from the sidebar.")
