import streamlit as st
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Orville's Freight Density & Class Calculator",
    page_icon="🚚",
    layout="wide",
)

st.title("Orville's Freight Density & Class Calculator")
st.caption(
    "This is a simple tool to calculate freight density and class based on pallet details."
)
st.divider()

# --- STATE INITIALIZATION ---
if "rows" not in st.session_state:
    st.session_state.rows = 3
if "reset_trigger" not in st.session_state:
    st.session_state.reset_trigger = False


# --- BUTTON FUNCTIONS ---
def add_row():
    st.session_state.rows += 1


def reset_form():
    st.session_state.rows = 3
    st.session_state.reset_trigger = True


def calculate_density_and_class(pallets):
    CUBIC_INCHES_PER_CUBIC_FOOT = 1728
    total_weight = 0
    total_volume = 0
    for p in pallets:
        qty, wt, l, w, h = p.values()
        if all(x > 0 for x in [qty, wt, l, w, h]):
            volume = (l * w * h * qty) / CUBIC_INCHES_PER_CUBIC_FOOT
            total_weight += wt * qty
            total_volume += volume
    if total_volume == 0:
        return 0, 0, 0, 0
    density = total_weight / total_volume
    # Class mapping
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


# --- INPUT FIELDS ---
st.subheader("📦 Pallet Details")

pallets = []
for i in range(st.session_state.rows):
    c1, c2, c3, c4, c5 = st.columns(5)
    qty = c1.number_input(
        "Pallets",
        min_value=0,
        step=1,
        key=f"qty_{i}",
        value=0 if st.session_state.reset_trigger else None,
    )
    wt = c2.number_input(
        "Weight (lbs)",
        min_value=0.0,
        step=0.1,
        key=f"wt_{i}",
        value=0.0 if st.session_state.reset_trigger else None,
    )
    l = c3.number_input(
        "Length (in)",
        min_value=0.0,
        step=0.1,
        key=f"l_{i}",
        value=0.0 if st.session_state.reset_trigger else None,
    )
    w = c4.number_input(
        "Width (in)",
        min_value=0.0,
        step=0.1,
        key=f"w_{i}",
        value=0.0 if st.session_state.reset_trigger else None,
    )
    h = c5.number_input(
        "Height (in)",
        min_value=0.0,
        step=0.1,
        key=f"h_{i}",
        value=0.0 if st.session_state.reset_trigger else None,
    )
    pallets.append(
        {
            "Pallets": qty,
            "Weight (lbs)": wt,
            "Length (in)": l,
            "Width (in)": w,
            "Height (in)": h,
        }
    )

st.session_state.reset_trigger = False

st.divider()

# --- ACTION BUTTONS (aligned together) ---
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.button("➕ Add Row", on_click=add_row, use_container_width=True)
with col2:
    st.button("🧮 Calculate", key="calc", use_container_width=True)
with col3:
    st.button("🔄 Reset", on_click=reset_form, use_container_width=True)

# --- CALCULATE RESULT ---
if st.session_state.get("calc", False):
    tw, tv, d, fc = calculate_density_and_class(pallets)
    if tv == 0:
        st.warning("Please fill in at least one complete row.")
    else:
        st.success("✅ Calculation Complete")
        a, b, c, dcol = st.columns(4)
        a.metric("Total Weight (lbs)", f"{tw:.2f}")
        b.metric("Total Cubic Feet", f"{tv:.2f}")
        c.metric("Density (lbs/ft³)", f"{d:.2f}")
        dcol.metric("Freight Class", f"Class {fc}")
        st.info(
            f"Freight Class **{fc}** is based on total density of **{d:.2f} lbs/ft³**."
        )

st.caption("Developed for MetroShoe Warehouse • by OrvilleDev 🧠")
