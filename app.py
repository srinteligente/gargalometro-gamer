import streamlit as st
import json
import os
import re

nome_icone = None
for arq in [
    "gargalo_detectado_ampliado.webp",
    "gargalo detectado.webp",
    "gargalo_detectado.webp"
]:
    if os.path.exists(arq):
        nome_icone = arq
        break

st.set_page_config(
    page_title="Gargalômetro Gamer",
    page_icon=nome_icone if nome_icone else "🖥️",
    layout="wide"
)

# Carrega bancos de dados
def carregar_dados():
    dados_hw = {"gpus": [], "cpus": []}
    if os.path.exists("banco_hardware_completo.json"):
        with open("banco_hardware_completo.json", "r", encoding="utf-8") as f:
            dados_hw = json.load(f)
    
    dados_links = {}
    if os.path.exists("links.json"):
        try:
            with open("links.json", "r", encoding="utf-8") as f:
                dados_links = json.load(f)
        except Exception as e:
            st.error(f"Erro ao ler links.json: {e}")
            
    return dados_hw, dados_links

db, LINKS = carregar_dados()
st.sidebar.caption(f"🔗 Links Ativos: {len(LINKS)}")

def classificar_plataforma_cpu(nome_cpu):
    u = nome_cpu.upper()
    
    if any(x in u for x in ["XEON", "FX-", "PHENOM", "ATHLON", "CORE2", "OPTERON", "SEMPRON", "A10-", "A8-", "A6-", "A4-"]):
        return "DEFASADA"
    
    m_intel_5d = re.search(r'I[3579]-(\d{2})\d{3}', u)
    if m_intel_5d:
        gen = int(m_intel_5d.group(1))
        if gen in [10, 11]:
            return "DEFASADA"
        elif 12 <= gen <= 14:
            return "LGA1700"

    if re.search(r'I[3579]-(\d)\d{3}', u) or re.search(r'I[3579]-\d{3}\b', u):
        return "DEFASADA"

    if "RYZEN" in u:
        m_ryzen = re.search(r'RYZEN\s+[3579]\s+(\d{4})', u)
        if m_ryzen:
            num = int(m_ryzen.group(1))
            if 1000 <= num < 6000:
                return "AM4"
            elif num >= 7000:
                return "AM5"
        if any(f" {g}" in u for g in ["5500", "5600", "5700", "5800", "5900", "5950", "3600", "2600", "1600"]):
            return "AM4"
        if any(f" {g}" in u for g in ["7500", "7600", "7700", "7800", "7900", "7950", "8400", "8500", "8600", "8700", "9600", "9700", "9800", "9900", "9950"]):
            return "AM5"

    return "OUTRA"

def detectar_video_integrado(cpu_obj):
    nome = cpu_obj["nome"]
    u = nome.upper()
    
    gpu_int = cpu_obj.get("gpu_integrada", "")
    if gpu_int and "Requer placa de vídeo" in gpu_int:
        return False, 0.0, "Requer placa de vídeo dedicada (sem gráficos integrados)."
    
    if "XEON" in u:
        return False, 0.0, "Intel Xeon não possui vídeo integrado."
    if bool(re.search(r'\d{4,5}F\b', u)) or bool(re.search(r'\d{4,5}KF\b', u)):
        return False, 0.0, "Processadores Intel série 'F' / 'KF' não possuem vídeo integrado."
    if "7500F" in u or "9500F" in u or "9700F" in u or "5500F" in u or "8400F" in u or "8700F" in u:
        return False, 0.0, f"O {nome} não possui vídeo integrado."
        
    if "RYZEN" in u:
        eh_zen4_ou_novo = any(gen in u for gen in ["7600", "7700", "7800", "7900", "7950", "8500", "8600", "8700", "9600", "9700", "9800", "9900", "9950"])
        eh_mobile = cpu_obj.get("notebook", False) or any(u.endswith(m) or (m + " ") in u for m in ["U", "H", "HS", "HX", "C"])
        eh_g = any(g in u for g in ["G", "GE"])
        
        if not (eh_zen4_ou_novo or eh_mobile or eh_g):
            return False, 0.0, "Processadores Ryzen desktop das séries 1000 a 5000 sem o sufixo 'G' não possuem vídeo integrado."
            
        if "8065S" in gpu_int or "495" in u:
            return True, 6.0, "Radeon 8065S (40 CUs - Nível de GPU potente)"
        if "8050S" in gpu_int or "490" in u or "485" in u:
            return True, 5.4, "Radeon 8050S (32 CUs - Desempenho gráfico elevado)"
        if "890M" in gpu_int or "475" in u or "470" in u:
            return True, 5.0, "Radeon 890M (16 CUs - Excelente para competitivos e leves)"
        if "780M" in gpu_int or "8700G" in u or "260" in u or "250" in u or "180" in u:
            return True, 4.8, "Radeon 780M (Roda competitivos e lançamentos em 1080p)"
        if "680M" in gpu_int or "170" in u or "160" in u:
            return True, 4.2, "Radeon 680M (Ótimo desempenho em 1080p para iGPU)"
        if "760M" in gpu_int or "8600G" in u or "230" in u or "165" in u:
            return True, 4.0, "Radeon 760M"
        if "660M" in gpu_int or "150" in u or "130" in u or "110" in u:
            return True, 3.2, "Radeon 660M"
        if "5700G" in u or "5600G" in u or "5600GT" in u:
            return True, 2.9, "Radeon Vega 7 Integrada (Jogos leves: Valorant, CS2, GTA V)"
        if "3400G" in u or "2400G" in u:
            return True, 2.7, "Radeon Vega 11 Integrada"
        if "3200G" in u or "2200G" in u:
            return True, 2.4, "Radeon Vega 8 Integrada"
        if "4600G" in u or "4650G" in u or "4300G" in u:
            return True, 2.7, "Radeon Vega 6/7 Integrada"
        if eh_zen4_ou_novo:
            return True, 2.0, "RDNA 2 Básica Integrada (Apenas vídeo básico)"
        return True, 2.5, "Gráficos Integrados AMD Radeon"

    if "INTEL" in u:
        if any(g in u for g in ["12", "13", "14", "ULTRA"]):
            return True, 2.4, "Intel UHD 770 / Iris Xe Integrada"
        return True, 1.8, "Intel HD / UHD Graphics Básica"
        
    return True, 1.8, "Vídeo Integrado Básico"

