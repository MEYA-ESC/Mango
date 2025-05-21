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

# Initialize a session‐state list to hold results
if "log" not in st.session_state:
    st.session_state.log = []

# Sidebar controls
st.sidebar.title("📋 Settings")
uploaded_file = st.sidebar.file_uploader("Upload Mango Image", type=["jpg", "jpeg", "png"])
zoom_pct = st.sidebar.slider("Crop zoom (%)", min_value=10, max_value=50, value=40)

# Ripeness classification thresholds
def classify_ripeness_by_hue(hue):
    if 80 <= hue < 180:
        return "Unripe"
    elif 60 <= hue < 80:
        return "Partially Ripe"
    elif 40 <= hue < 60:
        return "Ripe"
    elif 0 <= hue < 40 or hue >= 330:
        return "Overripe"
    else:
        return "Can't detect"

# Analyze image
def analyze_image(img, zoom):
    w, h = img.size
    z = zoom / 100.0
    left = int(w * z); top = int(h * z)
    right = int(w * (1 - z)); bottom = int(h * (1 - z))
    cropped = img.crop((left, top, right, bottom))

    arr = np.array(cropped)
    avg = arr.mean(axis=(0, 1))
    avg_py = [int(round(x)) for x in avg]

    # RGB → HSV hue
    rn, gn, bn = [c/255.0 for c in avg_py]
    h_norm, s, v = colorsys.rgb_to_hsv(rn, gn, bn)
    hue_deg = h_norm * 360

    ripeness = classify_ripeness_by_hue(hue_deg)
    return cropped, avg_py, hue_deg, ripeness

# App title
st.title("🥭 Mango Ripeness Detector")

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    cropped_img, avg_color, hue, ripeness = analyze_image(img, zoom_pct)

    # Columns
    col1, col2 = st.columns([2, 1])
    with col1:
        st.image(cropped_img, caption="Cropped Mango", use_container_width=True)
    with col2:
        st.subheader("🍃 Results")
        st.markdown(f"**Average RGB:** {tuple(avg_color)}")
        st.markdown(f"**Hue:** {hue:.1f}°")
        st.markdown(f"### Predicted: {ripeness}")

        st.markdown("**Color Swatch**")
        swatch = np.ones((100, 100, 3), dtype=np.uint8) * np.array(avg_color, dtype=np.uint8)
        st.image(swatch, use_container_width=True)

    # Log this result with a timestamp
    st.session_state.log.append({
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Filename": uploaded_file.name,
        "Avg_R": avg_color[0],
        "Avg_G": avg_color[1],
        "Avg_B": avg_color[2],
        "Hue": round(hue,1),
        "Ripeness": ripeness
    })

# Show Results Log if any
if st.session_state.log:
    st.markdown("---")
    st.subheader("📑 Results Log")
    df = pd.DataFrame(st.session_state.log)
    st.dataframe(df, use_container_width=True)

    # Download button
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download log as CSV",
        data=csv,
        file_name="mango_ripeness_log.csv",
        mime="text/csv"
    )
else:
    st.info("Please upload a mango image from the sidebar to get started.")
