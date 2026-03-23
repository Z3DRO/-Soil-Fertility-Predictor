import streamlit as st
import requests

# ── Page config ────────────────────────────────────────────
st.set_page_config(
    page_title="Soil Fertility Predictor",
    page_icon="🌾",
    layout="centered"
)

# ── Backend URL ────────────────────────────────────────────
# Change this to your Render URL after deployment
API_URL = "https://obscure-lamp-4pgxw6974gxh5rqg-8000.app.github.dev"

# ── Styling ────────────────────────────────────────────────
st.markdown("""
    <style>
    .main { background-color: #f5f5f0; }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        border-radius: 10px;
        padding: 10px 30px;
        width: 100%;
    }
    .result-box {
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        font-size: 22px;
        font-weight: bold;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────
st.title("🌾 Soil Fertility Predictor")
st.markdown("##### Predict soil fertility class based on nutrient values and season")
st.markdown("---")

# ── Season selector ────────────────────────────────────────
st.subheader("🗓️ Select Season")
season = st.selectbox(
    "Indian Agricultural Season",
    ["Kharif", "Rabi", "Zaid"],
    help="Kharif: Jun-Oct | Rabi: Nov-Mar | Zaid: Apr-May"
)

st.markdown("---")

# ── Nutrient inputs ────────────────────────────────────────
st.subheader("🧪 Enter Soil Nutrient Values")

col1, col2, col3 = st.columns(3)

with col1:
    N  = st.number_input("Nitrogen (N)", min_value=0.0, value=140.0, step=1.0, help="kg/ha")
    P  = st.number_input("Phosphorus (P)", min_value=0.0, value=8.5, step=0.1, help="kg/ha")
    K  = st.number_input("Potassium (K)", min_value=0.0, value=480.0, step=1.0, help="kg/ha")
    pH = st.number_input("pH", min_value=0.0, max_value=14.0, value=7.5, step=0.01)

with col2:
    EC = st.number_input("EC (dS/m)", min_value=0.0, value=0.65, step=0.01)
    OC = st.number_input("Organic Carbon (%)", min_value=0.0, value=0.9, step=0.01)
    S  = st.number_input("Sulphur (S)", min_value=0.0, value=15.0, step=0.1, help="kg/ha")
    Zn = st.number_input("Zinc (Zn)", min_value=0.0, value=0.30, step=0.01, help="mg/kg")

with col3:
    Fe = st.number_input("Iron (Fe)", min_value=0.0, value=0.80, step=0.01, help="mg/kg")
    Cu = st.number_input("Copper (Cu)", min_value=0.0, value=1.50, step=0.01, help="mg/kg")
    Mn = st.number_input("Manganese (Mn)", min_value=0.0, value=3.0, step=0.1, help="mg/kg")
    B  = st.number_input("Boron (B)", min_value=0.0, value=1.5, step=0.01, help="mg/kg")

st.markdown("---")

# ── Predict button ─────────────────────────────────────────
if st.button("🔍 Predict Soil Fertility"):
    payload = {
        "N": N, "P": P, "K": K, "pH": pH,
        "EC": EC, "OC": OC, "S": S, "Zn": Zn,
        "Fe": Fe, "Cu": Cu, "Mn": Mn, "B": B,
        "Season": season
    }

    with st.spinner("Analysing soil data..."):
        try:
            response = requests.post(f"{API_URL}/predict", json=payload, timeout=15)
            result = response.json()

            fertility = result["fertility_class"]
            confidence = result["confidence"]
            probs = result["probabilities"]

            # ── Result colour ──────────────────────────────
            color_map = {
                "Less Fertile": "#e74c3c",
                "Fertile": "#f39c12",
                "Highly Fertile": "#27ae60"
            }
            color = color_map.get(fertility, "#333")

            st.markdown(f"""
                <div class="result-box" style="background-color:{color}22; border: 2px solid {color};">
                    <span style="color:{color}">🌱 {fertility}</span><br>
                    <span style="font-size:16px; color:#555;">Confidence: {confidence}%</span>
                </div>
            """, unsafe_allow_html=True)

            # ── Probability breakdown ──────────────────────
            st.markdown("### 📊 Prediction Probabilities")
            for label, prob in probs.items():
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.progress(int(prob))
                with col_b:
                    st.write(f"**{label}**: {prob}%")

            # ── Recommendations ────────────────────────────
            st.markdown("### 💡 Recommendations")
            if fertility == "Less Fertile":
                st.warning("""
                - 🌿 Add organic compost or green manure
                - 💧 Improve irrigation and drainage
                - 🧂 Apply NPK fertilizers based on soil test
                - 🔄 Consider crop rotation with legumes
                """)
            elif fertility == "Fertile":
                st.info("""
                - ✅ Soil is in good condition
                - 🌾 Suitable for most crops this season
                - 📉 Monitor micronutrient levels regularly
                - 🌱 Maintain organic carbon with mulching
                """)
            else:
                st.success("""
                - 🏆 Excellent soil condition!
                - 🚀 Ideal for high-yield crops
                - 🔬 Conduct periodic tests to maintain fertility
                - ♻️ Continue sustainable farming practices
                """)

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Make sure the API is running.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ── Footer ─────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray;'>VUIP111 Major Project | Soil Fertility Trend Prediction Over Seasons</p>",
    unsafe_allow_html=True
)