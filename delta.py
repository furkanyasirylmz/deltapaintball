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

if "drink_prices" not in st.session_state:
    st.session_state.drink_prices = {}

if "payments" not in st.session_state:
    st.session_state.payments = {}

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

            for p in players:
                st.session_state.payments[p] = {
                    "deposit": 0,
                    "cash": 0,
                    "iban": 0
                }

            st.session_state.page = 2
            st.rerun()

# -------------------
# 2. SAYFA (YATAY TABLO YENİ HAL)
# -------------------
elif st.session_state.page == 2:
    st.title("🎮 Oyun Takibi")

    # HEADER
    header_cols = st.columns([2, 2, 6])
    header_cols[0].markdown("### Oyuncu")
    header_cols[1].markdown("### Boya")
    header_cols[2].markdown("### İçecekler")

    st.divider()

    for player in st.session_state.players:

        row = st.container()
        c1, c2, c3 = row.columns([2, 2, 6])

        # -------------------
        # PLAYER NAME
        # -------------------
        c1.markdown(f"### {player}")

        # -------------------
        # PAINT
        # -------------------
        b1, b2, b3 = c2.columns([1, 1, 2])

        if b1.button("➕", key=f"paint_plus_{player}"):
            st.session_state.data[player]["paint"] += 1
            st.rerun()

        if b2.button("➖", key=f"paint_minus_{player}"):
            if st.session_state.data[player]["paint"] > 0:
                st.session_state.data[player]["paint"] -= 1
                st.rerun()

        b3.markdown(f"🎯 **{st.session_state.data[player]['paint']}**")

        # -------------------
        # DRINKS GRID
        # -------------------
        drinks = list(st.session_state.drink_prices.keys())
        drink_grid = c3.columns(3)

        for j, d in enumerate(drinks):
            cc1, cc2 = drink_grid[j % 3].columns([1, 1])

            if cc1.button(f"+ {d}", key=f"{player}_{d}_plus"):
                st.session_state.data[player]["drinks"][d] += 1
                st.rerun()

            if cc2.button(f"- {d}", key=f"{player}_{d}_minus"):
                if st.session_state.data[player]["drinks"][d] > 0:
                    st.session_state.data[player]["drinks"][d] -= 1
                    st.rerun()

            drink_grid[j % 3].markdown(
                f"**{d}: {st.session_state.data[player]['drinks'][d]}**"
            )

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

    for player in st.session_state.players:
        data = st.session_state.data[player]

        paint_total = data["paint"] * paint_price
        drink_total = sum(data["drinks"][d] * drink_prices[d] for d in drink_prices)

        total = entry_fee + paint_total + drink_total
        grand_total += total

        st.subheader(player)
        st.write(f"Giriş: {entry_fee} TL")
        st.write(f"Boya Topu: {data['paint']} x {paint_price} TL")
        st.write(f"İçecekler: {drink_total} TL")
        st.write(f"Toplam: **{total} TL**")

        st.divider()

        summary_list.append({"İsim": player, "Toplam Ücret": total})

    st.markdown(f"## 🧾 GENEL TOPLAM: {grand_total} TL")

    st.dataframe(pd.DataFrame(summary_list), use_container_width=True)

    if st.button("➡️ ÖDEME EKRANINA GEÇ"):
        st.session_state.page = 4
        st.rerun()

# -------------------
# 4. SAYFA
# -------------------
elif st.session_state.page == 4:
    st.title("💳 Ödeme & Depozito")

    entry_fee = st.session_state.entry_fee
    paint_price = st.session_state.paint_price
    drink_prices = st.session_state.drink_prices

    st.subheader("➕ Depozito Girişi")

    col_d1, col_d2, col_d3 = st.columns([2,2,1])

    selected_player = col_d1.selectbox("Oyuncu", st.session_state.players)
    deposit_amount = col_d2.number_input("Tutar", min_value=0)

    if col_d3.button("Ekle"):
        st.session_state.payments[selected_player]["deposit"] += deposit_amount
        st.rerun()

    st.divider()
    st.subheader("📊 Ödeme Tablosu")

    excel_rows = []

    total_borc = 0
    total_deposit = 0
    total_cash = 0
    total_iban = 0

    for player in st.session_state.players:
        data = st.session_state.data[player]
        pay = st.session_state.payments[player]

        paint_total = data["paint"] * paint_price
        drink_total = sum(data["drinks"][d] * drink_prices[d] for d in drink_prices)

        borc = entry_fee + paint_total + drink_total

        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

        col1.write(f"**{player}**")
        col2.write(borc)
        col3.write(pay["deposit"])

        pay["cash"] = col4.number_input("Nakit", value=pay["cash"], key=f"cash_{player}")
        pay["iban"] = col5.number_input("IBAN", value=pay["iban"], key=f"iban_{player}")

        total_paid = pay["deposit"] + pay["cash"] + pay["iban"]
        kalan = borc - total_paid

        col6.write(total_paid)

        if kalan > 0:
            col7.markdown(f"🔴 {kalan}")
        elif kalan == 0:
            col7.markdown(f"🟢 {kalan}")
        else:
            col7.markdown(f"🟡 {kalan}")

        total_borc += borc
        total_deposit += pay["deposit"]
        total_cash += pay["cash"]
        total_iban += pay["iban"]

        excel_rows.append({
            "İsim": player,
            "Borç": borc,
            "Depozito": pay["deposit"],
            "Nakit": pay["cash"],
            "IBAN": pay["iban"],
            "Toplam Ödeme": total_paid,
            "Kalan": kalan
        })

    st.divider()
    st.markdown(f"**Toplam Borç:** {total_borc}")
    st.markdown(f"**Toplam Depozito:** {total_deposit}")
    st.markdown(f"**Nakit Toplam:** {total_cash}")
    st.markdown(f"**IBAN Toplam:** {total_iban}")

    df_excel = pd.DataFrame(excel_rows)

    total_row = pd.DataFrame([{
        "İsim": "GENEL TOPLAM",
        "Borç": total_borc,
        "Depozito": total_deposit,
        "Nakit": total_cash,
        "IBAN": total_iban,
        "Toplam Ödeme": total_deposit + total_cash + total_iban,
        "Kalan": total_borc - (total_deposit + total_cash + total_iban)
    }])

    df_excel = pd.concat([df_excel, total_row], ignore_index=True)

    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Rapor')
        return output.getvalue()

    excel_file = to_excel(df_excel)

    st.download_button(
        "📥 Excel İndir",
        excel_file,
        "odeme_rapor.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("🔄 YENİ GRUP"):
        st.session_state.clear()
        st.rerun()
