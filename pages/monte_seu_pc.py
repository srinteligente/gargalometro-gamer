import streamlit as st
import json
import os
import urllib.request
import urllib.parse

st.set_page_config(
    page_title="Monte seu PC Gamer - Gargalômetro",
    page_icon="🎯",
    layout="wide"
)

def carregar_vitrine():
    arq = "vitrine.json" if os.path.exists("vitrine.json") else "links.json"
    if os.path.exists(arq):
        try:
            with open(arq, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

VITRINE = carregar_vitrine()

st.title("🎯 Monte seu PC Gamer no GARGALÔMETRO")
st.caption("Escolha a sua faixa de investimento e veja a configuração recomendada equilibrada (Zero Gargalo)!")

# ⬅️ BOTÃO PARA VOLTAR
st.page_link(
    "app.py", 
    label="⬅️ Voltar para a Calculadora de Gargalo do Setup", 
    icon="🖥️", 
    use_container_width=True
)
st.divider()

faixas = [
    "🥉 R$ 2.000 a R$ 2.800 (Entrada / Competitivos Leves)",
    "🥈 R$ 3.000 a R$ 4.200 (Custo-Benefício 1080p Alto)",
    "🥇 R$ 4.500 a R$ 6.500 (Alta Performance 1080p/1440p)",
    "👑 Acima de R$ 7.000 (Top de Linha / Quad HD e 4K)"
]

orcamento_escolhido = st.radio("Selecione sua faixa de investimento:", faixas, horizontal=True)

st.divider()

if "2.000 a R$ 2.800" in orcamento_escolhido:
    st.subheader("🥉 Setup Entrada Inteligente (Gráficos Integrados com Upgrades Futuros)")
    st.markdown("""
    - **Processador:** AMD Ryzen 5 5600GT ou 4600G (6 núcleos / 12 threads com Vega 7)
    - **Placa-Mãe:** MSI A520M-A PRO (AM4)
    - **Memória:** 16 GB DDR4 (2x8GB) 3200MHz em Dual Channel
    - **Armazenamento:** SSD 512GB NVMe M.2
    - **Fonte:** 500W a 550W 80 Plus (com folga para adicionar GPU depois)
    - **Gabinete:** Gabinete padrão Mesh ou Aquário com ventoinhas
    """)
    st.info("💡 **Objetivo:** Roda jogos como Valorant, CS2, Fortnite e GTA V com excelente fluidez sem precisar de placa dedicada agora.")

elif "3.000 a R$ 4.200" in orcamento_escolhido:
    st.subheader("🥈 Setup Custo-Benefício Ouro (Full HD com Alta Taxa de Quadros)")
    st.markdown("""
    - **Processador:** AMD Ryzen 5 5500 ou Ryzen 5 5600
    - **Placa de Vídeo:** Radeon RX 6600 8GB ou RX 7600 8GB
    - **Placa-Mãe:** MSI A520M ou B550M
    - **Memória:** 16 GB ou 32 GB DDR4 3200MHz
    - **Armazenamento:** SSD 1 TB NVMe M.2
    - **Fonte:** 600W 80 Plus Bronze
    """)
    st.success("🎯 **Objetivo:** A configuração mais equilibrada do mercado nacional. Roda qualquer jogo atual em 1080p na qualidade alta.")

elif "4.500 a R$ 6.500" in orcamento_escolhido:
    st.subheader("🥇 Setup Alta Performance (Pronto para 1440p e Lançamentos Pesados)")
    st.markdown("""
    - **Processador:** Ryzen 5 5500X3D / Ryzen 7 5700X ou entrada AM5 (Ryzen 5 7600)
    - **Placa de Vídeo:** RTX 4060, RTX 5060 ou RX 9060 XT
    - **Placa-Mãe:** B550M AM4 ou B650M AM5
    - **Memória:** 32 GB (2x16GB) DDR4 3200MHz ou DDR5 6000MHz
    - **Armazenamento:** 1 TB ou 2 TB SSD NVMe Gen4
    - **Fonte:** 650W a 750W 80 Plus Gold
    """)
    st.success("🚀 **Objetivo:** Preparado para rodar GTA VI, Warzone e títulos com Ray Tracing e DLSS/FSR com alta estabilidade de 1% low.")

else:
    st.subheader("👑 Setup Entusiasta / Topo de Linha (Sem Limites em 1440p e 4K)")
    st.markdown("""
    - **Processador:** AMD Ryzen 7 7800X3D / 9800X3D (Rei Absoluto dos Games)
    - **Placa de Vídeo:** RTX 4070 Ti SUPER, RTX 5070 Ti, RTX 5080 ou RX 9070 XT
    - **Placa-Mãe:** B650 / X870 AM5 com dissipação reforçada
    - **Memória:** 32 GB ou 64 GB DDR5 6000MHz CL30
    - **Armazenamento:** 2 TB+ SSD NVMe Gen4 de alta velocidade
    - **Refrigeração:** Water Cooler 240mm ou 360mm ARGB
    - **Fonte:** 850W a 1000W 80 Plus Gold / Platinum
    """)
    st.balloons()

st.divider()

achados = VITRINE.get("achados_do_dia", [])
if achados:
    st.markdown("#### ⚡ Peças com Menor Preço Histórico para Adicionar ao Setup:")
    cols = st.columns(len(achados))
    for idx, item in enumerate(achados):
        with cols[idx]:
            with st.container(border=True):
                st.markdown(f"**{item.get('titulo', '')}**")
                st.caption(item.get('descricao', ''))
                st.link_button(item.get('texto_botao', 'Ver Oferta'), item.get('url', '#'), use_container_width=True)

st.divider()
st.subheader("🛠️ Quer que a gente monte a lista exata para você?")
with st.container(border=True):
    col_txt, col_form = st.columns([1, 1.2])
    with col_txt:
        st.markdown("### Consultoria VIP de Montagem")
        st.write("Não quer correr risco de incompatibilidade ou pagar mais caro? Montamos seu carrinho com os melhores cupons ativos do dia.")
        st.markdown("#### **Apenas R$ 20,00**")
        st.caption("Chame a gente preenchendo o formulário ao lado.")
    
    with col_form:
        with st.form("form_montagem_pc", clear_on_submit=True):
            nome = st.text_input("Seu Nome:")
            zap = st.text_input("Seu WhatsApp (com DDD):", placeholder="(61) 99999-9999")
            valor = st.text_input("Valor máximo que pretende investir (R$):", placeholder="Ex: R$ 4.000,00")
            jogos = st.text_area("Quais jogos você pretende jogar?", placeholder="Ex: GTA VI, FiveM, Fortnite, Warzone...")
            
            if st.form_submit_button("🚀 Enviar Pedido de Montagem (R$ 20,00)", use_container_width=True):
                if not zap.strip() or not valor.strip():
                    st.warning("Informe pelo menos WhatsApp e orçamento.")
                else:
                    url_endpoint = "https://formsubmit.co/ajax/dwdistrito@gmail.com"
                    dados = {
                        "Servico": "Monte seu PC Gamer - Consultoria (R$ 20,00)",
                        "Nome": nome if nome.strip() else "Nao informado",
                        "WhatsApp": zap,
                        "Orcamento": valor,
                        "Jogos": jogos if jogos.strip() else "Geral",
                        "_subject": f"🔥 Pedido de Montagem de PC: {zap} (R$ {valor})"
                    }
                    try:
                        data = urllib.parse.urlencode(dados).encode("utf-8")
                        req = urllib.request.Request(url_endpoint, data=data, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
                        with urllib.request.urlopen(req, timeout=10) as resp:
                            if resp.status == 200:
                                st.success("✅ Pedido recebido! Entraremos em contato via WhatsApp.")
                    except Exception:
                        st.error("Erro temporário ao enviar. Tente novamente.")
