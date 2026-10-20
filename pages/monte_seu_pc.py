import streamlit as st
import json
import os
import re

st.set_page_config(
    page_title="Monte seu PC Gamer - Orçamento & Compatibilidade",
    page_icon="🛠️",
    layout="wide"
)

# Ocultar o menu nativo lateral do Streamlit
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# Função para extrair valor numérico do padrão R$ 1.234,56
def extrair_preco(texto):
    if not texto:
        return 0.0
    match = re.search(r'R\$\s*([\d\.]+,\d{2})', texto)
    if match:
        valor_str = match.group(1).replace(".", "").replace(",", ".")
        try:
            return float(valor_str)
        except ValueError:
            return 0.0
    return 0.0

@st.cache_data
def carregar_vitrine():
    # Lê exclusivamente o arquivo oficial vitrine.json
    caminho = "vitrine.json"
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Erro ao ler vitrine.json: {e}")
            return {}
    return {}

vitrine = carregar_vitrine()

# Botão de retorno
st.page_link("app.py", label="⬅️ Voltar para o Gargalômetro", icon="🖥️")
st.divider()

st.title("🛠️ Monte seu PC Gamer com Validação Técnica")
st.caption("Montagem segura com travas automáticas de RAM, VRM da Placa-Mãe, Tamanho de GPU vs Gabinete e Orçamento em tempo real!")

if not vitrine:
    st.error("⚠️ Base de dados (`vitrine.json`) não encontrada na raiz do projeto.")
    st.stop()

def extrair_opcoes(categoria_dict):
    opcoes = [("Selecione uma opção...", "", "")]
    if not isinstance(categoria_dict, dict):
        return opcoes
    for subcat, dados in categoria_dict.items():
        itens = dados.get("itens", []) if isinstance(dados, dict) else dados
        for it in itens:
            opcoes.append((f"[{subcat}] {it['texto']}", it["url"], subcat, it["texto"]))
    return opcoes

# Busca flexível por palavras-chave para evitar incompatibilidade de emojis/espaços
def buscar_itens_por_chave(dicionario, termo):
    for k, v in dicionario.items():
        if termo.upper() in k.upper():
            return v.get("itens", []) if isinstance(v, dict) else v
    return []

# ----------------------------------------------------
# 1. PLATAFORMA & PROCESSADOR / PLACA-MÃE
# ----------------------------------------------------
st.markdown("### 1️⃣ Plataforma e Processador")
plataforma = st.radio(
    "Escolha a arquitetura:",
    [
        "🔴 AMD AM4 (DDR4 - Máximo Custo-Benefício)", 
        "🟣 AMD AM5 (DDR5 - Nova Geração & Longevidade)", 
        "🔵 Intel LGA 1700 (DDR4 / DDR5)",
        "🟡 Kit Xeon Baratíssimo (CPU + Placa Inclusos)"
    ],
    horizontal=True
)

eh_am4 = "AM4" in plataforma
eh_am5 = "AM5" in plataforma
eh_intel = "Intel" in plataforma
eh_xeon = "Xeon" in plataforma

placas_dict = vitrine.get("placas_mae", {})
c_cpu, c_mb = st.columns(2)

if eh_xeon:
    mbs_disp = buscar_itens_por_chave(placas_dict, "XEON")
    
    with c_mb:
        st.markdown("#### 🧩 Kit Combinado (Placa-Mãe + Processador)")
        opcoes_mb = ["Selecione o kit..."] + [m["texto"] for m in mbs_disp]
        sel_mb = st.selectbox("Kits Disponíveis:", opcoes_mb)
        mb_item = next((m for m in mbs_disp if m["texto"] == sel_mb), None)

    is_xeon_d3 = "X79" in (mb_item["texto"] if mb_item else "")
    is_xeon_d4 = "X99" in (mb_item["texto"] if mb_item else "")

    with c_cpu:
        st.markdown("#### ⚡ Processador (CPU)")
        if mb_item:
            st.info("💡 **Processador Incluso:** O processador Xeon já vem instalado neste kit.")
            cpu_item = {"texto": f"Processador Incluso no {mb_item['texto'].split('(')[0].strip()} (R$ 0,00)", "url": ""}
        else:
            st.caption("👈 Escolha primeiro o Kit Xeon ao lado.")
            cpu_item = None