# Cabeçalho
header_col1, header_col2 = st.columns([1, 8])
with header_col1:
    if nome_icone:
        st.image(nome_icone, width=90)
with header_col2:
    st.title("Gargalômetro Gamer")
    st.caption(f"Avaliador de Equilíbrio & Ranking (0 a 10) • Base: {len(db['gpus'])} GPUs e {len(db['cpus'])} CPUs")

# ========================================================
# 📢 DESTAQUES DO TOPO (LIVEPIX & TIKTOK)
# ========================================================
banner_col1, banner_col2 = st.columns(2)

with banner_col1:
    with st.container(border=True):
        st.markdown("##### 🎙️ Quer furar a fila na Live?")
        st.caption("Envie a sua dúvida por mensagem de áudio em tempo real na tela da transmissão!")
        st.link_button("⚡ Mandar Mensagem de Voz (LivePix)", "https://livepix.gg/srinteligente", use_container_width=True)

with banner_col2:
    with st.container(border=True):
        st.markdown("##### 📱 Siga o nosso perfil no TikTok!")
        st.caption("Dicas de hardware, análises, testes de desempenho e promoções exclusivas todo dia.")
        st.link_button("🔥 Seguir @srinteligente.shop", "https://www.tiktok.com/@srinteligente.shop", use_container_width=True)

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

st.divider()

col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.subheader("Configuração da Máquina")

    tipo_dispositivo = st.radio(
        "Tipo de Máquina",
        options=["🖥️ Desktop", "💻 Notebook"],
        horizontal=True
    )
    eh_notebook = tipo_dispositivo == "💻 Notebook"

    if eh_notebook:
        gpu_lista = [g["nome"] for g in db["gpus"] if g.get("notebook", False)]
        gpu_opcoes = ["Nenhuma (Gráficos Integrados / APU)"] + gpu_lista
        padrao_gpu_idx = next((i for i, n in enumerate(gpu_opcoes) if "RTX 4080 Mobile" in n or "4080" in n or "4060" in n), 0)
    else:
        gpu_lista = [g["nome"] for g in db["gpus"] if g.get("desktop", True)]
        gpu_opcoes = ["Nenhuma (Gráficos Integrados / APU)"] + gpu_lista
        padrao_gpu_idx = next((i for i, n in enumerate(gpu_opcoes) if "RTX 5060" in n or "RTX 4060" in n), 0)

    gpu_sel = st.selectbox("Placa de Vídeo (GPU)", gpu_opcoes, index=padrao_gpu_idx)

    if eh_notebook:
        cpu_lista = [c["nome"] for c in db["cpus"] if c.get("notebook", False)]
        padrao_cpu_idx = next((i for i, n in enumerate(cpu_lista) if "13700H" in n or "Ryzen 7 170" in n or "7735" in n), 0)
    else:
        cpu_lista = [c["nome"] for c in db["cpus"] if c.get("desktop", True)]
        padrao_cpu_idx = next((i for i, n in enumerate(cpu_lista) if "Ryzen 5 5600" in n and "5600G" not in n), 0)

    cpu_sel = st.selectbox("Processador (CPU)", cpu_lista, index=padrao_cpu_idx)
    cpu_obj = next(c for c in db["cpus"] if c["nome"] == cpu_sel)

    resolucao_sel = st.radio(
        "Resolução Principal de Jogo",
        options=["1080p (Full HD)", "1440p (Quad HD)", "4K (Ultra HD)"],
        horizontal=True
    )

    c1, c2 = st.columns(2)
    with c1:
        ram_opcoes = {
            "2 GB DDR2 (Legado Extremo)": 1.0,
            "4 GB DDR2 (Básico Antigo)": 1.5,
            "4 GB DDR3 (Entrada Básica DDR3)": 2.0,
            "8 GB DDR3 (Obsoleto)": 2.8,
            "16 GB DDR3 (Defasado)": 3.5,
            "8 GB DDR4 (Apertado)": 4.0,
            "16 GB DDR4 (Básico Atual)": 6.5,
            "32 GB DDR4 (Confortável DDR4)": 8.0,
            "48 GB DDR4 (Capacidade Alta DDR4)": 8.3,
            "64 GB DDR4 (Sobra em DDR4)": 8.5,
            "16 GB DDR5 (Entrada Nova Geração)": 7.5,
            "32 GB DDR5 (Padrão Ouro Atual)": 9.5,
            "48 GB DDR5 (Alta Performance 2x24GB)": 9.8,
            "64 GB DDR5 (Topo Absoluto)": 10.0,
            "128 GB+ DDR5 (Workstation)": 10.0
        }
        padrao_ram_idx = list(ram_opcoes.keys()).index("16 GB DDR4 (Básico Atual)")
        ram_sel = st.selectbox("Memória RAM", list(ram_opcoes.keys()), index=padrao_ram_idx)
        ram_nota = ram_opcoes[ram_sel]

    with c2:
        ssd_opcoes = {
            "Apenas HD Mecânico (Penalizado)": 2.0,
            "SSD SATA (240GB - 500GB)": 4.5,
            "512 GB SSD NVMe M.2": 6.0,
            "1 TB SSD NVMe M.2": 7.5,
            "2 TB SSD NVMe Gen4": 9.0,
            "4 TB+ SSD NVMe Gen4 / Gen5 (Topo)": 10.0
        }
        padrao_ssd_idx = list(ssd_opcoes.keys()).index("1 TB SSD NVMe M.2")
        ssd_sel = st.selectbox("Armazenamento Principal", list(ssd_opcoes.keys()), index=padrao_ssd_idx)
        ssd_nota = ssd_opcoes[ssd_sel]

    if not eh_notebook:
        fonte_w = st.slider("Fonte de Alimentação (Watts)", min_value=300, max_value=1600, value=650, step=50)
    else:
        fonte_w = 280

    jogar_gta = st.checkbox("🎮 Pretendo jogar GTA VI nesta máquina", value=True)

