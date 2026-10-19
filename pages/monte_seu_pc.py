import streamlit as st
import json
import os
import re

st.set_page_config(
    page_title="Monte seu PC Gamer - Assistente Passo a Passo",
    page_icon="🛠️",
    layout="wide"
)

# Ocultar o menu nativo lateral do Streamlit para manter a interface limpa
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        .stSelectbox label {
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# Função para carregar a vitrine
@st.cache_data
def carregar_vitrine():
    for arq in ["vitrine.json", "vitrine_2.json", "links.json"]:
        if os.path.exists(arq):
            try:
                with open(arq, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return {}

vitrine = carregar_vitrine()

# Botão para voltar à calculadora principal
st.page_link("app.py", label="⬅️ Voltar para a Calculadora de Gargalo (Gargalômetro)", icon="🖥️")
st.divider()

st.title("🛠️ Monte seu PC Gamer Passo a Passo")
st.caption("Selecione os componentes compatíveis, confira os preços promocionais com cupom e garanta a sua montagem sem erros!")

if not vitrine:
    st.error("⚠️ Não foi possível carregar a base de dados de peças (`vitrine.json`). Verifique se o arquivo está na raiz.")
    st.stop()

# Helpers para extrair itens das categorias
def extrair_opcoes(categoria_dict):
    """Transforma dicionário de abas em lista plana de tuplas (Texto, URL, Aba/Categoria)"""
    opcoes = [("Selecione uma opção...", "", "")]
    if not isinstance(categoria_dict, dict):
        return opcoes
    for subcat, dados in categoria_dict.items():
        itens = dados.get("itens", []) if isinstance(dados, dict) else dados
        for it in itens:
            opcoes.append((f"[{subcat}] {it['texto']}", it["url"], subcat))
    return opcoes

# Seleção de Plataforma Base
st.markdown("### 1️⃣ Escolha a Plataforma do Processador")
plataforma = st.radio(
    "Qual arquitetura deseja montar?",
    ["🔴 AMD AM4 (DDR4 - Máximo Custo-Benefício)", "🟣 AMD AM5 (DDR5 - Nova Geração & Longevidade)", "🔵 Intel LGA 1700 (DDR4 / DDR5)"],
    horizontal=True
)

eh_am4 = "AM4" in plataforma
eh_am5 = "AM5" in plataforma
eh_intel = "Intel" in plataforma

# Filtrar Processadores e Placas-Mãe compatíveis
chave_cpu = "🔴 AMD AM4 (DDR4)" if eh_am4 else ("🟣 AMD AM5 (DDR5 - Nova Geração)" if eh_am5 else "🔵 Intel LGA 1700")
chave_mb = "🔴 AMD AM4 (DDR4)" if eh_am4 else ("🟣 AMD AM5 (DDR5)" if eh_am5 else "🔵 Intel LGA 1700 (DDR4 / DDR5)")

cpus_disp = vitrine.get("cpus", {}).get(chave_cpu, {}).get("itens", [])
mbs_disp = vitrine.get("placas_mae", {}).get(chave_mb, {}).get("itens", [])

c_cpu, c_mb = st.columns(2)

with c_cpu:
    st.markdown("#### ⚡ Processador (CPU)")
    opcoes_cpu = ["Selecione o processador..."] + [c["texto"] for c in cpus_disp]
    sel_cpu = st.selectbox("Processadores Compatíveis:", opcoes_cpu)
    cpu_item = next((c for c in cpus_disp if c["texto"] == sel_cpu), None)
    if cpu_item:
        st.link_button(f"🛒 Ver Oferta CPU: {cpu_item['texto'][:40]}...", cpu_item["url"], use_container_width=True)

with c_mb:
    st.markdown("#### 🧩 Placa-Mãe (Motherboard)")
    opcoes_mb = ["Selecione a placa-mãe..."] + [m["texto"] for m in mbs_disp]
    sel_mb = st.selectbox("Placas-Mãe Compatíveis:", opcoes_mb)
    mb_item = next((m for m in mbs_disp if m["texto"] == sel_mb), None)
    if mb_item:
        st.link_button(f"🛒 Ver Oferta Placa-Mãe: {mb_item['texto'][:40]}...", mb_item["url"], use_container_width=True)

st.divider()

# Placa de Vídeo e Memória RAM
st.markdown("### 2️⃣ Placa de Vídeo e Memória RAM")
c_gpu, c_ram = st.columns(2)

# Coletar GPUs
opcoes_gpu = extrair_opcoes(vitrine.get("gpus", {}))
with c_gpu:
    st.markdown("#### 🎮 Placa de Vídeo (GPU)")
    sel_gpu_txt = st.selectbox("Selecione a Placa de Vídeo:", [op[0] for op in opcoes_gpu])
    gpu_item = next((op for op in opcoes_gpu if op[0] == sel_gpu_txt and op[1]), None)
    if gpu_item:
        st.link_button(f"🛒 Comprar Placa de Vídeo", gpu_item[1], use_container_width=True)

# Coletar RAM
opcoes_ram = extrair_opcoes(vitrine.get("memorias_ram", {}))
with c_ram:
    st.markdown("#### ⚡ Memória RAM")
    if eh_am4:
        st.info("💡 Para AM4, utilize kits DDR4 (ex: Kit CUSU 2x8GB 3200MHz dos Achados do Dia).")
    sel_ram_txt = st.selectbox("Selecione os Módulos de RAM:", [op[0] for op in opcoes_ram])
    ram_item = next((op for op in opcoes_ram if op[0] == sel_ram_txt and op[1]), None)
    if ram_item:
        st.link_button(f"🛒 Comprar Memória RAM", ram_item[1], use_container_width=True)

st.divider()

# Armazenamento e Arrefecimento
st.markdown("### 3️⃣ Armazenamento & Refrigeração")
c_arm, c_cooler = st.columns(2)

opcoes_arm = extrair_opcoes(vitrine.get("armazenamento", {}))
with c_arm:
    st.markdown("#### 💾 Armazenamento (NVMe / SATA)")
    sel_arm_txt = st.selectbox("Selecione o SSD / Armazenamento:", [op[0] for op in opcoes_arm])
    arm_item = next((op for op in opcoes_arm if op[0] == sel_arm_txt and op[1]), None)
    if arm_item:
        st.link_button(f"🛒 Comprar Armazenamento", arm_item[1], use_container_width=True)

opcoes_cooler = extrair_opcoes(vitrine.get("coolers", {}))
with c_cooler:
    st.markdown("#### ❄️ Cooler (Air Cooler ou Water Cooler LCD)")
    sel_cooler_txt = st.selectbox("Selecione a Refrigeração:", [op[0] for op in opcoes_cooler])
    cooler_item = next((op for op in opcoes_cooler if op[0] == sel_cooler_txt and op[1]), None)
    if cooler_item:
        st.link_button(f"🛒 Comprar Cooler", cooler_item[1], use_container_width=True)

st.divider()

# Fonte de Alimentação e Gabinete
st.markdown("### 4️⃣ Alimentação & Gabinete")
c_fonte, c_gab = st.columns(2)

opcoes_fonte = extrair_opcoes(vitrine.get("fontes", {}))
with c_fonte:
    st.markdown("#### 🔌 Fonte de Alimentação (500W a 1250W)")
    sel_fonte_txt = st.selectbox("Selecione a Fonte de Alimentação:", [op[0] for op in opcoes_fonte])
    fonte_item = next((op for op in opcoes_fonte if op[0] == sel_fonte_txt and op[1]), None)
    if fonte_item:
        st.link_button(f"🛒 Comprar Fonte", fonte_item[1], use_container_width=True)

opcoes_gab = extrair_opcoes(vitrine.get("gabinetes", {}))
with c_gab:
    st.markdown("#### 📦 Gabinete Gamer")
    sel_gab_txt = st.selectbox("Selecione o Gabinete:", [op[0] for op in opcoes_gab])
    gab_item = next((op for op in opcoes_gab if op[0] == sel_gab_txt and op[1]), None)
    if gab_item:
        st.link_button(f"🛒 Comprar Gabinete", gab_item[1], use_container_width=True)

st.divider()

# Resumo Final da Máquina
st.markdown("### 📋 Resumo da Sua Máquina Selecionada")
with st.container(border=True):
    itens_selecionados = [
        ("Processador (CPU)", cpu_item["texto"] if cpu_item else None, cpu_item["url"] if cpu_item else None),
        ("Placa-Mãe", mb_item["texto"] if mb_item else None, mb_item["url"] if mb_item else None),
        ("Placa de Vídeo (GPU)", gpu_item[0] if gpu_item else None, gpu_item[1] if gpu_item else None),
        ("Memória RAM", ram_item[0] if ram_item else None, ram_item[1] if ram_item else None),
        ("Armazenamento", arm_item[0] if arm_item else None, arm_item[1] if arm_item else None),
        ("Refrigeração", cooler_item[0] if cooler_item else None, cooler_item[1] if cooler_item else None),
        ("Fonte", fonte_item[0] if fonte_item else None, fonte_item[1] if fonte_item else None),
        ("Gabinete", gab_item[0] if gab_item else None, gab_item[1] if gab_item else None),
    ]

    total_escolhidos = sum(1 for it in itens_selecionados if it[1] is not None)
    
    if total_escolhidos == 0:
        st.info("👆 Selecione as peças acima para ver o resumo completo com todos os links de compra.")
    else:
        for cat, nome, link in itens_selecionados:
            if nome and link:
                c_lbl, c_btn = st.columns([3, 1])
                with c_lbl:
                    st.write(f"• **{cat}:** {nome}")
                with c_btn:
                    st.link_button("Ir para Loja 🔗", link, use_container_width=True)
            else:
                st.write(f"• **{cat}:** *(Pendente de escolha)*")