else:
    chave_busca_cpu = "AM4" if eh_am4 else ("AM5" if eh_am5 else "1700")
    cpus_disp = buscar_itens_por_chave(vitrine.get("cpus", {}), chave_busca_cpu)

    with c_cpu:
        st.markdown("#### ⚡ Processador (CPU)")
        opcoes_cpu = ["Selecione o processador..."] + [c["texto"] for c in cpus_disp]
        sel_cpu = st.selectbox("Processadores Disponíveis:", opcoes_cpu)
        cpu_item = next((c for c in cpus_disp if c["texto"] == sel_cpu), None)

    # Detecção de consumo e VRM
    cpu_nome_u = (cpu_item["texto"] if cpu_item else "").upper()
    eh_am4_pesado = eh_am4 and any(x in cpu_nome_u for x in ["5700", "5800", "5900", "5950"])
    eh_am5_pesado = eh_am5 and any(x in cpu_nome_u for x in ["7700", "9700", "7800", "9800", "9900", "9950"])

    chave_busca_mb = "AM4" if eh_am4 else ("AM5" if eh_am5 else "1700")
    mbs_disp = buscar_itens_por_chave(placas_dict, chave_busca_mb)

    # Travas de VRM
    if eh_am4_pesado:
        mbs_disp = [m for m in mbs_disp if "A520" not in m["texto"].upper()]
    elif eh_am5_pesado:
        mbs_disp = [m for m in mbs_disp if "B840" not in m["texto"].upper()]

    with c_mb:
        st.markdown("#### 🧩 Placa-Mãe Compatível")
        if eh_am4_pesado:
            st.warning("⚠️ **Trava de VRM Ativa (AM4):** CPUs Ryzen 7 e Ryzen 9 exigem placa com dissipador de calor no VRM. Placas A520 foram ocultadas; recomendamos B550.")
        elif eh_am5_pesado:
            st.warning("⚠️ **Trava de VRM Ativa (AM5):** CPUs 8-Core, Ryzen 9 e X3D exigem VRM robusto. A placa B840 foi ocultada; recomendamos B650, B850 ou X870.")
        
        opcoes_mb = ["Selecione a placa-mãe..."] + [m["texto"] for m in mbs_disp]
        sel_mb = st.selectbox("Placas-Mãe Recomendadas:", opcoes_mb)
        mb_item = next((m for m in mbs_disp if m["texto"] == sel_mb), None)

st.divider()

# ----------------------------------------------------
# 2. PLACA DE VÍDEO & MEMÓRIA RAM
# ----------------------------------------------------
st.markdown("### 2️⃣ Placa de Vídeo & Memória RAM")
c_gpu, c_ram = st.columns(2)

opcoes_gpu = extrair_opcoes(vitrine.get("gpus", {}))
with c_gpu:
    st.markdown("#### 🎮 Placa de Vídeo (GPU)")
    sel_gpu_txt = st.selectbox("Selecione a Placa de Vídeo:", [op[0] for op in opcoes_gpu])
    gpu_item = next((op for op in opcoes_gpu if op[0] == sel_gpu_txt and op[1]), None)

# Identificação de placas grandes/triplo fan
gpu_txt_u = (gpu_item[3] if gpu_item else "").upper()
eh_gpu_gigante = any(x in gpu_txt_u for x in ["5070 TI", "5080", "9070 XT", "3070", "INFINITY 3", "VENTUS 3X", "STEEL LEGEND", "TRIPLE FAN"])

# Lógica de seleção de memórias
mems_dict = vitrine.get("memorias_ram", {})
itens_ddr3 = buscar_itens_por_chave(mems_dict, "DDR3")
itens_ddr4 = buscar_itens_por_chave(mems_dict, "DDR4")
itens_ddr5 = buscar_itens_por_chave(mems_dict, "DDR5")

if eh_xeon:
    if is_xeon_d3:
        itens_ram_filtrados = itens_ddr3
    elif is_xeon_d4:
        itens_ram_filtrados = itens_ddr4
    else:
        itens_ram_filtrados = itens_ddr3 + itens_ddr4
elif eh_am4:
    itens_ram_filtrados = itens_ddr4
elif eh_am5:
    itens_ram_filtrados = itens_ddr5
