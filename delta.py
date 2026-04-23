import streamlit as st

st.set_page_config(page_title="Paintball Takip", layout="wide")

# Session state başlat
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

    st.subheader("Oyuncu İsimleri")
    names_input = st.text_area("İsimleri alt alta gir (4-20 kişi)")

    st.subheader("Fiyatlar")
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

            # Oyuncu verilerini başlat
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
# 2. SAYFA
# -------------------
elif st.session_state.page == 2:
    st.title("🎮 Oyun Takibi")

    for player in st.session_state.players:
        col1, col2, col3 = st.columns([2,1,3])

        # İsim
        col1.write(f"**{player}**")

        # Boya topu
        if col2.button("➕ Boya Topu", key=f"paint_{player}"):
            st.session_state.data[player]["paint"] += 1

        col2.write(f"🎯 {st.session_state.data[player]['paint']}")

        # İçecekler
        with col3:
            if st.button("🥤 İçecek Ekle", key=f"drink_{player}"):
                st.session_state[f"show_{player}"] = True

            if st.session_state.get(f"show_{player}", False):
                drink_cols = st.columns(4)
                drinks = ["Su", "Kahve", "Redbull", "Kutu İçecek"]

                for i, d in enumerate(drinks):
                    if drink_cols[i].button(d, key=f"{player}_{d}"):
                        st.session_state.data[player]["drinks"][d] += 1

    st.divider()

    if st.button("HESAPLA"):
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

    if st.button("YENİ GRUP"):
        st.session_state.clear()
        st.rerun()