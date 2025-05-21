# mango_app.py
import streamlit as st
import numpy as np
from PIL import Image
import colorsys

# Page config
st.set_page_config(
    page_title="🥭 Mango Ripeness Detector",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    # Crop center region
    w, h = img.size
    z = zoom / 100.0
    left = int(w * z)
    top = int(h * z)
    right = int(w * (1 - z))
    bottom = int(h * (1 - z))
    cropped = img.crop((left, top, right, bottom))

    # Compute avg RGB
    arr = np.array(cropped)
    avg = arr.mean(axis=(0, 1))
    r, g, b = avg

    r_norm, g_norm, b_norm = r/255, g/255, b/255
    h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
    hue_deg = h * 360

    ripeness = classify_ripeness_by_hue(hue_deg)
    return cropped, avg.astype(int), hue_deg, ripeness

st.title("🥭 Mango Ripeness Detector")

if uploaded_file:
    # Open & analyze
    img = Image.open(uploaded_file).convert("RGB")
    cropped_img, avg_color, hue, ripeness = analyze_image(img, zoom_pct)

    # Two responsive columns
    col1, col2 = st.columns([2, 1])

    with col1:
        st.image(cropped_img, caption="Cropped Mango", use_container_width=True)

    with col2:
        st.subheader("🍃 Results")
        st.markdown(f"**Average RGB:** {tuple(avg_color)}")
        st.markdown(f"**Hue:** {hue:.1f}°")
        st.markdown(f"### Predicted: {ripeness}")

        st.markdown("**Color Swatch**")
        swatch = np.ones((100, 100, 3), dtype=np.uint8) * avg_color
        st.image(swatch, use_container_width=True)

else:
    st.info("Please upload a mango image from the sidebar to get started.")
