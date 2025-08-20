# app.py
import streamlit as st
from pallet_core import plan_min_pallets  # 直接用你现有的函数

st.set_page_config(page_title="托盘配载小程序", layout="wide")
st.title("托盘配载小程序（Kozed/Crisup/CandyMaster）")

st.markdown("在下面输入每个产品的 **件数（cases）**，点击“计算”即可得到最少 pallet 数及逐层摆放。")

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

    submitted = st.form_submit_button("计算最省 Pallet")

orders = {
    "Kozed60": int(n_kozed60),
    "Kozed24": int(n_kozed24),
    "Crisup24": int(n_crisup24),
    "Crisup20": int(n_crisup20),
    "CandyMaster": int(n_candy),
}

if submitted:
    with st.spinner("计算中..."):
        total, pallets = plan_min_pallets(orders)

    st.success(f"最少需要 **{total}** 个 Pallet")
    st.caption(f"订单：{orders}")
    st.divider()

    # 展示逐板明细
    for i, pal in enumerate(pallets, 1):
        with st.expander(f"📦 Pallet {i}  |  装载 {pal['load']}"):
            # 逐层明细
            if pal.get("layer_plan"):
                for row in pal["layer_plan"]:
                    st.write(f"Layer {row['layer']}: **{row['sku']}** × {row['qty']}")
            else:
                st.write("（此板为满板模板，无逐层拆分）")
