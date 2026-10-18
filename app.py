# ========================================================
# 🚨 ACHADOS DO DIA / OFERTAS RELÂMPAGO
# ========================================================
st.markdown("#### ⚡ Achados do Dia com Menor Preço Histórico:")
promo_col1, promo_col2 = st.columns(2)

with promo_col1:
    with st.container(border=True):
        st.markdown("##### 🚀 Ryzen 5 5500 por R$ 449,00!")
        st.caption("6 Cores / 12 Threads • Menor preço no Mercado Livre (Queima de Estoque)")
        url_r5 = LINKS.get("r5_5500_ml_promo", "https://meli.la/1AqHwhD")
        st.link_button("🔥 Garantir R5 5500 por R$ 449 (Mercado Livre)", url_r5, use_container_width=True)

with promo_col2:
    with st.container(border=True):
        st.markdown("##### ❄️ Gabinete Aquário por Menos de R$ 180!")
        st.caption("Hayom GB1796 com 4 FANS instaladas e vidro temperado no TikTok Shop")
        url_gab = LINKS.get("gabinete_aquario_hayom_tiktok", "https://vt.tiktok.com/ZS9UmFDYeJYut-WLOg4/")
        st.link_button("🛒 Garantir Gabinete Aquário no TikTok", url_gab, use_container_width=True)
        