usando_igpu = (gpu_sel == "Nenhuma (Gráficos Integrados / APU)")
tem_igpu, nota_igpu, msg_igpu = detectar_video_integrado(cpu_obj)

if usando_igpu:
    if tem_igpu:
        gpu_obj = {"nome": f"Gráficos Integrados ({msg_igpu})", "nota": nota_igpu, "tdp": 15}
    else:
        gpu_obj = {"nome": "SEM VÍDEO (Processador não possui iGPU)", "nota": 0.5, "tdp": 0}
else:
    gpu_obj = next(g for g in db["gpus"] if g["nome"] == gpu_sel)

# ========================================================
# ⚖️ CÁLCULO DE NOTA RECALIBRADO (DESKTOP & NOTEBOOK)
# ========================================================
if eh_notebook:
    nota_calculada = (gpu_obj["nota"] * 0.60) + (cpu_obj["nota"] * 0.30) + (ram_nota * 0.07) + (ssd_nota * 0.03)
    fonte_nota = 9.5
else:
    fonte_nota = min(10.0, (fonte_w / 1200) * 10)
    nota_calculada = (gpu_obj["nota"] * 0.50) + (cpu_obj["nota"] * 0.25) + (ram_nota * 0.15) + (ssd_nota * 0.05) + (fonte_nota * 0.05)

penalidade_hd = 0.5 if "Apenas HD Mecânico" in ssd_sel else 0.0
nota_final = max(1.0, min(10.0, nota_calculada - penalidade_hd))

consumo_estimado = gpu_obj["tdp"] + cpu_obj["tdp"] + (35 if eh_notebook else 75)
fonte_recomendada = consumo_estimado * 1.35

# ========================================================
# 🎯 CÁLCULO DE GARGALO CALIBRADO (PADRÃO DE MERCADO)
# ========================================================
pesos_resolucao = {
    "1080p (Full HD)": 1.00,
    "1440p (Quad HD)": 1.25,
    "4K (Ultra HD)":   1.60
}

eh_xeon = "XEON" in cpu_obj["nome"].upper()
fator_xeon = 1.0
if eh_xeon and resolucao_sel == "1080p (Full HD)" and gpu_obj["nota"] >= 5.0:
    fator_xeon = 0.65

fps_potencial_gpu = gpu_obj["nota"] / pesos_resolucao[resolucao_sel]
fps_potencial_cpu = (cpu_obj["nota"] * fator_xeon) / 1.00

if fps_potencial_gpu > fps_potencial_cpu:
    pct_gargalo = ((fps_potencial_gpu - fps_potencial_cpu) / fps_potencial_gpu) * 100.0
    componente_limitante = "Processador (CPU)"
else:
    pct_gargalo = ((fps_potencial_cpu - fps_potencial_gpu) / fps_potencial_cpu) * 100.0
    componente_limitante = "Placa de Vídeo (GPU)"

pct_gargalo = round(min(100.0, max(0.0, pct_gargalo)), 1)

