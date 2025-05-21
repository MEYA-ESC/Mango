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
upload = st.sidebar.file_uploader("Upload Mango Image", type=["jpg","jpeg","png"])
cam = st.sidebar.camera_input("Or take a photo")
zoom_pct = st.sidebar.slider("Crop zoom (%)", 10, 50, 40)

# Pick source
image_source = upload if upload is not None else cam

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
    w,h = img.size
    z = zoom/100
    crop = img.crop((w*z, h*z, w*(1-z), h*(1-z)))
    arr = np.array(crop)
    avg = arr.mean(axis=(0,1))
    avg_py = [int(round(x)) for x in avg]

    # RGB->HSV for hue
    rn,gn,bn = [c/255 for c in avg_py]
    h_norm,_,_ = colorsys.rgb_to_hsv(rn,gn,bn)
    hue_deg = h_norm*360
    ripeness = classify_ripeness_by_hue(hue_deg)
    return crop, avg_py, hue_deg, ripeness

st.title("🥭 Mango Ripeness Detector")

# Process new image
if image_source:
    img = Image.open(image_source).convert("RGB")
    cropped, avg_color, hue, ripeness = analyze_image(img, zoom_pct)

    c1, c2 = st.columns([2,1])
    with c1:
        st.image(cropped, caption="Cropped Mango", use_container_width=True)
    with c2:
        st.subheader("🍃 Results")
        st.markdown(f"**Average RGB:** {tuple(avg_color)}")
        st.markdown(f"**Hue:** {hue:.1f}°")
        st.markdown(f"### Predicted: {ripeness}")
        sw = np.ones((100,100,3),dtype=np.uint8)*np.array(avg_color,dtype=np.uint8)
        st.image(sw, caption="Color Swatch", use_container_width=True)

    # append to log
    st.session_state.log.append({
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Avg_R": avg_color[0],
        "Avg_G": avg_color[1],
        "Avg_B": avg_color[2],
        "Hue": round(hue,1),
        "Ripeness": ripeness
    })

# Show and edit log as a table
if st.session_state.log:
    st.markdown("---")
    st.subheader("📑 Results Log (editable)")
    df = pd.DataFrame(st.session_state.log)

    edited_df = st.experimental_data_editor(
        df,
        num_rows="dynamic",           # allow add/delete
        use_container_width=True
    )

    # If the user added/deleted rows, update our session state
    if not edited_df.equals(df):
        st.session_state.log = edited_df.to_dict("records")
        st.experimental_rerun()

    # Download button
    csv = edited_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download log as CSV", csv, "mango_log.csv", "text/csv")

else:
    st.info("Please upload or snap a mango image from the sidebar.")
