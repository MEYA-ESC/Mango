# mango_app.py
import streamlit as st
import numpy as np
from PIL import Image
import colorsys

# Ripeness classification
def classify_ripeness_by_hue(color_hue):
    if 80 <= color_hue < 180:
        return "Unripe"
    elif 60 <= color_hue < 80:
        return "Partially Ripe"
    elif 40 <= color_hue < 60:
        return "Ripe"
    elif 0 <= color_hue < 40 or 330 <= color_hue < 360:
        return "Overripe"
    else:
        return "Can't detect"

# Process the uploaded image
def analyze_image(uploaded_image):
    img = Image.open(uploaded_image).convert("RGB")

    # Crop center 40%
    width, height = img.size
    zoom = 0.4
    left = int(width * zoom)
    top = int(height * zoom)
    right = int(width * (1 - zoom))
    bottom = int(height * (1 - zoom))
    cropped_img = img.crop((left, top, right, bottom))

    # Get average color
    img_np = np.array(cropped_img)
    avg_color = img_np.mean(axis=(0, 1))
    r, g, b = avg_color

    # Convert to HSL
    r_norm, g_norm, b_norm = r / 255, g / 255, b / 255
    h, s, l = colorsys.rgb_to_hls(r_norm, g_norm, b_norm)
    hue_deg = h * 360

    ripeness = classify_ripeness_by_hue(hue_deg)

    return cropped_img, avg_color.astype(int), hue_deg, ripeness

# Streamlit UI
st.set_page_config(page_title="Mango Ripeness Detector", layout="centered")
st.title("🥭 Mango Ripeness Detector")

uploaded_file = st.file_uploader("Upload a mango image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    cropped_img, avg_color, hue, ripeness = analyze_image(uploaded_file)

    st.image(cropped_img, caption="Cropped Mango (center region)", use_container_width=True)
    st.markdown(f"**Average RGB:** {avg_color}")
    st.markdown(f"**Hue:** {hue:.2f}°")
    st.markdown(f"### 🍃 Predicted Ripeness: `{ripeness}`")

    # Display color swatch
    st.markdown("**Average Color Sample:**")
    swatch = np.ones((100, 100, 3), dtype=np.uint8) * avg_color
    st.image(swatch, width=100)