with col_right:
    st.subheader("Resultado & Diagnóstico")
    
    st.metric(label="Nota Geral do Setup", value=f"{nota_final:.1f} / 10.0")
    st.progress(min(1.0, max(0.0, nota_final / 10.0)))

    st.write(f"• **GPU:** Nota {gpu_obj['nota']:.1f} ({gpu_obj['tdp']}W)")
    st.write(f"• **CPU:** Nota {cpu_obj['nota']:.1f} ({cpu_obj['tdp']}W)")
    st.write(f"• **RAM:** Nota {ram_nota:.1f} ({ram_sel.split(' ')[0]} GB)")
    st.write(f"• **Armazenamento:** Nota {ssd_nota:.1f}")
    if not eh_notebook:
        st.write(f"• **Fonte:** Nota {fonte_nota:.1f} ({fonte_w}W)")
    else:
        st.caption("⚡ Notebook Gamer: gerenciamento de energia e arrefecimento integrado de fábrica.")

    if usando_igpu:
        if not tem_igpu:
            st.error(f"🚨 **SEM VÍDEO!** O processador `{cpu_obj['nome']}` não possui placa gráfica integrada.")
        else:
            st.info(f"🖥️ **Vídeo Integrado Ativo:** {msg_igpu}.")

    if penalidade_hd > 0:
        st.warning("⚠️ **Penalização Aplicada (-0.5):** O uso exclusivo de HD mecânico causará congelamentos em jogos modernos.")

    if "DDR2" in ram_sel:
        st.error("🚨 **Memória DDR2:** Arquitetura obsoleta. Incompatível com jogos modernos.")
    elif "DDR3" in ram_sel:
        st.warning("⚠️ **Memória DDR3:** Plataforma defasada.")

    if not eh_notebook:
        st.markdown("---")
        if fonte_w < consumo_estimado:
            st.error(f"🚨 **Fonte insuficiente:** Consumo estimado é de ~{consumo_estimado}W e a sua fonte tem {fonte_w}W!")
        elif fonte_w < fonte_recomendada:
            st.warning(f"⚠️ **Pouca folga:** Recomendável pelo menos {int(fonte_recomendada)}W.")
        else:
            st.success("✅ **Alimentação segura.**")

    st.markdown("---")
    st.subheader("Análise de Gargalo por Resolução")

    if eh_xeon and resolucao_sel == "1080p (Full HD)" and gpu_obj["nota"] >= 5.0:
        if nome_icone:
            st.image(nome_icone, width=200)
        st.error("🚨 **GARGALO DE XEON EM FULL HD DETECTADO!**")
        st.write(f"**Gargalo estimado de CPU:** `{pct_gargalo}%`")
        st.progress(min(1.0, pct_gargalo / 100.0))
        st.write(f"O seu **{cpu_obj['nome']}** limita a **{gpu_obj['nome']}** em 1080p devido a clock e IPC antigos.")
        
    elif pct_gargalo >= 20.0 and componente_limitante == "Processador (CPU)":
        if nome_icone:
            st.image(nome_icone, width=200)
        st.error(f"🚨 **GARGALO DETECTADO EM {resolucao_sel.upper()}!**")
        st.write(f"**Gargalo estimado de CPU:** `{pct_gargalo}%`")
        st.progress(min(1.0, pct_gargalo / 100.0))
        st.write(f"O seu **{cpu_obj['nome']}** limita expressivamente a **{gpu_obj['nome']}**.")
        
    elif pct_gargalo >= 25.0 and componente_limitante == "Placa de Vídeo (GPU)":
        st.info(f"💡 **Limite Gráfico em {resolucao_sel}:** Gargalo natural de GPU de `{pct_gargalo}%`.")
        st.write("A placa gráfica trabalhará a 99%/100% de uso, o comportamento esperado em jogos pesados.")
        
    else:
        st.success(f"🎯 **Setup Perfeitamente Equilibrado em {resolucao_sel}!**")
        st.write(f"Variação estimada de apenas `{pct_gargalo}%`. O processador e a placa de vídeo trabalham em harmonia.")

    # ========================================================
    # 🌴 TESTE DE PRONTIDÃO: GTA VI (CORRIGIDO)
    # ========================================================
    if jogar_gta:
        st.markdown("---")
        st.subheader("🌴 Teste de Prontidão: GTA VI")
        tem_hd = "Apenas HD Mecânico" in ssd_sel
        gpu_n = gpu_obj["nota"]
        cpu_n = cpu_obj["nota"]
        
        m_ram = re.search(r'(\d+)\s*GB', ram_sel)
        gb_ram = int(m_ram.group(1)) if m_ram else 16

        gpu_nome_u = gpu_obj["nome"].upper()
        gpu_eh_8gb_gddr6 = any(x in gpu_nome_u for x in ["2060 SUPER", "2060S", "6600", "3060", "4060", "7600", "5050", "3070", "4070", "4080", "4090", "5060", "5070", "5080"])
        
        if usando_igpu:
            st.error("❌ **INCOMPATÍVEL COM GTA VI:** Exigirá GPU dedicada com VRAM física.")
        elif tem_hd:
            st.error("❌ **INCOMPATÍVEL COM GTA VI (Armazenamento):** Exige SSD obrigatoriamente.")
        elif gb_ram < 16:
            st.error(f"❌ **MEMÓRIA RAM INSUFICIENTE ({gb_ram} GB):** GTA VI exigirá no mínimo 16 GB.")
        elif (gpu_n < 4.2 and not gpu_eh_8gb_gddr6) or cpu_n < 3.8:
            st.error(f"⚠️ **ABAIXO DO MÍNIMO ESTIMADO:** GPU ({gpu_n:.1f}) / CPU ({cpu_n:.1f}).")
        elif gpu_n >= 7.8 and cpu_n >= 7.0 and gb_ram >= 16:
            st.balloons()
            st.success("👑 **PRONTO PARA O ALTO / ULTRA EM ALTA TAXA DE FPS!** A sua máquina roda com folga.")
        elif (gpu_n >= 5.8 or gpu_eh_8gb_gddr6) and cpu_n >= 5.0 and gb_ram >= 16:
            st.success("✅ **CONFIGURAÇÃO RECOMENDADA ATENDIDA (60 FPS 1080p/1440p).**")
        else:
            st.warning("⚠️ **CONFIGURAÇÃO MÍNIMA ATENDIDA (1080p 30-45+ FPS em qualidade Normal).**")

    # ========================================================
    # 💰 HUB DE UPGRADE POR PLATAFORMA (LÊ LINKS.JSON)
    # ========================================================
    st.markdown("---")
    st.subheader("🛒 Melhores Ofertas de Upgrade")

    plat_atual = classificar_plataforma_cpu(cpu_obj["nome"])
    ram_antiga = ("DDR2" in ram_sel) or ("DDR3" in ram_sel)
    precisa_trocar_plataforma = (plat_atual == "DEFASADA") or ram_antiga

    if precisa_trocar_plataforma:
        st.markdown("##### 🛠️ Migração de Plataforma Recomendada (Kits com Placa-Mãe + CPU + Cooler):")
        st.info(
            f"💡 A sua plataforma atual ({cpu_obj['nome']}) opera com barramentos ou IPC antigos. "
            "A saída inteligente é migrar para um kit novo:"
        )
        k_col1, k_col2 = st.columns(2)
        with k_col1:
            if "kit_5500f_mach1" in LINKS:
                st.link_button("🔥 Kit R5 5500F (PCIe 4.0) + MSI A520M + Cooler MACH1", LINKS["kit_5500f_mach1"], use_container_width=True)
            if "kit_5500f_risemode" in LINKS:
                st.link_button("⚡ Kit R5 5500F (PCIe 4.0) + MSI A520M + Rise Mode G700", LINKS["kit_5500f_risemode"], use_container_width=True)
        with k_col2:
            if "kit_5700x_watercooler" in LINKS:
                st.link_button("👑 Kit R7 5700X + MSI B550M WiFi6E + Water Cooler 240mm", LINKS["kit_5700x_watercooler"], use_container_width=True)

    st.markdown("##### ⚡ Processadores Recomendados por Plataforma:")
    tab_cpu_am4, tab_cpu_am5, tab_cpu_intel = st.tabs(["🔴 AMD AM4 (DDR4)", "🟣 AMD AM5 (DDR5 - Nova Geração)", "🔵 Intel LGA 1700"])

    with tab_cpu_am4:
        st.caption("🏷️ Cupons Mercado Livre: `SITE50`, `OFFHOJE`, `SEMDEMORA`, `VAIBARATO`, `DESCONTOSUPREMO`, `MEUVALEMELI`")
        c1_btn, c2_btn = st.columns(2)
        with c1_btn:
            url_r5_ml = LINKS.get("r5_5500_ml_promo", LINKS.get("r5_5500_ml", "https://meli.la/1AqHwhD"))
            st.link_button("🔥 Ryzen 5 5500 (ML - Promoção R$ 449,00)", url_r5_ml, use_container_width=True)
            if "r5_5500_kabum" in LINKS:
                st.link_button("📦 Ryzen 5 5500 (KaBuM!)", LINKS["r5_5500_kabum"], use_container_width=True)
            if "r5_5500x3d_shopee" in LINKS:
                st.link_button("🏷️ Ryzen 5 5500X3D (Shopee Cupons)", LINKS["r5_5500x3d_shopee"], use_container_width=True)
            if "r7_5700_shopee" in LINKS:
                st.link_button("🏷️ Ryzen 7 5700 (Shopee - Melhores Preços)", LINKS["r7_5700_shopee"], use_container_width=True)
            if "r7_5800xt_kabum" in LINKS:
                st.link_button("🔥 Ryzen 7 5800XT (KaBuM! - Cupom CPUAGORA)", LINKS["r7_5800xt_kabum"], use_container_width=True)
        with c2_btn:
            if "r5_5500_amazon" in LINKS:
                st.link_button("📦 Ryzen 5 5500 (Amazon Prime)", LINKS["r5_5500_amazon"], use_container_width=True)
            if "r5_5600x_amazon" in LINKS:
                st.link_button("⚡ Ryzen 5 5600X (Amazon)", LINKS["r5_5600x_amazon"], use_container_width=True)
            if "r5_5500x3d_ml" in LINKS:
                st.link_button("🔥 Ryzen 5 5500X3D (Mercado Livre)", LINKS["r5_5500x3d_ml"], use_container_width=True)
            if "r7_5700x_kabum" in LINKS:
                st.link_button("💳 Ryzen 7 5700X (KaBuM!)", LINKS["r7_5700x_kabum"], use_container_width=True)
            if "r7_5800x3d_ml" in LINKS:
                st.link_button("👑 Ryzen 7 5800X3D (Mercado Livre)", LINKS["r7_5800x3d_ml"], use_container_width=True)
            if "r7_5800x3d_kabum" in LINKS:
                st.link_button("👑 Ryzen 7 5800X3D (KaBuM! - Cupom CPUAGORA)", LINKS["r7_5800x3d_kabum"], use_container_width=True)

    with tab_cpu_am5:
        st.caption("🚀 Plataforma AMD AM5 com memória DDR5, alto IPC e processadores X3D")
        am5_1, am5_2 = st.columns(2)
        with am5_1:
            if "r5_8400f_ml" in LINKS:
                st.link_button("🔥 Ryzen 5 8400F (ML - Último em Estoque R$ 688,50)", LINKS["r5_8400f_ml"], use_container_width=True)
            if "r5_8500g_kabum" in LINKS:
                st.link_button("📦 Ryzen 5 8500G com Vídeo Integrado (KaBuM!)", LINKS["r5_8500g_kabum"], use_container_width=True)
            if "r5_7600x_kabum" in LINKS:
                st.link_button("⚡ Ryzen 5 7600X (KaBuM!)", LINKS["r5_7600x_kabum"], use_container_width=True)
            if "r5_9600x_kabum" in LINKS:
                st.link_button("🚀 Ryzen 5 9600X Zen 5 (KaBuM!)", LINKS["r5_9600x_kabum"], use_container_width=True)
            if "r7_7700_kabum" in LINKS:
                st.link_button("📦 Ryzen 7 7700 (KaBuM!)", LINKS["r7_7700_kabum"], use_container_width=True)
            if "r7_7800x3d_kabum" in LINKS:
                st.link_button("👑 Ryzen 7 7800X3D (KaBuM! - Rei do FPS)", LINKS["r7_7800x3d_kabum"], use_container_width=True)
            if "r9_9900x_kabum" in LINKS:
                st.link_button("👑 Ryzen 9 9900X Zen 5 (KaBuM!)", LINKS["r9_9900x_kabum"], use_container_width=True)
            if "r9_9950x_kabum" in LINKS:
                st.link_button("👑 Ryzen 9 9950X Topo de Linha (KaBuM!)", LINKS["r9_9950x_kabum"], use_container_width=True)
        with am5_2:
            if "r5_8400f_amazon" in LINKS:
                st.link_button("⚡ Ryzen 5 8400F (Amazon Prime)", LINKS["r5_8400f_amazon"], use_container_width=True)
            if "r5_8600g_kabum" in LINKS:
                st.link_button("📦 Ryzen 5 8600G Radeon 760M (KaBuM!)", LINKS["r5_8600g_kabum"], use_container_width=True)
            if "r5_7600x3d_kabum" in LINKS:
                st.link_button("🎯 Ryzen 5 7600X3D (KaBuM! - Cache 3D Custo-Benefício)", LINKS["r5_7600x3d_kabum"], use_container_width=True)
            if "r7_8700f_kabum" in LINKS:
                st.link_button("⚡ Ryzen 7 8700F 8-Cores (KaBuM!)", LINKS["r7_8700f_kabum"], use_container_width=True)
            if "r7_9700x_kabum" in LINKS:
                st.link_button("🚀 Ryzen 7 9700X Zen 5 (Amazon)", LINKS["r7_9700x_kabum"], use_container_width=True)
            if "r7_9800x3d_kabum" in LINKS:
                st.link_button("👑 Ryzen 7 9800X3D (KaBuM! - O Mais Forte do Mundo)", LINKS["r7_9800x3d_kabum"], use_container_width=True)
            if "r9_9900x3d_kabum" in LINKS:
                st.link_button("👑 Ryzen 9 9900X3D (KaBuM!)", LINKS["r9_9900x3d_kabum"], use_container_width=True)
            if "r9_9950x3d_amazon" in LINKS:
                st.link_button("👑 Ryzen 9 9950X3D (Amazon - Máxima Performance)", LINKS["r9_9950x3d_amazon"], use_container_width=True)

    with tab_cpu_intel:
        st.caption("🏷️ Use o cupom `CPUAGORA` na KaBuM! para desconto nos modelos Intel K/KF")
        i1_btn, i2_btn = st.columns(2)
        with i1_btn:
            if "intel_i5_14600kf_kabum" in LINKS:
                st.link_button("🔵 Intel Core i5-14600KF 5.3GHz (KaBuM! - Cupom CPUAGORA)", LINKS["intel_i5_14600kf_kabum"], use_container_width=True)
        with i2_btn:
            if "intel_i5_14600k_kabum" in LINKS:
                st.link_button("🔵 Intel Core i5-14600K 5.3GHz (KaBuM! - Cupom CPUAGORA)", LINKS["intel_i5_14600k_kabum"], use_container_width=True)

    st.markdown("##### 🧩 Placas-Mãe Recomendadas (AM4, AM5 e LGA 1700):")
    tab_mb_am4, tab_mb_am5, tab_mb_lga = st.tabs(["🔴 AMD AM4 (DDR4)", "🟣 AMD AM5 (DDR5)", "🔵 Intel LGA 1700 (DDR4 / DDR5)"])

    with tab_mb_am4:
        st.caption("🏷️ Use `MELIOFERTAS` no Mercado Livre ou `CHEGOUMSI` na KaBuM!")
        mb4_1, mb4_2 = st.columns(2)
        with mb4_1:
            if "mb_am4_a520_kabum" in LINKS:
                st.link_button("📦 MSI A520M-A PRO (KaBuM!)", LINKS["mb_am4_a520_kabum"], use_container_width=True)
            if "mb_am4_a520_ml" in LINKS:
                st.link_button("🔥 Gigabyte Ultra Durable A520M (Mercado Livre)", LINKS["mb_am4_a520_ml"], use_container_width=True)
            if "mb_am4_b550_msi_kabum" in LINKS:
                st.link_button("💳 MSI B550M Gaming Plus WiFi6E (KaBuM! - Cupom CHEGOUMSI)", LINKS["mb_am4_b550_msi_kabum"], use_container_width=True)
        with mb4_2:
            if "mb_am4_a520_amazon" in LINKS:
                st.link_button("⚡ MSI A520M-A PRO (Amazon Prime)", LINKS["mb_am4_a520_amazon"], use_container_width=True)
            if "mb_am4_b550_aorus_ml" in LINKS:
                st.link_button("🔥 Gigabyte B550M Aorus Elite (ML - Cupom MELIOFERTAS)", LINKS["mb_am4_b550_aorus_ml"], use_container_width=True)
            if "mb_am4_b550_aorus_amazon" in LINKS:
                st.link_button("⚡ Gigabyte B550M Aorus Elite (Amazon)", LINKS["mb_am4_b550_aorus_amazon"], use_container_width=True)

    with tab_mb_am5:
        st.caption("🚀 Plataforma Moderna AM5 com suporte a memória DDR5")
        mb5_1, mb5_2 = st.columns(2)
        with mb5_1:
            if "mb_am5_b840_ml" in LINKS:
                st.link_button("🔥 MSI Pro B840M-B AM5 (ML - R$ 469,20)", LINKS["mb_am5_b840_ml"], use_container_width=True)
            if "mb_am5_b650_ayw_shopee" in LINKS:
                st.link_button("🏷️ Asus B650M-AYW WiFi (Shopee - R$ 762,59)", LINKS["mb_am5_b650_ayw_shopee"], use_container_width=True)
            if "mb_am5_b650_asrock_rs_kabum" in LINKS:
                st.link_button("📦 ASRock B650 Pro RS ATX (KaBuM!)", LINKS["mb_am5_b650_asrock_rs_kabum"], use_container_width=True)
            if "mb_am5_b650_edge_wifi_kabum" in LINKS:
                st.link_button("👑 MSI MPG B650 Edge WIFI (KaBuM!)", LINKS["mb_am5_b650_edge_wifi_kabum"], use_container_width=True)
            if "mb_am5_b850_prime_amazon" in LINKS:
                st.link_button("⚡ ASUS Prime B850-PLUS PCIe 5.0 (Amazon)", LINKS["mb_am5_b850_prime_amazon"], use_container_width=True)
            if "mb_am5_x870_white_kabum" in LINKS:
                st.link_button("👑 ASUS X870 MAX GAMING WiFi7 BRANCA (KaBuM!)", LINKS["mb_am5_x870_white_kabum"], use_container_width=True)
        with mb5_2:
            if "mb_am5_b840_amazon" in LINKS:
                st.link_button("⚡ MSI Pro B840M-B AM5 (Amazon - R$ 478,99)", LINKS["mb_am5_b840_amazon"], use_container_width=True)
            if "mb_am5_b650_ayw_kabum" in LINKS:
                st.link_button("📦 Asus B650M-AYW WiFi (KaBuM!)", LINKS["mb_am5_b650_ayw_kabum"], use_container_width=True)
            if "mb_am5_b850_asrock_rs_kabum" in LINKS:
                st.link_button("📦 ASRock B850M Pro RS AM5 (KaBuM!)", LINKS["mb_am5_b850_asrock_rs_kabum"], use_container_width=True)
            if "mb_am5_b850_pro_a_kabum" in LINKS:
                st.link_button("📦 ASRock B850M Pro-A (KaBuM!)", LINKS["mb_am5_b850_pro_a_kabum"], use_container_width=True)
            if "mb_am5_b850_challenger_white_amazon" in LINKS:
                st.link_button("❄️ ASRock B850M Challenger WiFi BRANCA (Amazon)", LINKS["mb_am5_b850_challenger_white_amazon"], use_container_width=True)
            if "mb_am5_x870_kabum" in LINKS:
                st.link_button("👑 ASUS X870 MAX GAMING WiFi7 (KaBuM!)", LINKS["mb_am5_x870_kabum"], use_container_width=True)

    with tab_mb_lga:
        st.caption("🔵 Placas-mãe para processadores Intel 12ª, 13ª e 14ª Geração")
        mbl_1, mbl_2 = st.columns(2)
        with mbl_1:
            if "mb_lga1700_h610_ml" in LINKS:
                st.link_button("🔥 MSI Pro H610M-A DDR4 (Mercado Livre)", LINKS["mb_lga1700_h610_ml"], use_container_width=True)
            if "mb_lga1700_b760_msi_p_amazon" in LINKS:
                st.link_button("⚡ MSI PRO B760M-P DDR5 (Amazon - R$ 476,90)", LINKS["mb_lga1700_b760_msi_p_amazon"], use_container_width=True)
            if "mb_lga1700_b760_aorus_ml" in LINKS:
                st.link_button("🔥 Gigabyte B760M Aorus Elite DDR5 (Mercado Livre)", LINKS["mb_lga1700_b760_aorus_ml"], use_container_width=True)
        with mbl_2:
            if "mb_lga1700_h610_kabum" in LINKS:
                st.link_button("📦 MSI PRO H610M-S DDR4 II (KaBuM! - R$ 489,99)", LINKS["mb_lga1700_h610_kabum"], use_container_width=True)
            if "mb_lga1700_b760_msi_a_amazon" in LINKS:
                st.link_button("⚡ MSI PRO B760M-A WIFI DDR5 (Amazon)", LINKS["mb_lga1700_b760_msi_a_amazon"], use_container_width=True)

    st.markdown("##### 🎮 Placas de Vídeo Recomendadas para Jogos Modernos:")
    tab_gpu_custo, tab_gpu_inter, tab_gpu_high = st.tabs([
        "⚡ Custo-Benefício (1080p Alto/Ultra)", 
        "🔥 Intermediárias (1440p Quad HD)", 
        "👑 High-End & Entusiasta (4K / Ray Tracing)"
    ])
    
    with tab_gpu_custo:
        st.caption("🎯 **Melhores opções até R$ 2.000:** Ideal para rodar tudo em Full HD com alta taxa de FPS.")
        g1_btn, g2_btn = st.columns(2)
        with g1_btn:
            if "gpu_rx7600_biostar_shopee" in LINKS:
                st.link_button("🏷️ RX 7600 Biostar 8GB (Shopee - PROMO R$ 1.800)", LINKS["gpu_rx7600_biostar_shopee"], use_container_width=True)
            if "gpu_rtx5050_shopee" in LINKS:
                st.link_button("🔥 MSI NVIDIA RTX 5050 (Shopee Cupons)", LINKS["gpu_rtx5050_shopee"], use_container_width=True)
        with g2_btn:
            if "gpu_rx7600_amazon" in LINKS:
                st.link_button("⚡ ASRock RX 7600 Challenger 8GB (Amazon Prime)", LINKS["gpu_rx7600_amazon"], use_container_width=True)
            if "gpu_rtx5060_amazon" in LINKS:
                st.link_button("🎮 MSI RTX 5060 Shadow 2X OC (Amazon)", LINKS["gpu_rtx5060_amazon"], use_container_width=True)

    with tab_gpu_inter:
        st.caption("🚀 **Alta Performance:** Perfeitas para Quad HD (1440p) competitivo e alta fluidez.")
        gi1_btn, gi2_btn = st.columns(2)
        with gi1_btn:
            if "gpu_rtx3070_kabum" in LINKS:
                st.link_button("🔥 Husky Alpha RTX 3070 8GB GDDR6 (KaBuM!)", LINKS["gpu_rtx3070_kabum"], use_container_width=True)
            if "gpu_rtx5060ti_shopee" in LINKS:
                st.link_button("🚀 INNO3D GeForce RTX 5060 Ti (Shopee Cupons)", LINKS["gpu_rtx5060ti_shopee"], use_container_width=True)
            if "gpu_rx9060xt_shopee" in LINKS:
                st.link_button("⚡ PowerColor Radeon RX 9060 XT 8GB (Shopee)", LINKS["gpu_rx9060xt_shopee"], use_container_width=True)
        with gi2_btn:
            if "gpu_rtx5060ti_pny_kabum" in LINKS:
                st.link_button("⚡ PNY GeForce RTX 5060 Ti (KaBuM!)", LINKS["gpu_rtx5060ti_pny_kabum"], use_container_width=True)

    with tab_gpu_high:
        st.caption("🏷️ Cupom na KaBuM!: `SABADACOVGA10` para 10% OFF em modelos elegíveis")
        gh1_btn, gh2_btn = st.columns(2)
        with gh1_btn:
            if "gpu_rtx5070_asus_kabum" in LINKS:
                st.link_button("🔥 ASUS PRIME RTX 5070 OC 12G (KaBuM! - Cupom SABADACOVGA10)", LINKS["gpu_rtx5070_asus_kabum"], use_container_width=True)
            if "gpu_rx9070_asrock_kabum" in LINKS:
                st.link_button("❄️ ASRock Radeon RX 9070 Steel Legend (KaBuM!)", LINKS["gpu_rx9070_asrock_kabum"], use_container_width=True)
            if "gpu_rx9070xt_powercolor_shopee" in LINKS:
                st.link_button("🚀 PowerColor Radeon RX 9070 XT (Shopee)", LINKS["gpu_rx9070xt_powercolor_shopee"], use_container_width=True)
            if "gpu_rtx5070ti_palit_kabum" in LINKS:
                st.link_button("👑 Palit GeForce RTX 5070 Ti 16GB (KaBuM!)", LINKS["gpu_rtx5070ti_palit_kabum"], use_container_width=True)
            if "gpu_rtx5080_palit_ml" in LINKS:
                st.link_button("👑 Palit Infinity 3 RTX 5080 16GB GDDR7 (Mercado Livre)", LINKS["gpu_rtx5080_palit_ml"], use_container_width=True)
        with gh2_btn:
            if "gpu_rtx5070_palit_kabum" in LINKS:
                st.link_button("🔥 Palit RTX 5070 INFINITY 3 (KaBuM! - Cupom SABADACOVGA10)", LINKS["gpu_rtx5070_palit_kabum"], use_container_width=True)
            if "gpu_rx9070xt_asus_kabum" in LINKS:
                st.link_button("🚀 ASUS Prime Radeon RX 9070 XT OC (KaBuM!)", LINKS["gpu_rx9070xt_asus_kabum"], use_container_width=True)
            if "gpu_rtx5070ti_palit_ml" in LINKS:
                st.link_button("👑 Palit RTX 5070 Ti GamingPro-S 16GB (Mercado Livre)", LINKS["gpu_rtx5070ti_palit_ml"], use_container_width=True)
            if "gpu_rtx5080_msi_kabum" in LINKS:
                st.link_button("👑 MSI RTX 5080 Ventus 3X OC 16GB (KaBuM!)", LINKS["gpu_rtx5080_msi_kabum"], use_container_width=True)
