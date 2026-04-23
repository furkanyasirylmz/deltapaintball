import streamlit as st

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
    entry_fee = st.number_input("Giriş Ücreti", min_value=0, step=10)
    paint_price = st.number_input("1 Şarjör Fiyatı", min_value=0, step=10)

    if st.button("Devam Et"):
        players = [n.strip() for n in names_input.split("\n") if n.strip()]

        if len(players) < 4 or len(players) > 20:
            st.error("Oyuncu sayısı 4 ile 20 arasında olmalı.")
        else:
            st.session_state.players = players
            st.session_state.entry_fee = entry_fee
            st.session_state.paint_price = paint_price

            for p in players:
                st.session_state.data[p] = {
                    "paint": 0,
                    "drinks": {
                        "Su": 0,
                        "Kahve": 0,
                        "Redbull": 0,
                        "Kutu İçecek": 0
                    }
                }

            st.session_state.page = 2
            st.rerun()

# -------------------
# 2. SAYFA (GELİŞTİRİLDİ)
# -------------------
elif st.session_state.page == 2:
    st.title("🎮 Oyun Takibi")

    for i, player in enumerate(st.session_state.players):

        with st.container():
            col1, col2, col3 = st.columns([2,2,4])

            # İSİM
            col1.markdown(f"### {player}")

            # BOYA TOPU
            with col2:
                if st.button("➕ Boya Topu", key=f"paint_{player}"):
                    st.session_state.data[player]["paint"] += 1

                st.markdown(
                    f"🎯 **{st.session_state.data[player]['paint']}**",
                )

            # İÇECEKLER
            with col3:
                drinks = ["Su", "Kahve", "Redbull", "Kutu İçecek"]

                drink_cols = st.columns(4)

                for j, d in enumerate(drinks):
                    if drink_cols[j].button(
                        f"{d} ({st.session_state.data[player]['drinks'][d]})",
                        key=f"{player}_{d}"
                    ):
                        st.session_state.data[player]["drinks"][d] += 1

        # AYIRICI ÇİZGİ
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

    for player in st.session_state.players:
        data = st.session_state.data[player]
        total = entry_fee + (data["paint"] * paint_price)

        st.subheader(player)
        st.write(f"Giriş Ücreti: {entry_fee} TL")
        st.write(f"Boya Topu: {data['paint']} x {paint_price} TL")
        st.write(f"Toplam: **{total} TL**")

        st.write("İçecekler:")
        for d, count in data["drinks"].items():
            if count > 0:
                st.write(f"- {d}: {count} adet")

        st.divider()

    if st.button("🔄 YENİ GRUP"):
        st.session_state.clear()
        st.rerun()
