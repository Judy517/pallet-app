# app.py
import streamlit as st
from pallet_core import plan_min_pallets  

st.set_page_config(page_title="Expected Number of Pallets", layout="wide")
st.title("Expected Number of Pallets（Kozed/Crisup/CandyMaster）")

st.markdown("Please Enter **number of cases（cases）**，then click“Calculate”to get the minimum of pallet and the layer-by-layer arrangement pallet.")

with st.form("orders_form"):
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        n_kozed60 = st.number_input("Kozed60", min_value=0, value=0, step=1)
    with c2:
        n_kozed24 = st.number_input("Kozed24", min_value=0, value=0, step=1)
    with c3:
        n_crisup24 = st.number_input("Crisup24", min_value=0, value=0, step=1)
    with c4:
        n_crisup20 = st.number_input("Crisup20", min_value=0, value=0, step=1)
    with c5:
        n_candy = st.number_input("CandyMaster", min_value=0, value=0, step=1)

    submitted = st.form_submit_button("Calculate for minimum Pallet")

orders = {
    "Kozed60": int(n_kozed60),
    "Kozed24": int(n_kozed24),
    "Crisup24": int(n_crisup24),
    "Crisup20": int(n_crisup20),
    "CandyMaster": int(n_candy),
}

if submitted:
    with st.spinner("Calculating..."):
        total, pallets = plan_min_pallets(orders)

    st.success(f"Minimum **{total}**  Pallet")
    st.caption(f"Orders：{orders}")
    st.divider()

    # 展示逐板明细
    for i, pal in enumerate(pallets, 1):
        with st.expander(f"📦 Pallet {i}  |  loaded {pal['load']}"):
            # 逐层明细
            if pal.get("layer_plan"):
                for row in pal["layer_plan"]:
                    st.write(f"Layer {row['layer']}: **{row['sku']}** × {row['qty']}")
            else:
                st.write("（This pallet is a full template, no layer-by-layer breakdown）")
