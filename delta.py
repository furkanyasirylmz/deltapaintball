import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Paintball Takip", layout="wide")

# -------------------
# STATE
# -------------------
if "page" not in st.session_state:
    st.session_state.page = 1

if "players" not in st.session_state:
    st.session_state.players = []

if "data" not in st.session_state:
    st.session_state.data = {}

# -------------------
# 1. SAYFA
# -------------------
if st.session_state.page == 1:
    st.title("🎯 Paintball Giriş")

    names_input = st.text_area("İsimleri alt alta gir (4-20 kişi)")

    st.subheader("Fiyatlar")
    entry_fee = st.number_input("Giriş Ücreti", min_value=0, step=10)
    paint_price = st.number_input("1 Şarjör Fiyatı", min_value=0, step=10)

    st.subheader("İçecek Fiyatları")
    water_price = st.number_input("Su", min_value=0)
    coffee_price = st.number_input("Kahve", min_value=0)
    redbull_price = st.number_input("Redbull", min_value=0)
    soda_price = st.number_input("Soda", min_value=0)
    fruit_soda_price = st.number_input("Meyveli Soda", min_value=0)
    can_price = st.number_input("Kutu İçecek", min_value=0)

    if st.button("Devam Et"):
        players = [n.strip() for n in names_input.split("\n") if n.strip()]

        if len(players) < 4 or len(players) > 20:
            st.error("Oyuncu sayısı 4 ile 20 arasında olmalı.")
        else:
            st.session_state.players = players
            st.session_state.entry_fee = entry_fee
            st.session_state.paint_price = paint_price

            st.session_state.drink_prices = {
                "Su": water_price,
                "Kahve": coffee_price,
                "Redbull": redbull_price,
                "Soda": soda_price,
                "Meyveli Soda": fruit_soda_price,
                "Kutu İçecek": can_price
            }

            for p in players:
                st.session_state.data[p] = {
                    "paint": 0,
                    "drinks": {d: 0 for d in st.session_state.drink_prices}
                }

            st.session_state.page = 2
            st.rerun()

# -------------------
# 2. SAYFA
# -------------------
elif st.session_state.page == 2:
    st.title("🎮 Oyun Takibi")

    for i, player in enumerate(st.session_state.players):

        with st.container():
            col1, col2, col3 = st.columns([2,2,5])

            col1.markdown(f"### {player}")

            if col2.button("➕ Boya Topu", key=f"paint_{player}"):
                st.session_state.data[player]["paint"] += 1
                st.rerun()

            col2.markdown(f"🎯 **{st.session_state.data[player]['paint']}**")

            drinks = list(st.session_state.drink_prices.keys())
            drink_cols = col3.columns(3)

            for j, d in enumerate(drinks):
                if drink_cols[j % 3].button(
                    f"{d} ({st.session_state.data[player]['drinks'][d]})",
                    key=f"{player}_{d}"
                ):
                    st.session_state.data[player]["drinks"][d] += 1
                    st.rerun()

        if i != len(st.session_state.players) - 1:
            st.markdown("---")

    st.divider()

    if st.button("💰 HESAPLA"):
        st.session_state.page = 3
        st.rerun()

# -------------------
# 3. SAYFA
# -------------------
elif st.session_state.page == 3:
    st.title("💰 Hesap Özeti")

    entry_fee = st.session_state.entry_fee
    paint_price = st.session_state.paint_price
    drink_prices = st.session_state.drink_prices

    grand_total = 0
    summary_list = []
    excel_rows = []

    for player in st.session_state.players:
        data = st.session_state.data[player]

        paint_total = data["paint"] * paint_price
        drink_total = sum(data["drinks"][d] * drink_prices[d] for d in drink_prices)

        total = entry_fee + paint_total + drink_total
        grand_total += total

        # UI detay
        st.subheader(player)
        st.write(f"Giriş: {entry_fee} TL")
        st.write(f"Boya Topu: {data['paint']} x {paint_price} TL")
        st.write(f"İçecekler: {drink_total} TL")
        st.write(f"Toplam: **{total} TL**")

        st.divider()

        # Özet tablo için
        summary_list.append({"İsim": player, "Toplam Ücret": total})

        # Excel için
        excel_rows.append({
            "İsim": player,
            "Giriş Ücreti": entry_fee,
            "Boya Topu Ücreti": paint_total,
            "Meşrubat Toplam": drink_total,
            "Toplam Ücret": total
        })

    # GENEL TOPLAM
    st.markdown(f"## 🧾 GENEL TOPLAM: {grand_total} TL")

    # -------------------
    # TABLO (İSİM + TOPLAM)
    # -------------------
    st.subheader("📊 Özet Tablo")
    df_summary = pd.DataFrame(summary_list)
    st.dataframe(df_summary, use_container_width=True)

    # -------------------
    # EXCEL EXPORT
    # -------------------
    df_excel = pd.DataFrame(excel_rows)

    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Rapor')
        return output.getvalue()

    excel_file = to_excel(df_excel)

    st.download_button(
        label="📥 Excel İndir",
        data=excel_file,
        file_name="paintball_rapor.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("🔄 YENİ GRUP"):
        st.session_state.clear()
        st.rerun()
