import streamlit as st
import pandas as pd
from io import BytesIO
import uuid

st.set_page_config(page_title="Freight Density & Class Calculator", layout="wide")

# -----------------------------
# CSS Styling
# -----------------------------
st.markdown(
    """
<style>
div.stTextInput>div>div>input {
    color: #000000;  /* pure black text */
    font-size: 14px;
    height: 28px;
}
div.stButton>button {
    padding: 0.25em 0.5em;
    font-size: 14px;
}
.header-col {
    font-weight: bold;
    background-color: #f0f0f0;
    padding: 4px;
    text-align: center;
}
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------
# Helper Functions
# -----------------------------
def new_empty_row():
    return {
        "Pallets": "",
        "Weight (lbs)": "",
        "Length (in)": "",
        "Width (in)": "",
        "Height (in)": "",
        "uid": str(uuid.uuid4()),
    }


def calculate_density_and_class(pallets):
    CUBIC_INCHES_PER_CUBIC_FOOT = 1728
    total_weight = 0
    total_volume = 0
    for p in pallets:
        try:
            qty = float(p.get("Pallets") or 0)
            wt = float(p.get("Weight (lbs)") or 0)
            l = float(p.get("Length (in)") or 0)
            w = float(p.get("Width (in)") or 0)
            h = float(p.get("Height (in)") or 0)
        except:
            continue
        if all(x > 0 for x in [qty, wt, l, w, h]):
            total_volume += (l * w * h * qty) / CUBIC_INCHES_PER_CUBIC_FOOT
            total_weight += wt * qty

    if total_volume == 0:
        return 0, 0, 0, 0

    density = total_weight / total_volume
    if density >= 50:
        fc = 50
    elif density >= 35:
        fc = 55
    elif density >= 30:
        fc = 60
    elif density >= 22.5:
        fc = 65
    elif density >= 15:
        fc = 70
    elif density >= 13.5:
        fc = 77.5
    elif density >= 12:
        fc = 85
    elif density >= 10.5:
        fc = 92.5
    elif density >= 9:
        fc = 100
    elif density >= 8:
        fc = 125
    elif density >= 6:
        fc = 150
    elif density >= 4:
        fc = 175
    elif density >= 2:
        fc = 250
    elif density >= 1:
        fc = 300
    else:
        fc = 400

    return total_weight, total_volume, density, fc


# -----------------------------
# Session State Initialization
# -----------------------------
if "pallets" not in st.session_state:
    st.session_state.pallets = [new_empty_row()]
if "calculated_result" not in st.session_state:
    st.session_state.calculated_result = None

# -----------------------------
# Excel Upload
# -----------------------------
st.title("Freight Density & Class Calculator")
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    expected_cols = [
        "Pallets",
        "Weight (lbs)",
        "Length (in)",
        "Width (in)",
        "Height (in)",
    ]
    if all(col in df.columns for col in expected_cols):
        st.session_state.pallets = []
        for idx, r in df[expected_cols].iterrows():
            row = r.to_dict()
            row["uid"] = str(uuid.uuid4())
            st.session_state.pallets.append(row)
        st.success("Excel data loaded successfully!")

# -----------------------------
# Table Headers
# -----------------------------
headers = ["Pallets", "Weight (lbs)", "Length (in)", "Width (in)", "Height (in)", ""]
cols = st.columns(len(headers))
for col, h in zip(cols, headers):
    col.markdown(f"<div class='header-col'>{h}</div>", unsafe_allow_html=True)

# -----------------------------
# Table Rows with Delete Button
# -----------------------------
# Store rows to delete to avoid modifying the list during iteration
rows_to_delete = []

for idx, row in enumerate(st.session_state.pallets):
    uid = row["uid"]
    input_cols = st.columns(len(headers))
    for field, col in zip(headers[:-1], input_cols[:-1]):
        key = f"{field}_{uid}"
        val = row.get(field, "")
        updated = col.text_input("", value=val, key=key)
        st.session_state.pallets[idx][field] = updated

    if input_cols[-1].button("🗑️", key=f"delete_{uid}"):
        rows_to_delete.append(idx)

# Perform deletion outside the loop
for i in sorted(rows_to_delete, reverse=True):
    st.session_state.pallets.pop(i)

# -----------------------------
# Add Row & Calculate Buttons
# -----------------------------
btn_cols = st.columns([1, 1])
with btn_cols[0]:
    if st.button("➕ Add Row", key="add_row_button"):
        st.session_state.pallets.append(new_empty_row())

with btn_cols[1]:
    if st.button("🧮 Calculate", key="calculate_button"):
        total_weight, total_volume, density, fc = calculate_density_and_class(
            st.session_state.pallets
        )
        st.session_state.calculated_result = {
            "total_weight": total_weight,
            "total_volume": total_volume,
            "density": density,
            "freight_class": fc,
        }

# -----------------------------
# Display Results
# -----------------------------
if st.session_state.calculated_result:
    res = st.session_state.calculated_result
    st.markdown(
        f"<p style='font-size:50px; font-weight:bold; margin:0; color:#000000'>Freight Class: {res['freight_class']}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='font-size:30px; font-weight:bold; margin:0; color:#000000'>Total Cubic Feet: {res['total_volume']:.2f}</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='font-size:30px; font-weight:bold; margin:0; color:#000000'>Density (lb/ft³): {res['density']:.2f}</p>",
        unsafe_allow_html=True,
    )

    # Excel Download
    df_out = pd.DataFrame(st.session_state.pallets)
    df_out["Total Weight"] = res["total_weight"]
    df_out["Total Cubic Feet"] = res["total_volume"]
    df_out["Density"] = res["density"]
    df_out["Freight Class"] = res["freight_class"]

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_out.to_excel(writer, index=False)
    st.download_button(
        label="⬇️ Download Excel Result",
        data=buffer.getvalue(),
        file_name="freight_result.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