else:
    if mb_item and "DDR4" in mb_item["texto"]:
        itens_ram_filtrados = itens_ddr4
    elif mb_item and "DDR5" in mb_item["texto"]:
        itens_ram_filtrados = itens_ddr5
    else:
        itens_ram_filtrados = itens_ddr4 + itens_ddr5

with c_ram:
    st.markdown("#### ⚡ Memória RAM")
    if eh_xeon and is_xeon_d3:
        st.caption("🔒 **Filtro:** Exibindo apenas memórias **DDR3** para o kit Xeon X79.")
    elif eh_xeon and is_xeon_d4:
        st.caption("🔒 **Filtro:** Exibindo apenas memórias **DDR4** para o kit Xeon X99.")
    elif eh_am4:
        st.caption("🔒 **Filtro:** Exibindo apenas memórias **DDR4** para AM4.")
    elif eh_am5:
        st.caption("🔒 **Filtro:** Exibindo apenas memórias **DDR5** para AM5.")

    opcoes_ram = ["Selecione a memória RAM..."] + [r["texto"] for r in itens_ram_filtrados]
    sel_ram_txt = st.selectbox("Módulos Compatíveis:", opcoes_ram)
    ram_item = next((r for r in itens_ram_filtrados if r["texto"] == sel_ram_txt), None)

st.divider()

# ----------------------------------------------------
# 3. ARMAZENAMENTO & REFRIGERAÇÃO
# ----------------------------------------------------
st.markdown("### 3️⃣ Armazenamento & Refrigeração")
c_arm, c_cooler = st.columns(2)

opcoes_arm = extrair_opcoes(vitrine.get("armazenamento", {}))
with c_arm:
    st.markdown("#### 💾 Armazenamento (SATA / NVMe)")
    sel_arm_txt = st.selectbox("Selecione o Disco:", [op[0] for op in opcoes_arm])
    arm_item = next((op for op in opcoes_arm if op[0] == sel_arm_txt and op[1]), None)

opcoes_cooler = extrair_opcoes(vitrine.get("coolers", {}))
with c_cooler:
    st.markdown("#### ❄️ Cooler / Refrigeração")
    sel_cooler_txt = st.selectbox("Selecione o Cooler:", [op[0] for op in opcoes_cooler])
    cooler_item = next((op for op in opcoes_cooler if op[0] == sel_cooler_txt and op[1]), None)

st.divider()

# ----------------------------------------------------
# 4. FONTE & GABINETE
# ----------------------------------------------------
st.markdown("### 4️⃣ Fonte de Alimentação & Gabinete")
c_fonte, c_gab = st.columns(2)

opcoes_fonte = extrair_opcoes(vitrine.get("fontes", {}))
with c_fonte:
    st.markdown("#### 🔌 Fonte de Alimentação")
    sel_fonte_txt = st.selectbox("Selecione a Fonte:", [op[0] for op in opcoes_fonte])
    fonte_item = next((op for op in opcoes_fonte if op[0] == sel_fonte_txt and op[1]), None)

# Identificação se escolheu Water Cooler de 360mm
cooler_nome_u = (cooler_item[3] if cooler_item else "").upper()
eh_wc_360 = "360" in cooler_nome_u

todos_gabinetes = extrair_opcoes(vitrine.get("gabinetes", {}))
gabinetes_filtrados = todos_gabinetes

# Trava 1: Se escolheu WC de 360mm, restringe aos gabinetes compatíveis com radiador 360mm
if eh_wc_360:
    gabinetes_filtrados = [
        g for g in gabinetes_filtrados 
        if "360MM" in g[0].upper() or "360" in g[0].upper() or g[1] == ""
    ]

# Trava 2: Se escolheu GPU longa/triplo fan, restringe gabinetes compactos
if eh_gpu_gigante:
    gabinetes_filtrados = [
        g for g in gabinetes_filtrados 
        if any(m in g[0].upper() for m in ["320MM", "330MM", "360MM", "400MM"]) or g[1] == ""
    ]

with c_gab:
    st.markdown("#### 📦 Gabinete Gamer")
    if eh_wc_360 and eh_gpu_gigante:
        st.warning("⚠️ **Travas Ativas (WC 360mm + GPU Longa):** Exibindo apenas gabinetes compatíveis com radiador de 360mm e placas de vídeo compridas.")
    elif eh_wc_360:
        st.warning("⚠️ **Trava de Water Cooler Ativa:** Gabinetes compactos foram ocultados. Exibindo apenas modelos com suporte a radiadores de 360mm.")
    elif eh_gpu_gigante:
        st.warning("⚠️ **Trava de GPU Ativa:** Gabinetes compactos foram ocultados para assegurar espaço interno suficiente.")

    sel_gab_txt = st.selectbox("Selecione o Gabinete:", [g[0] for g in gabinetes_filtrados])
    gab_item = next((g for g in gabinetes_filtrados if g[0] == sel_gab_txt and g[1]), None)

st.divider()

# ----------------------------------------------------
# 5. RESUMO FINAL & ORÇAMENTO EM TEMPO REAL
# ----------------------------------------------------
st.markdown("### 💰 Orçamento Total & Resumo da Máquina")

itens_finais = [
    ("Processador (CPU)", cpu_item["texto"] if cpu_item else None, cpu_item["url"] if cpu_item else None),
    ("Placa-Mãe", mb_item["texto"] if mb_item else None, mb_item["url"] if mb_item else None),
    ("Placa de Vídeo (GPU)", gpu_item[3] if gpu_item else None, gpu_item[1] if gpu_item else None),
    ("Memória RAM", ram_item["texto"] if ram_item else None, ram_item["url"] if ram_item else None),
    ("Armazenamento", arm_item[3] if arm_item else None, arm_item[1] if arm_item else None),
    ("Refrigeração", cooler_item[3] if cooler_item else None, cooler_item[1] if cooler_item else None),
    ("Fonte", fonte_item[3] if fonte_item else None, fonte_item[1] if fonte_item else None),
    ("Gabinete", gab_item[3] if gab_item else None, gab_item[1] if gab_item else None),
]

valor_total = 0.0
itens_selecionados_count = 0

for cat, nome, link in itens_finais:
    if nome:
        itens_selecionados_count += 1
        valor_total += extrair_preco(nome)

with st.container(border=True):
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.markdown(f"#### 🛒 Componentes Selecionados: `{itens_selecionados_count} / 8`")
    with col_t2:
        st.metric(label="VALOR TOTAL ESTIMADO", value=f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.markdown("---")
    
    if itens_selecionados_count == 0:
        st.info("👆 Selecione as peças nos menus acima para montar o setup e calcular o custo total.")
    else:
        for cat, nome, link in itens_finais:
            if nome:
                preco_item = extrair_preco(nome)
                preco_badge = f"**R$ {preco_item:,.2f}**".replace(",", "X").replace(".", ",").replace("X", ".") if preco_item > 0 else "*(Preço no link)*"
                if cat == "Processador (CPU)" and eh_xeon:
                    preco_badge = "*(Incluso no Kit)*"
                
                c_desc, c_val, c_btn = st.columns([3, 1, 1])
                with c_desc:
                    st.write(f"• **{cat}:** {nome}")
                with c_val:
                    st.write(preco_badge)
                with c_btn:
                    if link:
                        st.link_button("Comprar 🔗", link, use_container_width=True)
                    else:
                        st.write("—")
            else:
                st.write(f"• **{cat}:** *(Pendente de escolha)*")

st.divider()

# ----------------------------------------------------
# 6. PERIFÉRICOS & ACESSÓRIOS (TIKTOK SHOP)
# ----------------------------------------------------
st.markdown("### 🎧 Complete seu Setup com Periféricos Gamer")

with st.container(border=True):
    col_perif_txt, col_perif_btn = st.columns([2.5, 1.2])
    with col_perif_txt:
        st.markdown("#### 🖱️ Mouse, Teclado, Headset, Microfone e Webcam")
        st.write(
            "Já escolheu as peças do seu PC? "
            "Confira na nossa vitrine da **TikTok Shop** as melhores opções de mouses sem fio, teclados mecânicos, headsets e acessórios testados e aprovados nas nossas lives!"
        )
    with col_perif_btn:
        st.write("")
        st.link_button(
            "🔥 Acessar TikTok Shop", 
            "https://vt.tiktok.com/ZS9UXjfYhhqnB-PcwuJ/", 
            use_container_width=True
        )
