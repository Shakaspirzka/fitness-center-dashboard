"""
Dashboard interactiv pentru analiza potențialului spațiului fitness
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium import plugins
from streamlit_folium import st_folium
import math
import base64
import os
from calculations import (
    get_scenario_analysis,
    compare_scenarios,
    OCCUPANCY_SCENARIOS,
    SUBSCRIPTION_TYPES,
    DESIRED_MONTHLY_REVENUE,
    LOCATION,
    COMPETITORS,
    CAPACITY_PER_HOUR,
    COMPETITOR_LOCATIONS,
    get_financial_forecast_summary,
    get_financial_forecast_by_space
)
from competitor_analysis import (
    get_competitive_positioning,
    get_competitors_comparison,
    calculate_market_position,
    get_layout_comparison,
    get_recommended_layout,
    simulate_new_redgym_impact,
    calculate_profitability_comparison,
    COMFORT_THRESHOLDS,
    get_all_extended_competitors,
    get_competitors_by_category,
    get_all_competitor_locations,
    get_social_media_summary,
    get_competitor_detailed_info
)

# Configurare pagină
st.set_page_config(
    page_title="💪 Dashboard Analiză Potențial Spațiu Fitness & Recuperare",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funcție helper pentru încărcarea și afișarea imaginilor
def load_image(image_path, max_width=800):
    """
    Încarcă o imagine și o returnează ca base64 pentru afișare în Streamlit
    """
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as img_file:
                img_bytes = img_file.read()
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                return img_b64
        except Exception as e:
            st.warning(f"Nu s-a putut încărca imaginea {image_path}: {e}")
            return None
    return None

def display_image(image_path, caption="", max_width=800):
    """
    Afișează o imagine în Streamlit
    """
    img_b64 = load_image(image_path)
    if img_b64:
        st.markdown(f"""
        <div style="text-align: center; margin: 20px 0;">
            <img src="data:image/png;base64,{img_b64}" style="max-width: {max_width}px; width: 100%; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />
            {f'<p style="margin-top: 10px; color: #666; font-style: italic;">{caption}</p>' if caption else ''}
        </div>
        """, unsafe_allow_html=True)
        return True
    return False

# Funcție helper pentru culori abonamente
def get_subscription_colors():
    """
    Returnează un dicționar cu culori pentru fiecare tip de abonament
    """
    colors = {
        'clase_miscare': '#2ecc71',  # verde
        'fitness_access': '#3498db',  # albastru
        'complet': '#e74c3c',  # roșu
        'family': '#f39c12',  # portocaliu
        'masaj': '#9b59b6',  # mov
        'kineto': '#1abc9c'  # turcoaz
    }
    return {SUBSCRIPTION_TYPES[k]['name']: colors[k] for k in colors if k in SUBSCRIPTION_TYPES}

# Funcție helper pentru cuprins (fără imagine de fundal)
def create_table_of_contents(title, items):
    """
    Creează un cuprins interactiv cu scroll smooth
    
    Args:
        title: Titlul cuprinsului
        items: Lista de tuple-uri (id_anchor, text_link)
    """
    items_html = "\n".join([f'        <li><a href="#{item_id}">{item_text}</a></li>' for item_id, item_text in items])
    
    return f"""
    <style>
    .toc-container-simple {{
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 30px;
        border: 2px solid #e0e0e0;
    }}
    .toc-container-simple h3 {{
        margin-top: 0;
        color: #1f77b4;
        background: rgba(255, 255, 255, 0.9);
        padding: 10px 15px;
        border-radius: 5px;
        display: inline-block;
        font-weight: bold;
    }}
    .toc-container-simple ul {{
        list-style-type: none;
        padding-left: 0;
        background: rgba(255, 255, 255, 0.9);
        padding: 15px;
        border-radius: 5px;
        margin-top: 15px;
    }}
    .toc-container-simple li {{
        margin: 8px 0;
    }}
    .toc-container-simple a {{
        text-decoration: none;
        color: #1f77b4;
        font-weight: 500;
        transition: color 0.2s ease;
    }}
    .toc-container-simple a:hover {{
        color: #0d5a8a;
        text-decoration: underline;
    }}
    html {{
        scroll-behavior: smooth;
    }}
    </style>
    <div class="toc-container-simple">
    <h3>{title}</h3>
    <ul>
{items_html}
    </ul>
    </div>
    <script>
    document.querySelectorAll('.toc-container-simple a').forEach(anchor => {{
        anchor.addEventListener('click', function (e) {{
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {{
                const offset = 80; // Offset pentru header-ul Streamlit
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - offset;
                window.scrollTo({{
                    top: offsetPosition,
                    behavior: 'smooth'
                }});
            }}
        }});
    }});
    </script>
    """

# Stiluri custom
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .scenario-box {
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f8f9fa;
    }
    </style>
""", unsafe_allow_html=True)

# Header
# Header-ul a fost eliminat - se folosește doar imaginea header-ului complet
st.markdown(f"### 📍 Locație: {LOCATION['address']}, {LOCATION['city']}")

# Sidebar - Filtre
st.sidebar.header("⚙️ Parametri Analiză")

# Selectare scenariu
selected_scenario = st.sidebar.selectbox(
    "Scenariu Ocupare",
    options=list(OCCUPANCY_SCENARIOS.keys()),
    format_func=lambda x: OCCUPANCY_SCENARIOS[x]['name'],
    index=1  # Default: Mediu
)

# Distribuție servicii - Mobilis Vita (toate formează 100%)
st.sidebar.subheader("Distribuție Servicii (%)")
st.sidebar.caption("💡 **Notă:** Valorile se normalizează automat la 100%. Serviciile per sesiune ocupă slot-uri ca orice alt serviciu.")

# Toate serviciile formează 100%
clase_miscare_pct = st.sidebar.slider(
    f"{SUBSCRIPTION_TYPES['clase_miscare']['name']} ({SUBSCRIPTION_TYPES['clase_miscare']['price']} RON/lună)",
    0, 100, 50, 5,
    help=SUBSCRIPTION_TYPES['clase_miscare']['description']
)
fitness_access_pct = st.sidebar.slider(
    f"{SUBSCRIPTION_TYPES['fitness_access']['name']} ({SUBSCRIPTION_TYPES['fitness_access']['price']} RON/lună)",
    0, 100, 20, 5,
    help=SUBSCRIPTION_TYPES['fitness_access']['description']
)
complet_pct = st.sidebar.slider(
    f"{SUBSCRIPTION_TYPES['complet']['name']} ({SUBSCRIPTION_TYPES['complet']['price']} RON/lună)",
    0, 100, 15, 5,
    help=SUBSCRIPTION_TYPES['complet']['description']
)
family_pct = st.sidebar.slider(
    f"{SUBSCRIPTION_TYPES['family']['name']} ({SUBSCRIPTION_TYPES['family']['price']} RON/lună)",
    0, 100, 5, 5,
    help=SUBSCRIPTION_TYPES['family']['description']
)
masaj_pct = st.sidebar.slider(
    f"{SUBSCRIPTION_TYPES['masaj']['name']} ({SUBSCRIPTION_TYPES['masaj']['price']} RON/sesiune)",
    0, 100, 5, 5,
    help=f"{SUBSCRIPTION_TYPES['masaj']['description']}. Fiecare sesiune ocupă 1 slot."
)
kineto_pct = st.sidebar.slider(
    f"{SUBSCRIPTION_TYPES['kineto']['name']} ({SUBSCRIPTION_TYPES['kineto']['price']} RON/sesiune)",
    0, 100, 5, 5,
    help=f"{SUBSCRIPTION_TYPES['kineto']['description']}. Fiecare sesiune ocupă 1 slot."
)

# Normalizare distribuție (toate serviciile formează 100%)
total_pct = clase_miscare_pct + fitness_access_pct + complet_pct + family_pct + masaj_pct + kineto_pct
if total_pct == 0:
    clase_miscare_pct, fitness_access_pct, complet_pct, family_pct, masaj_pct, kineto_pct = 50, 20, 15, 5, 5, 5
    total_pct = 100

# Calculează procentajele normalizate
clase_miscare_normalized = (clase_miscare_pct / total_pct) * 100
fitness_access_normalized = (fitness_access_pct / total_pct) * 100
complet_normalized = (complet_pct / total_pct) * 100
family_normalized = (family_pct / total_pct) * 100
masaj_normalized = (masaj_pct / total_pct) * 100
kineto_normalized = (kineto_pct / total_pct) * 100

# Afișează procentajele normalizate
if total_pct != 100:
    st.sidebar.info(f"📊 **Distribuție normalizată:** Clase {clase_miscare_normalized:.1f}% | Fitness {fitness_access_normalized:.1f}% | Complet {complet_normalized:.1f}% | Family {family_normalized:.1f}% | Masaj {masaj_normalized:.1f}% | Kineto {kineto_normalized:.1f}%")
else:
    st.sidebar.success(f"✅ **Distribuție:** Clase {clase_miscare_normalized:.1f}% | Fitness {fitness_access_normalized:.1f}% | Complet {complet_normalized:.1f}% | Family {family_normalized:.1f}% | Masaj {masaj_normalized:.1f}% | Kineto {kineto_normalized:.1f}%")

# Explicație servicii per sesiune
if masaj_normalized > 0 or kineto_normalized > 0:
    st.sidebar.caption(f"💡 **Servicii per sesiune:** Masaj {masaj_normalized:.1f}% | Kineto {kineto_normalized:.1f}% din slot-uri ocupate = sesiuni/lună (calculat automat din ocupare)")

subscription_distribution = {
    'clase_miscare': clase_miscare_pct / total_pct,
    'fitness_access': fitness_access_pct / total_pct,
    'complet': complet_pct / total_pct,
    'family': family_pct / total_pct,
    'masaj': masaj_pct / total_pct,
    'kineto': kineto_pct / total_pct
}

# Parametri demografici
st.sidebar.subheader("Parametri Demografici")
participation_rate = st.sidebar.slider(
    "Rata Participare Populație (%)",
    1, 30, 10, 1
) / 100

population_density = st.sidebar.number_input(
    "Densitate Populație (oameni/km²)",
    min_value=100,
    max_value=10000,
    value=1000,
    step=100
)

# Parametri campanie
st.sidebar.subheader("Parametri Campanie")
conversion_rate = st.sidebar.slider(
    "Rata Conversie Campanie (%)",
    1, 20, 5, 1
) / 100

coverage_rate = st.sidebar.slider(
    "Rata de Acoperire (%)",
    10, 100, 50, 5,
    help="Ce procent din populația interesată trebuie atins de campanie"
) / 100

# Calculează analiza pentru scenariul selectat (inclusiv campania cu conversie și acoperire)
analysis = get_scenario_analysis(
    selected_scenario,
    subscription_distribution,
    participation_rate,
    population_density,
    conversion_rate,
    coverage_rate
)

# Main content
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Venit Lunar (RON)",
        f"{analysis['revenue']['total']:,.0f}",
        delta=f"{analysis['revenue']['total'] - DESIRED_MONTHLY_REVENUE:,.0f}" if analysis['revenue']['total'] >= DESIRED_MONTHLY_REVENUE else None,
        delta_color="normal" if analysis['revenue']['total'] >= DESIRED_MONTHLY_REVENUE else "inverse"
    )

with col2:
    st.metric(
        "Clienți Totali",
        f"{analysis['total_clients']:,}",
        help="Numărul total de clienți necesari pentru scenariul selectat"
    )

with col3:
    st.metric(
        "Raza Influență (km)",
        f"{analysis['influence_radius_km']:.2f}",
        help="Raza de influență necesară pentru a atinge numărul de clienți"
    )

with col4:
    st.metric(
        "Ocupare",
        f"{analysis['occupancy_percentage']}",
        help="Rata de ocupare pentru scenariul selectat"
    )

# Header complet cu logo și branding Mobilis Vita+
# Încearcă mai multe căi pentru a găsi imaginea (local și Streamlit Cloud)
header_paths = [
    "images/header_complet.png",  # Cale relativă (Streamlit Cloud)
    r"C:\Users\D\Desktop\Folder\consult\mircea coach\fitness_center_dashboard\images\header_complet.png"  # Fallback local
]

header_b64 = None
header_loaded_path = None
for path in header_paths:
    if os.path.exists(path):
        header_b64 = load_image(path)
        if header_b64:
            header_loaded_path = path
            break

# Afișează header-ul complet dacă există
if header_b64:
    st.markdown(f"""
    <div style="text-align: center; margin: 0 0 20px 0; padding: 0;">
        <img src="data:image/png;base64,{header_b64}" style="max-width: 100%; width: 100%; height: auto; display: block;" />
    </div>
    """, unsafe_allow_html=True)

# Locație sub header
st.markdown(f"### 📍 Locație: {LOCATION['address']}, {LOCATION['city']}")

# Tabs pentru diferite vizualizări
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📊 Rezumat", 
    "💰 Venituri", 
    "👥 Clienți & Demografie", 
    "📈 Comparare Scenarii",
    "🗺️ Hartă Participare",
    "🎯 Campanie",
    "🏆 Analiză Concurențială",
    "📘 Scopul și Arhitectura Dashboard",
    "💵 Previziuni Financiare"
])

with tab1:
    st.subheader("Rezumat Analiză")
    
    # Cuprins pentru tab Rezumat
    toc_items = [
        ("intro-model", "💡 Introducere - Modelul de Gândire"),
        ("galerie-imagini", "🖼️ Galerie Imagini - Mobilis Vita+"),
        ("capacitate-spatiu", "📊 Capacitate Spațiu"),
        ("distributie-abonamente", "💳 Distribuție Abonamente"),
        ("clienti-tip", "👥 Clienți pe Tip Abonament"),
        ("raza-influenta", "🗺️ Raza de Influență"),
        ("model-gandire", "📘 Modelul de Gândire - Detalii Complete")
    ]
    st.markdown(create_table_of_contents("📑 Cuprins", toc_items), unsafe_allow_html=True)
    
    # Secțiune introductivă despre modelul de gândire - vizibilă imediat
    st.markdown('<div id="intro-model"></div>', unsafe_allow_html=True)
    st.info("""
    **💡 Cum funcționează acest dashboard?**
    
    Acest dashboard folosește o abordare **"De Sus în Jos" (Top-Down)**: pornim de la obiectivul final (venit dorit: 50,000 RON/lună) 
    și calculăm înapoi ce este necesar:
    
    **Venit Dorit** → **Clienți Necesari** → **Ocupare Spațiu** → **Populație Necesară** → **Rază de Influență**
    
    Toate calculele se actualizează automat când ajustezi parametrii din sidebar. 
    Pentru detalii complete despre logica de calcul, vezi secțiunea expandabilă de mai jos sau tab-ul "📘 Scopul și Arhitectura Dashboard".
    """)
    
    # Secțiune Galerie Imagini
    st.markdown('<div id="galerie-imagini"></div>', unsafe_allow_html=True)
    st.markdown("### 🖼️ Galerie Imagini - Mobilis Vita+")
    st.markdown("""
    **Descoperă spațiul nostru:** Un mediu modern, family-friendly, dedicat mișcării și sănătății pentru toate vârstele.
    """)
    
    # Galerie cu imagini organizate
    gallery_images = [
        ("images/spatiu_interior_1.png", "Spațiu interior modern - Zonă de mișcare și fitness"),
        ("images/clase_copii.png", "Clase de mișcare pentru copii - Family-friendly"),
        ("images/receptie_perete_verde.png", "Zonă de recepție cu perete verde - Primire caldă"),
        ("images/spatiu_interior_2.png", "Spațiu interior cu zonă pentru copii - Versatil și modern"),
        ("images/instructor_copil.png", "Ghidare personalizată - Fără judecăți, cu suport"),
        ("images/grup_miscare.png", "Clase de mișcare pentru toate vârstele - Comunitate"),
        ("images/clase_toate_varstele.png", "Inclusivitate - De la copii la bunici"),
        ("images/zona_asteptare_neon.png", "Zonă de așteptare modernă - Design contemporan"),
        ("images/receptie_logo.png", "Recepție cu branding Mobilis Vita+"),
        ("images/spatiu_interior_3.png", "Spațiu interior - Design modern și funcțional")
    ]
    
    # Afișează imagini în grid 2 coloane
    for i in range(0, len(gallery_images), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(gallery_images):
                img_path, caption = gallery_images[i + j]
                with col:
                    display_image(img_path, caption, max_width=600)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div id="capacitate-spatiu"></div>', unsafe_allow_html=True)
        st.markdown("### Capacitate Spațiu")
        st.write(f"**Capacitate maximă lunară:** {analysis['max_capacity']:,} slot-uri")
        st.write(f"**Slot-uri ocupate:** {analysis['occupied_slots']:,} slot-uri")
        st.write(f"**Rata ocupare:** {analysis['occupancy_rate']*100:.1f}%")
        
        st.markdown('<div id="distributie-abonamente"></div>', unsafe_allow_html=True)
        st.markdown("### Distribuție Abonamente")
        st.caption("💡 **Notă:** Procentajele sunt normalizate automat la 100% pentru calcule corecte.")
        dist_df = pd.DataFrame({
            'Tip Abonament': [SUBSCRIPTION_TYPES[k]['name'] for k in subscription_distribution.keys()],
            'Procentaj': [f"{v*100:.1f}%" for v in subscription_distribution.values()],
            'Preț (RON)': [SUBSCRIPTION_TYPES[k]['price'] for k in subscription_distribution.keys()]
        })
        st.dataframe(dist_df, use_container_width=True, hide_index=True)
        
        # Afișează suma pentru claritate
        total_check = sum(subscription_distribution.values()) * 100
        if abs(total_check - 100) < 0.01:
            st.success(f"✅ **Suma procentajelor:** {total_check:.1f}% (normalizat automat)")
        else:
            st.warning(f"⚠️ **Suma procentajelor:** {total_check:.1f}%")
    
    with col2:
        st.markdown('<div id="clienti-tip"></div>', unsafe_allow_html=True)
        st.markdown("### Clienți pe Tip Abonament")
        clients_data = analysis['revenue']['clients']
        # Filtrează doar cheile care există în SUBSCRIPTION_TYPES (exclude chei suplimentare precum 'pt_session_sessions')
        valid_keys = [k for k in clients_data.keys() if k in SUBSCRIPTION_TYPES]
        clients_df = pd.DataFrame({
            'Tip Abonament': [SUBSCRIPTION_TYPES[k]['name'] for k in valid_keys],
            'Număr Clienți': [clients_data[k] for k in valid_keys]
        })
        
        fig_clients = px.bar(
            clients_df,
            x='Tip Abonament',
            y='Număr Clienți',
            color='Tip Abonament',
            color_discrete_map=get_subscription_colors()
        )
        fig_clients.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig_clients, use_container_width=True)
        
        st.markdown('<div id="raza-influenta"></div>', unsafe_allow_html=True)
        st.markdown("### Raza de Influență")
        st.info(f"""
        Pentru a atinge **{analysis['total_clients']} clienți** cu:
        - Rata participare: **{participation_rate*100:.1f}%**
        - Densitate populație: **{population_density:,} oameni/km²**
        
        Este necesară o rază de influență de **{analysis['influence_radius_km']:.2f} km**
        """)
    
    # Secțiune detaliată despre modelul de gândire
    st.markdown("---")
    st.markdown('<div id="model-gandire"></div>', unsafe_allow_html=True)
    st.markdown("## 🧠 Modelul de Gândire - Detalii Complete")
    
    st.markdown("""
    **📚 Această secțiune explică în detaliu logica din spatele tuturor calculelor.**  
    **Recomandăm să o citești pentru a înțelege complet cum funcționează dashboard-ul.**
    """)
    
    with st.expander("📖 **Click pentru a deschide explicațiile detaliate despre modelul de gândire**", expanded=False):
        st.markdown("""
        ### 🎯 Abordarea "De Sus în Jos" (Top-Down)
        
        Dashboard-ul folosește o abordare **top-down**, pornind de la obiectivul final (venit dorit) și construind modelul înapoi:
        
        ```
        Venit Dorit (50,000 RON/lună)
            ↓
        Câți clienți sunt necesari?
            ↓
        Ce distribuție de abonamente?
            ↓
        Câtă ocupare a spațiului?
            ↓
        Câtă populație trebuie să acopăr?
            ↓
        Cât de mare trebuie să fie raza de influență?
        ```
        
        ---
        
        ### 📐 Principiile de Bază
        
        **1. Capacitatea Spațiului**
        - **Capacitate per oră**: 20 oameni
        - **Program**: 10 ore/zi × 7 zile/săptămână = 70 ore/săptămână
        - **Capacitate maximă lunară**: ~6,062 slot-uri (70 ore/săptămână × 4.33 săptămâni/lună × 20 oameni)
        - Fiecare "slot" reprezintă o oră de utilizare a spațiului
        
        **2. Scenariile de Ocupare**
        - **Redus (25-50%)**: Realist pentru primele luni
        - **Mediu (50-75%)**: Realist după stabilizare
        - **Ridicat (>75%)**: Optimist, necesită timp și marketing puternic
        
        **3. Calculul Clienților**
        - Pentru abonamente nelimitate (Basic, Standard, Premium): presupunem **3 vizite/săptămână** per client
        - Pentru PT/Reabilitare: fiecare slot ocupat = 1 sesiune; presupunem **5 sesiuni/lună** per client
        - Clienții sunt calculați astfel încât să ocupe slot-urile alocate fiecărui tip de serviciu
        
        **4. Calculul Veniturilor**
        - Venit = Suma (Clienți tip × Preț abonament tip)
        - Pentru PT: Venit = Sesiuni PT × Preț per sesiune
        
        ---
        
        ### 🗺️ Raza de Influență - Logica Geografică
        
        Raza de influență este calculată astfel:
        
        1. **Populație disponibilă per km²** = Densitate populație × Rata participare
        2. **Suprafață necesară** = Clienți necesari / Populație disponibilă per km²
        3. **Rază** = √(Suprafață / π)
        
        **Exemplu:**
        - Ai nevoie de 300 clienți
        - Densitate: 1,000 oameni/km²
        - Participare: 10% → 100 oameni disponibili/km²
        - Suprafață necesară: 300 / 100 = 3 km²
        - Rază: √(3 / 3.14) ≈ 1 km
        
        **De ce este important?**
        - Știi exact cât de mare trebuie să fie zona de marketing
        - Poți planifica campaniile geografic
        - Poți estima costurile de marketing
        
        ---
        
        ### 📊 Distribuția Serviciilor
        
        Toate serviciile (inclusiv PT/Reabilitare) formează **100% din slot-uri ocupate**:
        - Procentajele se normalizează automat
        - PT/Reabilitare ocupă slot-uri ca orice alt serviciu
        - Fiecare procentaj reprezintă cât din slot-urile ocupate sunt alocate acelui serviciu
        
        **Exemplu:**
        - Ocupare: 60% = 3,637 slot-uri ocupate
        - PT: 5% → 182 slot-uri = 182 sesiuni PT/lună
        - Basic: 40% → 1,455 slot-uri → ~112 clienți (presupunând 3 vizite/săptămână)
        
        ---
        
        ### 💡 Insights Cheie
        
        **1. Relația între Ocupare și Venituri**
        - Ocupare mai mare = mai mulți clienți = mai multe venituri
        - Dar: ocupare 100% este nerealistă
        - Scenariul mediu (50-75%) este cel mai echilibrat
        
        **2. Impactul Distribuției Abonamentelor**
        - Mai mulți premium = venituri mai mari
        - Dar: mai puțini clienți premium disponibili
        - Echilibrul este cheia
        
        **3. Importanța Razei de Influență**
        - Rază mică (<2 km) = campanie locală, mai ieftină
        - Rază mare (>5 km) = campanie amplă, mai scumpă
        - Planifică în consecință
        
        **4. Rata de Participare este Critică**
        - 10% este o estimare conservatoare
        - Dacă ai date reale, folosește-le
        - Impact direct asupra razei de influență
        - Reprezintă procentul din populația totală care ar putea fi interesați de fitness
        
        **5. Rata de Acoperire Definește Dimensiunea Campaniei**
        - Controlată de tine (10-100%, default 50%)
        - Definește ce procent din populația interesată trebuie atins
        - Impact direct asupra costurilor campaniei
        - Mai mare = campanie mai amplă, dar mai scumpă
        
        **6. Rata de Conversie Determină Eficiența**
        - Reflectă calitatea campaniei și a ofertei
        - 5% este un standard realist pentru campanii bine targetate
        - Poate fi îmbunătățită prin mesaje clare și oferte atractive
        - Impact direct asupra numărului de oameni care trebuie atinși
        
        ---
        
        ### 🔄 Cum Funcționează Dashboard-ul
        
        **Fluxul de Date:**
        ```
        Utilizator ajustează filtre (ocupare, distribuție, parametri demografici)
            ↓
        Dashboard recalculează automat toate metricile
            ↓
        Rezultatele se actualizează în timp real
            ↓
        Utilizator vede impactul imediat
        ```
        
        **De ce este important?**
        - Nu trebuie să rulezi scripturi separate
        - Poți explora rapid multe scenarii
        - Înțelegi relațiile între parametri
        
        ---
        
        ### 📝 Notă Importantă
        
        Acest dashboard este un **instrument de planificare și analiză**, nu o predicție exactă. 
        
        **Valoarea lui:**
        - Îți dă o înțelegere clară a potențialului
        - Te ajută să planifici marketing-ul
        - Te ajută să iei decizii informate
        - Poți explora scenarii diferite rapid
        
        **Limitele:**
        - Folosește presupuneri (rata participare, distribuție)
        - Nu include cheltuieli (în dezvoltare)
        - Blocurile sunt simulate (poți importa date reale)
        
        ---
        
        **💡 Pentru mai multe detalii despre modelul de gândire, vezi tab-ul "📘 Scopul și Arhitectura Dashboard"**
        """)

with tab2:
    st.subheader("Analiză Venituri")
    
    # Cuprins pentru tab Venituri
    toc_items = [
        ("distributie-venituri", "📊 Distribuție Venituri pe Tip Abonament"),
        ("comparatie-venit", "📈 Comparație cu Venitul Dorit"),
        ("tabel-detaliu", "📋 Tabel Detaliat Venituri")
    ]
    st.markdown(create_table_of_contents("📑 Cuprins", toc_items), unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div id="distributie-venituri"></div>', unsafe_allow_html=True)
        # Grafic venituri pe tip abonament
        revenue_data = analysis['revenue']
        # Obține doar tipurile cu venit > 0 (din toate tipurile disponibile)
        active_types = [k for k in SUBSCRIPTION_TYPES.keys() 
                       if k in revenue_data and revenue_data.get(k, 0) > 0]
        
        revenue_df = pd.DataFrame({
            'Tip Abonament': [SUBSCRIPTION_TYPES[k]['name'] for k in active_types],
            'Venit (RON)': [revenue_data.get(k, 0) for k in active_types]
        })
        
        fig_revenue = px.pie(
            revenue_df,
            values='Venit (RON)',
            names='Tip Abonament',
            title="Distribuție Venituri pe Tip Abonament",
            color='Tip Abonament',
            color_discrete_map=get_subscription_colors()
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        # Comparație cu venitul dorit
        fig_target = go.Figure()
        fig_target.add_trace(go.Bar(
            x=['Venit Actual', 'Venit Dorit'],
            y=[revenue_data['total'], DESIRED_MONTHLY_REVENUE],
            marker_color=['#3498db', '#e74c3c'],
            text=[f"{revenue_data['total']:,.0f} RON", f"{DESIRED_MONTHLY_REVENUE:,.0f} RON"],
            textposition='auto'
        ))
        fig_target.update_layout(
            title="Comparație cu Venitul Dorit",
            yaxis_title="Venit (RON)",
            height=400
        )
        st.plotly_chart(fig_target, use_container_width=True)
        
        # Tabel detaliat venituri
        st.markdown('<div id="tabel-detaliu"></div>', unsafe_allow_html=True)
        revenue_detail_data = []
        for k in active_types:
            if k in revenue_data['clients']:
                clients_count = revenue_data['clients'].get(k, 0)
                price = SUBSCRIPTION_TYPES[k]['price']
                if SUBSCRIPTION_TYPES[k].get('is_session_based', False):
                    price_label = f"{price} RON/sesiune"
                else:
                    price_label = f"{price} RON/lună"
                
                revenue_detail_data.append({
                    'Tip Abonament': SUBSCRIPTION_TYPES[k]['name'],
                    'Clienți/Sesiuni': clients_count,
                    'Preț': price_label,
                    'Venit Total (RON)': revenue_data.get(k, 0)
                })
        
        revenue_detail = pd.DataFrame(revenue_detail_data)
        if len(revenue_detail) > 0:
            total_clients = revenue_detail['Clienți/Sesiuni'].sum()
            revenue_detail.loc[len(revenue_detail)] = ['TOTAL', total_clients, '', revenue_data['total']]
        st.dataframe(revenue_detail, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Analiză Clienți & Demografie")
    
    # Cuprins pentru tab Clienți & Demografie
    toc_items = [
        ("necesar-clienti", "👥 Necesar Clienți"),
        ("parametri-demografici", "📊 Parametri Demografici"),
        ("zona-acoperire", "🗺️ Zonă de Acoperire")
    ]
    st.markdown(create_table_of_contents("📑 Cuprins", toc_items), unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div id="necesar-clienti"></div>', unsafe_allow_html=True)
        st.markdown("### Necesar Clienți")
        clients_data = analysis['revenue']['clients']
        # Obține toate tipurile active din clients_data care există în SUBSCRIPTION_TYPES
        active_client_types = [k for k in SUBSCRIPTION_TYPES.keys() 
                              if k in clients_data and clients_data.get(k, 0) > 0]
        
        # Pentru serviciile per sesiune, afișăm și numărul de sesiuni
        display_data = []
        for k in active_client_types:
            name = SUBSCRIPTION_TYPES[k]['name']
            clients_count = clients_data.get(k, 0)
            sub_info = SUBSCRIPTION_TYPES[k]
            
            # Verifică dacă este serviciu per sesiune
            if sub_info.get('is_session_based', False):
                # Pentru servicii per sesiune, afișăm clienți și sesiuni
                sessions_key = f'{k}_sessions'
                sessions_count = clients_data.get(sessions_key, clients_count * 5)
                display_data.append({
                    'Tip Abonament': name,
                    'Număr Clienți': clients_count,
                    'Sesiuni/lună': sessions_count,
                    'Label': f"{clients_count} clienți ({sessions_count} sesiuni/lună)"
                })
            else:
                display_data.append({
                    'Tip Abonament': name,
                    'Număr Clienți': clients_count,
                    'Sesiuni/lună': None,
                    'Label': f"{clients_count} clienți"
                })
        
        clients_df = pd.DataFrame(display_data)
        
        # Grafic cu label-uri personalizate
        fig_clients_detailed = px.bar(
            clients_df,
            x='Tip Abonament',
            y='Număr Clienți',
            text='Label',
            color='Tip Abonament',
            color_discrete_map=get_subscription_colors()
        )
        fig_clients_detailed.update_traces(textposition='outside')
        fig_clients_detailed.update_layout(
            title="Necesar Clienți pe Tip Serviciu",
            yaxis_title="Număr Clienți",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_clients_detailed, use_container_width=True)
        
        # Tabel detaliat cu sesiuni pentru serviciile per sesiune
        session_based_types = [k for k in active_client_types if SUBSCRIPTION_TYPES[k].get('is_session_based', False)]
        for k in session_based_types:
            sessions_key = f'{k}_sessions'
            sessions_count = clients_data.get(sessions_key, 0)
            st.info(f"💡 **{SUBSCRIPTION_TYPES[k]['name']}:** {clients_data.get(k, 0)} clienți × ~5 sesiuni/lună = {sessions_count} sesiuni/lună")
    
    with col2:
        st.markdown('<div id="parametri-demografici"></div>', unsafe_allow_html=True)
        st.markdown("### Parametri Demografici")
        demo_data = {
            'Parametru': [
                'Rata Participare',
                'Densitate Populație',
                'Raza Influență',
                'Suprafață Acoperită',
                'Populație Totală',
                'Populație Interesată'
            ],
            'Valoare': [
                f"{participation_rate*100:.1f}%",
                f"{population_density:,} oameni/km²",
                f"{analysis['influence_radius_km']:.2f} km",
                f"{analysis['campaign']['area_km2']:.2f} km²",
                f"{analysis['campaign']['total_population']:,}",
                f"{analysis['campaign']['interested_population']:,}"
            ]
        }
        demo_df = pd.DataFrame(demo_data)
        st.dataframe(demo_df, use_container_width=True, hide_index=True)
        
        # Vizualizare rază de influență
        st.markdown('<div id="zona-acoperire"></div>', unsafe_allow_html=True)
        st.markdown("### Zonă de Acoperire")
        st.info(f"""
        **Suprafață acoperită:** {analysis['campaign']['area_km2']:.2f} km²
        
        **Populație în zonă:** {analysis['campaign']['total_population']:,} oameni
        
        **Populație potențial interesată:** {analysis['campaign']['interested_population']:,} oameni
        """)

with tab4:
    st.subheader("Comparare Scenarii")
    
    # Compară toate scenariile
    comparison_df = compare_scenarios(
        subscription_distribution,
        participation_rate,
        population_density,
        conversion_rate,
        coverage_rate
    )
    
    st.markdown('<div id="tabel-comparare"></div>', unsafe_allow_html=True)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div id="grafic-venituri"></div>', unsafe_allow_html=True)
        # Grafic venituri pe scenarii
        fig_comp_revenue = px.bar(
            comparison_df,
            x='Scenariu',
            y='Venit Total (RON)',
            color='Scenariu',
            title="Venituri pe Scenarii",
            text='Venit Total (RON)'
        )
        fig_comp_revenue.update_traces(texttemplate='%{text:,.0f} RON', textposition='outside')
        fig_comp_revenue.add_hline(
            y=DESIRED_MONTHLY_REVENUE,
            line_dash="dash",
            line_color="red",
            annotation_text="Venit Dorit"
        )
        st.plotly_chart(fig_comp_revenue, use_container_width=True)
    
    with col2:
        st.markdown('<div id="grafic-raza"></div>', unsafe_allow_html=True)
        # Grafic rază influență pe scenarii
        fig_comp_radius = px.bar(
            comparison_df,
            x='Scenariu',
            y='Raza Influență (km)',
            color='Scenariu',
            title="Raza de Influență pe Scenarii",
            text='Raza Influență (km)'
        )
        fig_comp_radius.update_traces(texttemplate='%{text:.2f} km', textposition='outside')
        st.plotly_chart(fig_comp_radius, use_container_width=True)
    
    # Grafic clienți pe scenarii
    fig_comp_clients = px.line(
        comparison_df,
        x='Scenariu',
        y='Clienți Totali',
        markers=True,
        title="Evoluție Clienți pe Scenarii"
    )
    st.plotly_chart(fig_comp_clients, use_container_width=True)

with tab5:
    st.subheader("🗺️ Hartă Participare pe Blocuri și Cartiere")
    
    # Cuprins pentru tab Hartă
    toc_items = [
        ("harta-interactiva", "🗺️ Hartă Interactivă"),
        ("linkuri-google-maps", "📍 Link-uri Google Maps"),
        ("informatii-analiza", "ℹ️ Informații despre Analiză"),
        ("detalii-blocuri", "🏘️ Detalii Blocuri și Cartiere")
    ]
    st.markdown(create_table_of_contents("📑 Cuprins", toc_items), unsafe_allow_html=True)
    
    # Funcție pentru calcularea distanței Haversine (în km)
    def haversine_distance(lat1, lon1, lat2, lon2):
        """Calculează distanța între două puncte geografice în km"""
        R = 6371  # Raza Pământului în km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c
    
    # Coordonatele locației
    center_lat, center_lon = LOCATION['coordinates']
    radius_km = analysis['influence_radius_km']
    
    # Inițializare variabile
    num_blocks = 20
    blocks_data = []
    
    # Creează hartă centrată pe locație (zoom optimizat pentru Bacău)
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=14,  # Zoom mai apropiat pentru a vedea mai bine detaliile
        tiles='OpenStreetMap'
    )
    
    # Adaugă marker pentru locația salii (marcat distinctiv cu verde)
    folium.Marker(
        [center_lat, center_lon],
        popup=f"<b>💪 Sala Fitness & Recuperare</b><br>{LOCATION['address']}<br>{LOCATION['city']}<br><b>Poziționare:</b> Controlată, anti-aglomerație<br><b>Capacitate:</b> {CAPACITY_PER_HOUR} persoane/oră",
        tooltip="Sala Noastră - Aleea Prieteniei nr 14",
        icon=folium.Icon(color='green', icon='home')
    ).add_to(m)
    
    # Adaugă markeri pentru concurenți
    for comp_key, comp_loc in COMPETITOR_LOCATIONS.items():
        comp_lat, comp_lon = comp_loc['coordinates']
        comp_name = comp_loc['name']
        
        # Obține informații despre concurent din COMPETITORS dacă există
        comp_info = ""
        if comp_key in COMPETITORS:
            comp_data = COMPETITORS[comp_key]
            comp_info = f"<br><b>Capacitate:</b> {comp_data['capacity_simultaneous']} persoane<br><b>Membri:</b> {comp_data['active_members']}<br><b>Model:</b> {comp_data['model']}"
        elif comp_key == 'gymnastic_club':
            comp_info = "<br><b>Tip:</b> Sală locală mică<br><b>Model:</b> Comunitate restrânsă"
        elif comp_key == 'pole_fitness':
            comp_info = "<br><b>Tip:</b> Specializată (Pole Fitness)<br><b>Model:</b> Nișă specifică"
        elif comp_key == 'q_fitt':
            comp_info = "<br><b>Tip:</b> Sală locală<br><b>Model:</b> Comunitate restrânsă"
        
        folium.Marker(
            [comp_lat, comp_lon],
            popup=f"<b>🏋️ {comp_name}</b>{comp_info}",
            tooltip=f"Concurent: {comp_name}",
            icon=folium.Icon(color=comp_loc['color'], icon='info-sign')
        ).add_to(m)
    
    # Adaugă cercul de influență
    folium.Circle(
        location=[center_lat, center_lon],
        radius=radius_km * 1000,  # Convertim km în metri
        popup=f"Raza de influență: {radius_km:.2f} km",
        color='#3186cc',
        fill=True,
        fillColor='#3186cc',
        fillOpacity=0.2,
        weight=2
    ).add_to(m)
    
    # Generează chenare (poligone) pentru blocurile/cartierele reale
    # Creăm chenare rectangulare care reprezintă blocurile din cartiere
    # Fiecare chenar are o suprafață aproximativă de 0.1-0.15 km² (un bloc/cartier)
    
    total_clients_needed = analysis['total_clients']
    
    # Creăm o grilă de chenare în jurul locației, aliniată cu structura reală a orașului
    # Folosim o grilă mai densă pentru a se alinia mai bine cu blocurile reale
    grid_size = 7  # 7x7 = 49 chenare (mai multe pentru acoperire mai bună)
    block_size_km = 0.12  # Fiecare chenar are ~0.12 km latime/înălțime (mai mic pentru precizie)
    
    # Calculează participarea medie necesară pentru a atinge obiectivul
    total_area_covered = math.pi * (radius_km ** 2)  # Suprafața totală acoperită
    total_population_in_radius = int(total_area_covered * population_density)
    avg_participation_needed = total_clients_needed / total_population_in_radius if total_population_in_radius > 0 else participation_rate
    
    for i in range(grid_size):
        for j in range(grid_size):
            # Calculează centrul chenarului
            offset_lat = (i - grid_size/2 + 0.5) * block_size_km / 111  # +0.5 pentru centrare
            offset_lon = (j - grid_size/2 + 0.5) * block_size_km / (111 * math.cos(math.radians(center_lat)))
            
            block_center_lat = center_lat + offset_lat
            block_center_lon = center_lon + offset_lon
            
            # Calculează distanța de la centrul sălii la centrul chenarului
            distance = haversine_distance(center_lat, center_lon, block_center_lat, block_center_lon)
            
            # Skip chenarele care sunt prea departe de raza de influență (doar cele din interiorul razei)
            if distance > radius_km:
                continue
            
            # Calculează suprafața chenarului (aproximativ)
            block_area_km2 = block_size_km * block_size_km
            block_population = int(block_area_km2 * population_density)
            
            # Participare necesară bazată pe distanță și necesarul total
            # Mai aproape = participare mai mare necesară
            if distance <= radius_km * 0.3:
                participation_multiplier = 1.3  # Zone apropiate: participare mai mare
                color = 'green'
                intensity = 'Ridicată'
            elif distance <= radius_km * 0.6:
                participation_multiplier = 1.0  # Zone medii: participare normală
                color = 'blue'
                intensity = 'Medie'
            elif distance <= radius_km * 0.9:
                participation_multiplier = 0.7  # Zone îndepărtate: participare redusă
                color = 'orange'
                intensity = 'Moderată'
            else:
                participation_multiplier = 0.5  # Zone la margine: participare scăzută
                color = 'red'
                intensity = 'Redusă'
            
            # Calculează participarea necesară pentru acest bloc
            # Participarea este calculată astfel încât suma tuturor blocurilor să dea clienții necesari
            # Folosim participarea medie necesară ca bază și ajustăm cu multiplicatorul de distanță
            participation_needed = avg_participation_needed * participation_multiplier
            
            # Ajustare: zonele mai apropiate trebuie să contribuie mai mult
            # Normalizăm astfel încât suma tuturor blocurilor să dea clienții necesari
            participation_needed = max(0.01, min(participation_needed, 0.30))  # Limitează între 1% și 30%
            
            interested_population = int(block_population * participation_needed)
            
            # Creează chenarul (poligon rectangular)
            half_size = block_size_km / 2
            block_bounds = [
                [block_center_lat - half_size/111, block_center_lon - half_size/(111 * math.cos(math.radians(center_lat)))],
                [block_center_lat + half_size/111, block_center_lon - half_size/(111 * math.cos(math.radians(center_lat)))],
                [block_center_lat + half_size/111, block_center_lon + half_size/(111 * math.cos(math.radians(center_lat)))],
                [block_center_lat - half_size/111, block_center_lon + half_size/(111 * math.cos(math.radians(center_lat)))],
                [block_center_lat - half_size/111, block_center_lon - half_size/(111 * math.cos(math.radians(center_lat)))]  # Închide poligonul
            ]
            
            blocks_data.append({
                'lat': block_center_lat,
                'lon': block_center_lon,
                'distance': distance,
                'participation': participation_needed,
                'population': block_population,
                'interested': interested_population,
                'color': color,
                'intensity': intensity,
                'bounds': block_bounds
            })
            
            # Adaugă poligonul (chenar) pentru bloc
            folium.Polygon(
                locations=block_bounds,
                popup=folium.Popup(
                    f"""
                    <b>Bloc/Cartier</b><br>
                    <b>Distanță:</b> {distance:.2f} km<br>
                    <b>Participare necesară:</b> {participation_needed*100:.1f}% ({intensity})<br>
                    <b>Populație:</b> {block_population:,} oameni<br>
                    <b>Populație necesară:</b> {interested_population:,} oameni<br>
                    <b>Suprafață:</b> {block_area_km2:.2f} km²
                    """,
                    max_width=280
                ),
                tooltip=f"Participare necesară: {participation_needed*100:.1f}% ({intensity})",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.4,
                weight=2
            ).add_to(m)
    
    # Adaugă legendă îmbunătățită - mutată în top-right pentru vizibilitate maximă
    legend_html = f'''
    <div style="position: fixed; 
                top: 80px; right: 20px; width: 320px; 
                background-color: white; border:4px solid #1f77b4; z-index:9999; 
                font-size:16px; padding: 18px; border-radius: 10px; 
                box-shadow: 0 6px 15px rgba(0,0,0,0.4);
                font-family: Arial, sans-serif;
                max-height: 85vh; overflow-y: auto;">
    <h4 style="margin-top:0; margin-bottom:15px; font-size:20px; font-weight:bold; color:#1f77b4; border-bottom:3px solid #1f77b4; padding-bottom:8px;">📋 Legendă</h4>
    <p style="margin:10px 0 8px 0; font-weight:bold; font-size:17px; color:#000000;">Participare Necesară:</p>
    <p style="margin:5px 0; font-size:16px; line-height:1.6; color:#000000;"><span style="color:green; font-size:22px; font-weight:bold; margin-right:8px;">▢</span> <b>Ideală</b> (&lt;10%)</p>
    <p style="margin:5px 0; font-size:16px; line-height:1.6; color:#000000;"><span style="color:blue; font-size:22px; font-weight:bold; margin-right:8px;">▢</span> <b>Bună</b> (10-20%)</p>
    <p style="margin:5px 0; font-size:16px; line-height:1.6; color:#000000;"><span style="color:orange; font-size:22px; font-weight:bold; margin-right:8px;">▢</span> <b>Medie</b> (20-30%)</p>
    <p style="margin:5px 0; font-size:16px; line-height:1.6; color:#000000;"><span style="color:red; font-size:22px; font-weight:bold; margin-right:8px;">▢</span> <b>Dificilă</b> (&gt;30%)</p>
    <p style="margin:12px 0 8px 0; font-size:13px; color:#666; font-style:italic; border-top:2px solid #ddd; padding-top:10px;">Chenarele reprezintă blocurile/cartierele</p>
    <hr style="margin:12px 0; border:2px solid #ddd;">
    <p style="margin:10px 0 8px 0; font-weight:bold; font-size:17px; color:#000000;">Locații:</p>
    <p style="margin:5px 0; font-size:16px; line-height:1.6; color:#000000;"><span style="color:green; font-size:22px; margin-right:8px;">🏠</span> <b>Sală Noastră</b></p>
    <p style="margin:5px 0; font-size:16px; line-height:1.6; color:#000000;"><span style="color:red; font-size:22px; margin-right:8px;">🏋️</span> <b>Concurenți</b></p>
    <p style="margin:5px 0; font-size:16px; line-height:1.6; color:#000000;"><span style="color:#3186cc; font-size:22px; margin-right:8px;">○</span> <b>Rază influență</b> (~{radius_km:.2f} km)</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Afișează hartă
    st.markdown('<div id="harta-interactiva"></div>', unsafe_allow_html=True)
    st.info("💡 **Notă:** Harta necesită conexiune la internet pentru a se încărca. Dacă nu apare, verifică conexiunea.")
    
    try:
        # Salvează harta temporar și o afișează
        map_data = st_folium(m, width=1200, height=600, returned_objects=[])
    except Exception as e:
        st.error(f"⚠️ Eroare la afișarea hărții Folium: {str(e)}")
        st.info("💡 **Soluții:**\n1. Verifică conexiunea la internet\n2. Reîmprospătează pagina (F5)\n3. Verifică dacă firewall-ul blochează conexiunea")
        
        # Alternativă: Hărți Google Maps
        st.markdown("---")
        st.markdown('<div id="linkuri-google-maps"></div>', unsafe_allow_html=True)
        st.markdown("### 🗺️ Hărți Google Maps - Locații Săli")
        
        # Harta noastră
        st.markdown("#### 📍 Sală Noastră")
        gym_lat, gym_lon = LOCATION['coordinates']
        google_maps_url = f"https://www.google.com/maps?q={gym_lat},{gym_lon}&z=15"
        st.markdown(f"**Locație:** {LOCATION['address']}, {LOCATION['city']}")
        st.markdown(f"**Coordonate:** {gym_lat:.4f}, {gym_lon:.4f}")
        st.markdown(f"[🗺️ Deschide în Google Maps]({google_maps_url})")
        
        # Iframe cu Google Maps pentru sala noastră
        st.markdown(f"""
        <iframe 
            width="100%" 
            height="400" 
            frameborder="0" 
            style="border:0" 
            src="https://www.google.com/maps/embed/v1/place?key=AIzaSyBFw0Qbyq9zTFTd-tUY6d-s6M4kfWL7l0Q&q={gym_lat},{gym_lon}&zoom=15" 
            allowfullscreen>
        </iframe>
        """, unsafe_allow_html=True)
        
        # Hărți pentru concurenți
        st.markdown("#### 🏋️ Locații Concurenți")
        for comp_key, comp_loc in COMPETITOR_LOCATIONS.items():
            comp_lat, comp_lon = comp_loc['coordinates']
            comp_name = comp_loc['name']
            comp_url = f"https://www.google.com/maps?q={comp_lat},{comp_lon}&z=15"
            
            st.markdown(f"**{comp_name}**")
            st.markdown(f"Coordonate: {comp_lat:.4f}, {comp_lon:.4f}")
            st.markdown(f"[🗺️ Deschide în Google Maps]({comp_url})")
            st.markdown("---")
        
        # Informații despre hartă
        st.markdown('<div id="informatii-analiza"></div>', unsafe_allow_html=True)
        st.markdown("### Informații despre Analiză")
        st.write(f"**Raza de influență:** {radius_km:.2f} km")
        st.write(f"**Număr blocuri/cartiere:** {num_blocks}")
    
    # Secțiune alternativă cu Google Maps
    st.markdown("---")
    st.markdown("## 🗺️ Hărți Google Maps - Locații Săli")
    st.info("💡 **Alternativă:** Dacă harta interactivă de mai sus nu funcționează corect, poți folosi aceste link-uri Google Maps pentru a vedea locațiile exacte ale tuturor sălilor.")
    
    col_map1, col_map2 = st.columns(2)
    
    with col_map1:
        st.markdown("### 📍 Sală Noastră")
        gym_lat, gym_lon = LOCATION['coordinates']
        google_maps_url = f"https://www.google.com/maps?q={gym_lat},{gym_lon}&z=15"
        st.markdown(f"**Locație:** {LOCATION['address']}, {LOCATION['city']}")
        st.markdown(f"**Coordonate:** {gym_lat:.4f}, {gym_lon:.4f}")
        st.markdown(f"**Link:** [{google_maps_url}]({google_maps_url})")
        st.markdown(f"[🗺️ **Deschide în Google Maps**]({google_maps_url})")
    
    with col_map2:
        st.markdown("### 🏋️ Concurenți - Link-uri Google Maps")
        for comp_key, comp_loc in COMPETITOR_LOCATIONS.items():
            comp_lat, comp_lon = comp_loc['coordinates']
            comp_name = comp_loc['name']
            comp_url = f"https://www.google.com/maps?q={comp_lat},{comp_lon}&z=15"
            
            st.markdown(f"**{comp_name}**")
            st.markdown(f"Coordonate: {comp_lat:.4f}, {comp_lon:.4f}")
            st.markdown(f"[🗺️ Deschide în Google Maps]({comp_url})")
            st.markdown("---")
    
    # Tabel cu detalii blocuri
    st.markdown("---")
    st.markdown('<div id="detalii-blocuri"></div>', unsafe_allow_html=True)
    st.markdown("### Detalii Blocuri și Cartiere")
    
    blocks_df = pd.DataFrame(blocks_data)
    blocks_df = blocks_df.sort_values('distance')
    blocks_df['Bloc'] = [f"Bloc #{i+1}" for i in range(len(blocks_df))]
    blocks_df['Distanță (km)'] = blocks_df['distance'].round(2)
    blocks_df['Participare (%)'] = (blocks_df['participation'] * 100).round(1)
    blocks_df['Populație'] = blocks_df['population']
    blocks_df['Interesați'] = blocks_df['interested']
    blocks_df['Intensitate'] = blocks_df['intensity']
    
    display_df = blocks_df[['Bloc', 'Distanță (km)', 'Participare (%)', 'Populație', 'Interesați', 'Intensitate']]
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Statistici
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Blocuri", len(blocks_data))
    with col2:
        st.metric("Populație Totală", f"{blocks_df['Populație'].sum():,}")
    with col3:
        st.metric("Populație Interesată", f"{blocks_df['Interesați'].sum():,}")
    with col4:
        avg_participation = blocks_df['Participare (%)'].mean()
        st.metric("Participare Medie", f"{avg_participation:.1f}%")

with tab6:
    st.subheader("Analiză Campanie la Nivel de Cartier")
    
    # Cuprins pentru tab Campanie
    toc_items = [
        ("metrici-campanie", "📊 Metrici Campanie"),
        ("detalii-campanie", "📋 Detalii Campanie"),
        ("funnel-conversie", "📈 Funnel Conversie"),
        ("recomandari-campanie", "💡 Recomandări Campanie"),
        ("cost-campanie", "💰 Estimare Cost Campanie"),
        ("sondaj-cartier", "📋 Sondaj în Cartier"),
        ("concurs-cartier", "🏆 Concurs de Cartier")
    ]
    st.markdown(create_table_of_contents("📑 Cuprins", toc_items), unsafe_allow_html=True)
    
    campaign = analysis['campaign']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Populație de Atins",
            f"{campaign['people_to_reach']:,}",
            help="Populația care trebuie atinsă de campanie (din cei interesați)"
        )
    
    with col2:
        st.metric(
            "Raza Campanie (km)",
            f"{campaign['radius_km']:.2f}",
            help="Raza necesară pentru campanie"
        )
    
    with col3:
        st.metric(
            "Rata Conversie",
            f"{conversion_rate*100:.1f}%",
            help="Ce procent din cei atinși devin clienți"
        )
    
    with col4:
        st.metric(
            "Suprafață (km²)",
            f"{campaign['area_km2']:.2f}",
            help="Suprafața acoperită de campanie"
        )
    
    # Metric suplimentar pentru rata de acoperire
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Rata de Acoperire",
            f"{coverage_rate*100:.1f}%",
            help="Ce procent din populația interesată trebuie atins de campanie"
        )
    with col2:
        st.metric(
            "Populație Interesată",
            f"{campaign['interested_population']:,}",
            help="Numărul total de oameni potențial interesați în zonă"
        )
    
    st.markdown('<div id="detalii-campanie"></div>', unsafe_allow_html=True)
    st.markdown("### Detalii Campanie")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Dimensiune Campanie:**
        - Populație totală în zonă: **{campaign['total_population']:,}** oameni
        - Populație potențial interesată: **{campaign['interested_population']:,}** oameni ({participation_rate*100:.1f}% din total)
        - Populație de atins prin campanie: **{campaign['people_to_reach']:,}** oameni ({coverage_rate*100:.1f}% din cei interesați)
        
        **Acoperire Geografică:**
        - Raza: **{campaign['radius_km']:.2f} km**
        - Suprafață: **{campaign['area_km2']:.2f} km²**
        
        **Rata de Acoperire:** {coverage_rate*100:.1f}% din populația interesată trebuie atinsă de campanie pentru a obține clienții necesari.
        """)
    
    with col2:
        st.markdown('<div id="funnel-conversie"></div>', unsafe_allow_html=True)
        # Grafic piramida conversiei cu tooltip-uri detaliate
        # Definiții și metode de calcul pentru fiecare etapă
        definitions = [
            f"<b>Definiție:</b> Totalul populației care locuiește în zona acoperită de campanie.<br>"
            f"<b>Calcul:</b> Suprafață (km²) × Densitate Populație<br>"
            f"<b>Formula:</b> {campaign['area_km2']:.2f} km² × {population_density:,} oameni/km² = {campaign['total_population']:,} oameni",
            
            f"<b>Definiție:</b> Numărul de oameni din populația totală care ar putea fi interesați de serviciile fitness.<br>"
            f"<b>Calcul:</b> Populație Totală × Rata de Participare<br>"
            f"<b>Formula:</b> {campaign['total_population']:,} × {participation_rate*100:.1f}% = {campaign['interested_population']:,} oameni<br>"
            f"<b>Notă:</b> Rata de participare reflectă procentul din populație care ar putea fi interesați de fitness.",
            
            f"<b>Definiție:</b> Numărul de oameni din populația interesată care trebuie atinși efectiv de campanie.<br>"
            f"<b>Calcul:</b> Populație Interesată × Rata de Acoperire<br>"
            f"<b>Formula:</b> {campaign['interested_population']:,} × {coverage_rate*100:.1f}% = {campaign['people_to_reach']:,} oameni<br>"
            f"<b>Notă:</b> Rata de acoperire definește ce procent din cei interesați trebuie atinși pentru a obține clienții necesari.",
            
            f"<b>Definiție:</b> Numărul final de clienți obținuți după conversie.<br>"
            f"<b>Calcul:</b> Populație de Atins × Rata de Conversie<br>"
            f"<b>Formula:</b> {campaign['people_to_reach']:,} × {conversion_rate*100:.1f}% = {analysis['total_clients']:,} clienți<br>"
            f"<b>Notă:</b> Rata de conversie reprezintă procentul din cei atinși care devin efectiv clienți."
        ]
        
        conversion_stages = pd.DataFrame({
            'Etapă': [
                'Populație Totală',
                'Populație Interesată',
                'Populație de Atins',
                'Clienți Finali'
            ],
            'Număr': [
                campaign['total_population'],
                campaign['interested_population'],
                campaign['people_to_reach'],
                analysis['total_clients']
            ],
            'Definiție': definitions
        })
        
        fig_funnel = px.funnel(
            conversion_stages,
            x='Număr',
            y='Etapă',
            title="Funnel Conversie Campanie",
            custom_data=['Definiție']
        )
        
        # Actualizează tooltip-ul pentru a include definiția și metoda de calcul
        fig_funnel.update_traces(
            hovertemplate='<b>%{y}</b><br>' +
                         'Număr: <b>%{x:,}</b><br>' +
                         '<br>%{customdata[0]}<br>' +
                         '<extra></extra>'
        )
        
        st.plotly_chart(fig_funnel, use_container_width=True)
    
    st.markdown('<div id="recomandari-campanie"></div>', unsafe_allow_html=True)
    st.markdown("### Recomandări Campanie")
    
    if campaign['radius_km'] <= 2:
        st.success("✅ **Campanie locală:** Raza de influență este mică (< 2 km). Recomandăm campanii la nivel de cartier: distribuție de flyere, parteneriate cu magazine locale, rețele sociale locale.")
    elif campaign['radius_km'] <= 5:
        st.warning("⚠️ **Campanie extinsă:** Raza de influență este medie (2-5 km). Recomandăm o combinație de campanii locale și digitale: Facebook/Google Ads geo-targetate, parteneriate cu centre comerciale, evenimente locale.")
    else:
        st.error("🔴 **Campanie amplă:** Raza de influență este mare (> 5 km). Recomandăm campanii digitale extinse: Google Ads, Facebook Ads, parteneriate cu clinici medicale, colaborări cu antrenori personali.")
    
    # Calcul cost estimativ campanie
    st.markdown('<div id="cost-campanie"></div>', unsafe_allow_html=True)
    st.markdown("### Estimare Cost Campanie")
    
    cost_per_person = st.number_input(
        "Cost per persoană atinsă (RON)",
        min_value=0.1,
        max_value=10.0,
        value=1.0,
        step=0.1,
        help="Costul estimat pentru a atinge o persoană prin campanie"
    )
    
    estimated_campaign_cost = campaign['people_to_reach'] * cost_per_person
    
    st.metric(
        "Cost Total Estimativ Campanie",
        f"{estimated_campaign_cost:,.0f} RON",
        help="Costul estimat pentru a atinge populația necesară"
    )
    
    # Secțiune Sondaj
    st.markdown("---")
    st.markdown('<div id="sondaj-cartier"></div>', unsafe_allow_html=True)
    st.markdown("### 📋 Sondaj în Cartier")
    
    st.markdown("""
    **De ce este necesar un sondaj?**
    
    Un sondaj în cartier vă permite să:
    - **Înțelegeți nevoile reale** ale potențialilor clienți din zonă
    - **Identificați preferințele** pentru program, servicii și prețuri
    - **Măsurați interesul** pentru diferite tipuri de abonamente
    - **Creați o bază de date** cu contacte pentru campanii viitoare
    - **Construiți relații** cu comunitatea locală înainte de deschidere
    
    **Când să realizați sondajul:**
    - Înainte de finalizarea planului de afaceri
    - În timpul pregătirii spațiului
    - Ca parte a campaniei de pre-lansare
    """)
    
    # Întrebări predefinite pentru sondaj
    st.markdown("#### Exemple de întrebări pentru sondaj")
    
    default_questions = [
        "Vârsta dumneavoastră?",
        "Locuiți în acest cartier?",
        "Aveți experiență cu săli de fitness?",
        "Ce tip de antrenament preferați? (forță, cardio, funcțional, recuperare)",
        "Ce oră a zilei preferați pentru antrenament?",
        "Cât ați fi dispus să plătiți pentru un abonament lunar?",
        "Ce servicii suplimentare vă interesează? (antrenor personal, nutriție, masaj)",
        "Cât de important este pentru dumneavoastră să aveți spațiu suficient și să nu stați la coadă?",
        "Ați fi interesat de o aplicație pentru rezervarea timpului de antrenament?",
        "Cum ați auzit despre noi? (recomandare, social media, flyer, altceva)"
    ]
    
    # Session state pentru întrebări
    if 'survey_questions' not in st.session_state:
        st.session_state.survey_questions = default_questions.copy()
    
    # Editor pentru întrebări
    st.markdown("#### ✏️ Editează întrebările pentru sondaj")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("💡 Puteți adăuga, edita sau șterge întrebări pentru a personaliza sondajul pentru cartierul dumneavoastră.")
    
    with col2:
        if st.button("🔄 Resetare la întrebări predefinite"):
            st.session_state.survey_questions = default_questions.copy()
            st.rerun()
    
    # Lista de întrebări editabile
    new_questions = []
    # Asigură-te că session_state este inițializat
    survey_questions = st.session_state.get('survey_questions', default_questions.copy())
    for i, question in enumerate(survey_questions):
        col1, col2 = st.columns([10, 1])
        with col1:
            edited_question = st.text_input(
                f"Întrebare {i+1}",
                value=question,
                key=f"question_{i}",
                label_visibility="collapsed"
            )
            if edited_question:
                new_questions.append(edited_question)
        with col2:
            if st.button("🗑️", key=f"delete_{i}", help="Șterge întrebarea"):
                if 'survey_questions' in st.session_state:
                    st.session_state.survey_questions.pop(i)
                st.rerun()
    
    # Actualizează lista dacă s-au făcut modificări
    if len(new_questions) == len(survey_questions):
        st.session_state.survey_questions = new_questions
    
    # Adaugă întrebare nouă
    st.markdown("#### ➕ Adaugă întrebare nouă")
    new_question = st.text_input(
        "Scrieți o întrebare nouă:",
        key="new_question_input",
        placeholder="Ex: Cât de des ați folosi sala? (zile pe săptămână)"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("➕ Adaugă", key="add_question"):
            if new_question and new_question.strip():
                st.session_state.survey_questions.append(new_question.strip())
                st.rerun()
    
    # Afișează întrebările finale
    final_questions = st.session_state.get('survey_questions', default_questions.copy())
    if final_questions:
        st.markdown("#### 📝 Lista finală de întrebări")
        st.markdown("**Total întrebări:** " + str(len(final_questions)))
        for i, q in enumerate(final_questions, 1):
            st.markdown(f"{i}. {q}")
    
    # Secțiune Concurs
    st.markdown("---")
    st.markdown('<div id="concurs-cartier"></div>', unsafe_allow_html=True)
    st.markdown("### 🏆 Concurs de Cartier")
    
    st.markdown("""
    **De ce un concurs de cartier?**
    
    Un concurs de cartier este o modalitate excelentă de:
    - **Creștere a vizibilității** brandului în comunitate
    - **Atragere a atenției** asupra deschiderii sălii
    - **Construire a relațiilor** cu locuitorii din zonă
    - **Generare de conținut** pentru social media
    - **Creare a unui sentiment de comunitate** în jurul sălii
    
    **Tipuri de concursuri recomandate:**
    """)
    
    st.markdown("""
    #### 🏃 Ture de Cartier (Semi-Maraton)
    - **Format:** Cursă pe distanțe variate (5km, 10km)
    - **Categorii pe vârstă:** 
      - Juniori (12-17 ani)
      - Tineri (18-35 ani)
      - Seniori (36-50 ani)
      - Veterani (50+ ani)
    - **Premii:** Abonamente gratuite (1, 3, 6 luni), trofee, produse locale
    - **Beneficii:** Vizibilitate maximă, participare masivă, conținut pentru social media
    
    #### ⚡ Sprinturi
    - **Format:** Competiții de viteză pe distanțe scurte (50m, 100m)
    - **Categorii pe vârstă:** Similar cu turele
    - **Premii:** Abonamente, produse sportive, vouchere
    - **Beneficii:** Accesibil pentru toate vârstele, distractiv, rapid
    
    #### 💪 Concurs de Forță
    - **Format:** Competiții pe categorii:
      - Deadlift (ridicare greutate)
      - Bench press (presă pe bancă)
      - Squat (genuflexiuni cu greutate)
    - **Categorii pe vârstă și greutate:**
      - Tineri (18-35): Lightweight, Middleweight, Heavyweight
      - Seniori (36-50): Lightweight, Middleweight, Heavyweight
      - Veterani (50+): Open category
    - **Premii:** Abonamente premium, echipament sportiv, trofee personalizate
    - **Beneficii:** Atrage entuziaștii fitness, demonstrează echipamentul sălii
    
    #### 🎯 Structură Recomandată pentru Premii
    """)
    
    prize_structure = pd.DataFrame({
        'Poziție': ['Locul 1', 'Locul 2', 'Locul 3', 'Locurile 4-10'],
        'Premiu': [
            'Abonament 6 luni + trofeu + produse locale',
            'Abonament 3 luni + medalie + produse locale',
            'Abonament 1 lună + medalie + produse locale',
            'Abonament 1 lună sau produse locale'
        ],
        'Valoare Estimată (RON)': ['~3000', '~1500', '~500', '~200-500']
    })
    
    st.dataframe(prize_structure, use_container_width=True, hide_index=True)
    
    st.markdown("""
    #### 💰 Estimare Costuri Concurs
    
    **Costuri potențiale:**
    - Organizare și logistică: 2,000 - 5,000 RON
    - Premii (abonamente, trofee, produse): 5,000 - 10,000 RON
    - Marketing și promovare: 1,000 - 3,000 RON
    - Permise/autorizații (dacă e necesar): 500 - 2,000 RON
    - **Total estimat:** 8,500 - 20,000 RON
    
    **ROI potențial:**
    - Vizibilitate în comunitate: **Fără preț**
    - Baza de date cu participanți: **200-500 contacte**
    - Abonamente generate direct: **20-50 abonamente noi**
    - Conținut social media: **Săptămâni de postări**
    """)
    
    st.markdown("""
    #### 📅 Calendar Recomandat
    
    1. **2-3 luni înainte de deschidere:** Anunț concurs
    2. **1-2 luni înainte:** Început înscrieri, campanie promoțională
    3. **2-3 săptămâni înainte:** Finalizare înscrieri, pregătiri finale
    4. **1 săptămână înainte de deschidere:** Desfășurare concurs
    5. **Ziua deschiderii:** Ceremonie de premiere, tururi ghidate ale sălii
    """)

with tab7:
    st.subheader("🏆 Analiză Concurențială & Poziționare Strategică")
    
    positioning = get_competitive_positioning()
    competitors = get_competitors_comparison()
    market_pos = calculate_market_position(analysis['total_clients'], CAPACITY_PER_HOUR)
    
    # Încarcă imaginea de fundal pentru cuprins
    # Încearcă mai întâi calea relativă (pentru Streamlit Cloud), apoi calea absolută (pentru local)
    background_image_path = None
    if os.path.exists("harta_sali.png"):
        background_image_path = "harta_sali.png"
    elif os.path.exists(r"C:\Users\D\Desktop\fundal_corect.png"):
        background_image_path = r"C:\Users\D\Desktop\fundal_corect.png"
    elif os.path.exists(r"C:\Users\D\Desktop\harta sali.png"):
        background_image_path = r"C:\Users\D\Desktop\harta sali.png"
    
    background_image_b64 = ""
    if background_image_path:
        try:
            with open(background_image_path, "rb") as img_file:
                background_image_b64 = base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            st.warning(f"Nu s-a putut încărca imaginea: {e}")
    
    # Cuprins interactiv cu scroll smooth și imagine de fundal
    st.markdown(f"""
    <style>
    .toc-container {{
        background-image: url('data:image/png;base64,{background_image_b64}');
        background-size: contain;
        background-position: center;
        background-repeat: no-repeat;
        background-color: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 30px;
        border: 2px solid #e0e0e0;
    }}
    .toc-container h3 {{
        margin-top: 0;
        color: #1f77b4;
        background: rgba(255, 255, 255, 0.85);
        padding: 10px 15px;
        border-radius: 5px;
        display: inline-block;
        font-weight: bold;
    }}
    .toc-container ul {{
        list-style-type: none;
        padding-left: 0;
        background: rgba(255, 255, 255, 0.85);
        padding: 15px;
        border-radius: 5px;
        margin-top: 15px;
    }}
    .toc-container li {{
        margin: 8px 0;
    }}
    .toc-container a {{
        text-decoration: none;
        color: #1f77b4;
        font-weight: 500;
        transition: color 0.2s ease;
    }}
    .toc-container a:hover {{
        color: #0d5a8a;
        text-decoration: underline;
    }}
    html {{
        scroll-behavior: smooth;
    }}
    </style>
    <div class="toc-container">
    <h3>📑 Cuprins</h3>
    <ul>
        <li><a href="#pozitionare-strategica">🎯 1. Poziționare Strategică</a></li>
        <li><a href="#capacitate-optima">📊 2. Capacitate Optimă</a></li>
        <li><a href="#comparare-concurenti">🏢 3. Comparare cu Concurenți</a></li>
        <li><a href="#pozitionare-piata">📈 4. Poziționare în Piață</a></li>
        <li><a href="#raza-influenta">🗺️ 5. Raza de Influență</a></li>
        <li><a href="#layout-comparativ">📐 6. Layout Comparativ (mp/om)</a></li>
        <li><a href="#layout-recomandat">🏗️ 7. Layout Recomandat</a></li>
        <li><a href="#simulare-redgym">🔮 8. Simulare RedGym Nouă Locație</a></li>
        <li><a href="#profitabilitate">💰 9. Profitabilitate</a></li>
        <li><a href="#analiza-completa-concurenti">🔍 10. Analiză Completă Concurenți</a></li>
        <li><a href="#analiza-social-media">📱 11. Analiză Social Media</a></li>
        <li><a href="#concluzie-strategica">📋 12. Concluzie Strategică</a></li>
        <li><a href="#recomandari">📌 13. Recomandări pentru Poziționare</a></li>
    </ul>
    </div>
    <script>
    document.querySelectorAll('.toc-container a').forEach(anchor => {{
        anchor.addEventListener('click', function (e) {{
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {{
                const offset = 80; // Offset pentru header-ul Streamlit
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - offset;
                window.scrollTo({{
                    top: offsetPosition,
                    behavior: 'smooth'
                }});
            }}
        }});
    }});
    </script>
    """, unsafe_allow_html=True)
    
    # Secțiune 1: Poziționare Strategică
    st.markdown('<div id="pozitionare-strategica"></div>', unsafe_allow_html=True)
    st.markdown("### 🎯 Poziționare Strategică")
    st.info(f"**{positioning['positioning']}**")
    
    # Imagini ilustrative pentru poziționare
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        display_image("images/instructor_copil.png", "Ghidare personalizată - Fără judecăți, cu suport", max_width=500)
    with col_img2:
        display_image("images/clase_copii.png", "Family-friendly - Clase pentru copii", max_width=500)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ Avantaje Competitive")
        for advantage in positioning['key_advantages']:
            st.write(f"• {advantage}")
    
    with col2:
        st.markdown("#### ❌ Ce NU Facem")
        for item in positioning['what_we_dont_do']:
            st.write(f"• {item}")
    
    # Public țintă (dacă există în positioning)
    if 'target_audience' in positioning:
        st.markdown("#### 🎯 Public Țintă - Entry-Point pentru Mișcare")
        st.success("""
        **Mobilis Vita se adresează:**
        """)
        for audience in positioning['target_audience']:
            st.write(f"• {audience}")
    
    # Prioritatea serviciilor (dacă există)
    if 'services_priority' in positioning:
        st.markdown("#### 📋 Prioritatea Serviciilor")
        services_priority = positioning['services_priority']
        st.info(f"""
        **Serviciu Principal:** {services_priority.get('primary', 'N/A')}
        
        **Servicii Secundare:** {services_priority.get('secondary', 'N/A')}
        
        **Serviciu Terțiar:** {services_priority.get('tertiary', 'N/A')}
        """)
    
    # Secțiune 2: Capacitate Optimă
    st.markdown('<div id="capacitate-optima"></div>', unsafe_allow_html=True)
    st.markdown("### 📊 Capacitate Optimă")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Capacitate Simultană", positioning['optimal_capacity']['simultaneous'])
    with col2:
        st.metric("Ocupare Lansare", positioning['optimal_capacity']['launch_occupancy'])
    with col3:
        st.metric("Ocupare Maturitate", positioning['optimal_capacity']['mature_occupancy'])
    with col4:
        st.metric("⚠️ Prag Avertisment", positioning['optimal_capacity']['warning_threshold'])
    
    st.warning(f"**Notă:** Depășirea constantă a pragului de {positioning['optimal_capacity']['warning_threshold']} afectează negativ experiența și retenția.")
    
    # Secțiune 3: Comparare cu Concurenți
    st.markdown('<div id="comparare-concurenti"></div>', unsafe_allow_html=True)
    st.markdown("### 🏢 Comparare cu Concurenți")
    
    # Grafic comparativ capacitate
    fig_capacity = go.Figure()
    
    colors_map = {'red': '#e74c3c', 'blue': '#3498db', 'green': '#2ecc71', 'purple': '#9b59b6'}
    
    for comp in competitors:
        fig_capacity.add_trace(go.Bar(
            x=[comp['name']],
            y=[comp['capacity']],
            name=comp['name'],
            marker_color=colors_map.get(comp['color'], '#95a5a6')
        ))
    
    # Adaugă noastre
    fig_capacity.add_trace(go.Bar(
        x=['Sala Noastră'],
        y=[CAPACITY_PER_HOUR],
        name='Sala Noastră',
        marker_color='#9b59b6'
    ))
    
    fig_capacity.update_layout(
        title="Comparare Capacitate Simultană",
        yaxis_title="Persoane",
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig_capacity, use_container_width=True)
    
    # Tabel detaliat
    display_df = pd.DataFrame({
        'Tip': [c['name'] for c in competitors] + ['Sala Noastră (Aleea Prieteniei)'],
        'Capacitate Simultană': [c['capacity'] for c in competitors] + [CAPACITY_PER_HOUR],
        'Abonați Activi': [c['members'] for c in competitors] + [analysis['total_clients']],
        'Model': [c['model'] for c in competitors] + [positioning['positioning']],
        'Limitări': [c['limitation'] for c in competitors] + ['N/A - Model optimizat']
    })
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Secțiune 4: Poziționare în Piață
    st.markdown('<div id="pozitionare-piata"></div>', unsafe_allow_html=True)
    st.markdown("### 📈 Poziționare în Piață")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Cota Piață - Capacitate",
            f"{market_pos['market_share_capacity_pct']:.1f}%",
            help="Cota noastră de piață bazată pe capacitate"
        )
        st.write(f"**Capacitate noastră:** {market_pos['our_capacity']} persoane")
        st.write(f"**Capacitate totală concurenți:** {market_pos['total_competitor_capacity']} persoane")
    
    with col2:
        st.metric(
            "Cota Piață - Membri",
            f"{market_pos['market_share_members_pct']:.1f}%",
            help="Cota noastră de piață bazată pe numărul de membri"
        )
        st.write(f"**Membri noștri:** {market_pos['our_members']}")
        st.write(f"**Membri totali concurenți:** {market_pos['total_competitor_members']}")
    
    st.success(f"💡 **{market_pos['positioning_note']}**")
    
    # Secțiune 5: Raza de Influență
    st.markdown('<div id="raza-influenta"></div>', unsafe_allow_html=True)
    st.markdown("### 🗺️ Raza de Influență")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Raza estimată:** {positioning['influence_radius']['estimated']}
        
        **Zonă primară (60% clienți):**
        - Primii 500-700m
        - Acces pietonal
        - Proximitate maximă
        
        **Zonă secundară (40% clienți):**
        - Prin recomandări
        - Retenție
        - Servicii specializate
        """)
    
    with col2:
        # Grafic distribuție pe zone
        zones_data = pd.DataFrame({
            'Zonă': ['Primară (500-700m)', 'Secundară (recomandări)'],
            'Procentaj Clienți': [60, 40]
        })
        
        fig_zones = px.pie(
            zones_data,
            values='Procentaj Clienți',
            names='Zonă',
            title="Distribuție Clienți pe Zone"
        )
        st.plotly_chart(fig_zones, use_container_width=True)
    
    # Secțiune 6: Layout Comparativ (mp/om)
    st.markdown('<div id="layout-comparativ"></div>', unsafe_allow_html=True)
    st.markdown("### 📐 Layout Comparativ (mp/om)")
    
    st.markdown("""
    **De ce contează mp/om?**
    
    În fitness, confortul perceput ≠ mp total, ci: **câți metri pătrați revin fiecărui utilizator simultan**
    
    - **Sub ~6 mp/om** → Aglomerație
    - **8–10 mp/om** → Acceptabil
    - **12+ mp/om** → Premium / Control
    """)
    
    # Input pentru suprafața noastră - Mobilis Vita
    st.info("""
    **Mobilis Vita - Structură Spațiu:**
    - **Sala de Fitness:** 65-70 mp (serviciu secundar)
    - **Sala de Clase:** 50 mp (serviciu principal)
    - **Total:** ~115-120 mp
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        fitness_area = st.number_input(
            "Sala de Fitness (mp)",
            min_value=60,
            max_value=75,
            value=67,
            step=1,
            help="Sala de fitness: 65-70 mp (serviciu secundar)",
            key="fitness_area_m2"
        )
    with col2:
        classes_area = st.number_input(
            "Sala de Clase (mp)",
            min_value=45,
            max_value=55,
            value=50,
            step=1,
            help="Sala de clase de mișcare: 50 mp (serviciu principal)",
            key="classes_area_m2"
        )
    
    our_area_m2 = fitness_area + classes_area
    
    layout_comparison = get_layout_comparison(our_area_m2, CAPACITY_PER_HOUR)
    layout_df = pd.DataFrame(layout_comparison)
    
    # Grafic mp/om
    fig_m2_per_person = go.Figure()
    
    colors_map = {'red': '#e74c3c', 'blue': '#3498db', 'green': '#2ecc71', 'purple': '#9b59b6'}
    
    for _, row in layout_df.iterrows():
        color = colors_map.get(row['Color'], '#95a5a6')
        fig_m2_per_person.add_trace(go.Bar(
            x=[row['Locație']],
            y=[row['mp/om']],
            name=row['Locație'],
            marker_color=color,
            text=f"{row['mp/om']} mp/om",
            textposition='auto'
        ))
    
    # Adaugă linii de prag
    fig_m2_per_person.add_hline(y=6, line_dash="dash", line_color="red", 
                                annotation_text="Prag aglomerație (<6 mp/om)")
    fig_m2_per_person.add_hline(y=8, line_dash="dash", line_color="orange", 
                                annotation_text="Prag acceptabil (8 mp/om)")
    fig_m2_per_person.add_hline(y=12, line_dash="dash", line_color="green", 
                                annotation_text="Prag premium (12+ mp/om)")
    
    fig_m2_per_person.update_layout(
        title="Comparare mp/om - Confort per Locație",
        yaxis_title="mp/om",
        xaxis_title="Locație",
        showlegend=False,
        height=500
    )
    st.plotly_chart(fig_m2_per_person, use_container_width=True)
    
    # Tabel detaliat
    st.dataframe(
        layout_df[['Locație', 'Suprafață (mp)', 'Oameni Simultan', 'mp/om', 'Experiență']],
        use_container_width=True,
        hide_index=True
    )
    
    # Insight critic
    st.info("""
    🔑 **Insight critic:**
    
    Toate sălile mari din Bacău sunt sub pragul de confort la orele dorite de oameni.
    
    👉 Tu NU trebuie să spui: "avem aparate noi"
    
    👉 Tu spui: "nu stai la coadă"
    """)
    
    # Secțiune 7: Layout Recomandat
    st.markdown('<div id="layout-recomandat"></div>', unsafe_allow_html=True)
    st.markdown("### 🏗️ Layout Recomandat pentru Sala Noastră")
    
    layout_recommended = get_recommended_layout()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Suprafață totală:** {layout_recommended['total_area_m2']} mp")
        st.markdown(f"**Sala Fitness:** {layout_recommended.get('fitness_area_m2', 'N/A')} mp")
        st.markdown(f"**Sala Clase:** {layout_recommended.get('classes_area_m2', 'N/A')} mp")
        
        # Capacitate țintă - structură nouă pentru Mobilis Vita
        target_capacity = layout_recommended.get('target_capacity', {})
        if 'total_simultaneous' in target_capacity:
            total_cap = target_capacity['total_simultaneous']
            st.markdown(f"**Capacitate țintă totală:** {total_cap.get('min', 'N/A')}-{total_cap.get('max', 'N/A')} persoane (optimal: {total_cap.get('optimal', 'N/A')})")
            if 'fitness_simultaneous' in target_capacity:
                fitness_cap = target_capacity['fitness_simultaneous']
                st.markdown(f"  - Sala Fitness: {fitness_cap.get('min', 'N/A')}-{fitness_cap.get('max', 'N/A')} persoane")
            if 'classes_simultaneous' in target_capacity:
                classes_cap = target_capacity['classes_simultaneous']
                st.markdown(f"  - Sala Clase: {classes_cap.get('min', 'N/A')}-{classes_cap.get('max', 'N/A')} persoane")
        else:
            # Fallback pentru structura veche (dacă există)
            if 'min' in target_capacity and 'max' in target_capacity:
                st.markdown(f"**Capacitate țintă:** {target_capacity['min']}-{target_capacity['max']} persoane")
        
        # mp/om țintă
        m2_per_person = layout_recommended.get('m2_per_person_range', {})
        if 'overall' in m2_per_person:
            overall = m2_per_person['overall']
            st.markdown(f"**mp/om țintă (overall):** {overall.get('min', 'N/A')}-{overall.get('max', 'N/A')} mp/om (optimal: {overall.get('optimal', 'N/A')})")
        elif 'min' in m2_per_person and 'max' in m2_per_person:
            st.markdown(f"**mp/om țintă:** {m2_per_person['min']}-{m2_per_person['max']} mp/om")
    
    with col2:
        # Grafic distribuție spațiu
        layout_dist_data = []
        for key, value in layout_recommended['distribution'].items():
            layout_dist_data.append({
                'Zonă': value['description'],
                'Procentaj': value['percentage'],
                'Suprafață (mp)': value['m2']
            })
        
        layout_dist_df = pd.DataFrame(layout_dist_data)
        
        fig_layout = px.pie(
            layout_dist_df,
            values='Suprafață (mp)',
            names='Zonă',
            title="Distribuție Spațiu Recomandată",
            hover_data=['Procentaj']
        )
        st.plotly_chart(fig_layout, use_container_width=True)
    
    # Tabel detaliat layout
    layout_detail_df = pd.DataFrame({
        'Zonă': [v['description'] for v in layout_recommended['distribution'].values()],
        'Procentaj': [f"{v['percentage']}%" for v in layout_recommended['distribution'].values()],
        'Suprafață (mp)': [v['m2'] for v in layout_recommended['distribution'].values()]
    })
    st.dataframe(layout_detail_df, use_container_width=True, hide_index=True)
    
    st.success("""
    ➡️ **Rezultat:** Flux aerisit + senzație de spațiu > realitatea fizică
    """)
    
    # Secțiune 8: Simulare RedGym Nouă Locație
    st.markdown('<div id="simulare-redgym"></div>', unsafe_allow_html=True)
    st.markdown("### 🔮 Simulare: Ce se întâmplă dacă RedGym deschide o nouă locație?")
    
    simulation = simulate_new_redgym_impact()
    
    st.markdown(f"**Scenariu:** {simulation['scenario']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ❌ Ce NU se întâmplă")
        for item in simulation['what_doesnt_happen']:
            st.write(f"• {item}")
    
    with col2:
        st.markdown("#### ✅ Ce SE întâmplă în realitate")
        
        st.markdown(f"**{simulation['what_happens']['effect_1_fragmentation']['title']}**")
        st.write(simulation['what_happens']['effect_1_fragmentation']['description'])
        for detail in simulation['what_happens']['effect_1_fragmentation']['details']:
            st.write(f"  - {detail}")
        
        st.markdown(f"**{simulation['what_happens']['effect_2_education']['title']}**")
        st.write(simulation['what_happens']['effect_2_education']['description'])
        for detail in simulation['what_happens']['effect_2_education']['details']:
            st.write(f"  - {detail}")
    
    # Tabel impact
    impact_df = pd.DataFrame({
        'Indicator': ['Cerere totală fitness zonă', 'Presiune pe volum', 'Avantajul tău'],
        'Fără nou RedGym': [
            simulation['impact_estimates']['without_new_redgym']['total_demand'],
            simulation['impact_estimates']['without_new_redgym']['volume_pressure'],
            simulation['impact_estimates']['without_new_redgym']['our_advantage']
        ],
        'Cu nou RedGym': [
            simulation['impact_estimates']['with_new_redgym']['total_demand'],
            simulation['impact_estimates']['with_new_redgym']['volume_pressure'],
            simulation['impact_estimates']['with_new_redgym']['our_advantage']
        ]
    })
    st.dataframe(impact_df, use_container_width=True, hide_index=True)
    
    st.warning(f"🔑 **Paradox:** {simulation['paradox']}")
    
    # Secțiune 9: Profitabilitate (Profit/abonat vs Profit/mp)
    st.markdown('<div id="profitabilitate"></div>', unsafe_allow_html=True)
    st.markdown("### 💰 Profitabilitate: Profit/Abonat vs Profit/mp")
    
    st.markdown("""
    Aici se face diferența între **"sală plină"** și **"sală sănătoasă"**.
    """)
    
    profitability = calculate_profitability_comparison(
        analysis['revenue']['total'],
        analysis['total_clients'],
        our_area_m2
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏢 Sală Mare (RedGym / CityGym)")
        st.write(f"**Abonați:** {profitability['big_gym']['members']}")
        st.write(f"**Preț mediu:** {profitability['big_gym']['avg_price']} RON")
        st.write(f"**Venit lunar:** {profitability['big_gym']['monthly_revenue']:,.0f} RON")
        st.write(f"**Suprafață:** {profitability['big_gym']['area_m2']} mp")
        st.write(f"**Venit/mp:** {profitability['big_gym']['revenue_per_m2']:.2f} RON/mp")
    
    with col2:
        st.markdown("#### 🏋️ Sala Noastră (Model Controlat)")
        st.write(f"**Abonați:** {profitability['our_gym']['members']}")
        st.write(f"**Preț mediu:** {profitability['our_gym']['avg_price']} RON")
        st.write(f"**Venit lunar:** {profitability['our_gym']['monthly_revenue']:,.0f} RON")
        st.write(f"**Suprafață:** {profitability['our_gym']['area_m2']} mp")
        st.write(f"**Venit/mp:** {profitability['our_gym']['revenue_per_m2']:.2f} RON/mp")
    
    # Comparație profitabilitate
    st.markdown("#### 📊 Comparație Profitabilitate Reală")
    
    comparison_data = []
    for key, value in profitability['comparison'].items():
        comparison_data.append({
            'Indicator': key.replace('_', ' ').title(),
            'Sală Mare': value['big_gym'],
            'Sala Noastră': value['our_gym'],
            'Notă': value['note']
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # Concluzie investitor
    st.markdown("#### 🔑 Concluzia de Investitor")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**NU câștigi prin:**")
        for item in profitability['conclusion']['dont_win_by']:
            st.write(f"• {item}")
    
    with col2:
        st.markdown("**CÂȘTIGI prin:**")
        for item in profitability['conclusion']['win_by']:
            st.write(f"• {item}")
    
    st.markdown("---")
    
    # Secțiune 10: Analiză Completă Concurenți
    st.markdown('<div id="analiza-completa-concurenti"></div>', unsafe_allow_html=True)
    st.markdown("### 🔍 Analiză Completă Concurenți - Piața din Bacău")
    
    st.markdown("""
    Această secțiune oferă o analiză detaliată a tuturor concurenților din zonă, organizați pe categorii:
    - **Săli de Fitness** - Săli tradiționale de fitness și bodybuilding
    - **Săli de Kineto / Reabilitare** - Centre specializate pe recuperare medicală
    - **Cabinete de Masaj** - Servicii de wellness și relaxare
    - **Săli cu Clase de Mișcare și Terapii** - Pilates, yoga, terapii alternative, clase pentru copii
    """)
    
    # Selector de categorie
    all_competitors_data = get_all_extended_competitors()
    category_names = {
        'fitness': '🏋️ Săli de Fitness',
        'kineto': '🏥 Săli de Kineto / Reabilitare',
        'masaj': '💆 Cabinete de Masaj',
        'terapii': '🧘 Clase de Mișcare și Terapii'
    }
    
    # Label cu font mai mare
    st.markdown("""
    <div style="font-size: 1.2em; font-weight: 500; margin-bottom: 10px; color: #333;">
        Selectează categoria pentru analiză detaliată:
    </div>
    """, unsafe_allow_html=True)
    
    selected_category = st.selectbox(
        "",
        options=list(category_names.keys()),
        format_func=lambda x: category_names[x],
        key="competitor_category_selector",
        label_visibility="collapsed"
    )
    
    competitors_in_category = get_competitors_by_category(selected_category)
    
    if competitors_in_category:
        st.markdown(f"#### {category_names[selected_category]}")
        
        for idx, competitor in enumerate(competitors_in_category):
            with st.expander(f"**{competitor['name']}** - {competitor.get('positioning', 'N/A')}", expanded=(idx == 0)):
                # Locații
                st.markdown("##### 📍 Locații")
                locations_df = pd.DataFrame([
                    {
                        'Nume Locație': loc['name'],
                        'Adresă': loc.get('address', 'N/A'),
                        'Suprafață (mp)': loc.get('area_m2', 0),
                        'Capacitate Simultană': loc.get('capacity_simultaneous', 0)
                    }
                    for loc in competitor.get('locations', [])
                ])
                st.dataframe(locations_df, use_container_width=True, hide_index=True)
                
                # Prețuri
                st.markdown("##### 💰 Prețuri Practicate")
                prices = competitor.get('prices', {})
                if prices:
                    prices_list = []
                    for key, value in prices.items():
                        if isinstance(value, bool):
                            if value:
                                prices_list.append(f"**{key.replace('_', ' ').title()}**: Disponibil")
                        else:
                            prices_list.append(f"**{key.replace('_', ' ').title()}**: {value} RON")
                    st.markdown("\n".join([f"- {p}" for p in prices_list]))
                
                # Servicii
                st.markdown("##### 🎯 Servicii Oferite")
                services = competitor.get('services', [])
                if services:
                    st.markdown("\n".join([f"- {s}" for s in services]))
                
                # Poziționare
                st.markdown("##### 📊 Poziționare")
                st.info(competitor.get('positioning', 'N/A'))
                
                # Clienți
                st.markdown("##### 👥 Detalii Clienți")
                clients_info = competitor.get('clients', {})
                if clients_info:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Membri/Clienți", clients_info.get('total_members', 'N/A'))
                        st.write(f"**Tipologie:** {clients_info.get('typology', 'N/A')}")
                    with col2:
                        st.write(f"**Ore de vârf:** {clients_info.get('peak_hours', 'N/A')}")
                        st.write(f"**Rata de retenție:** {clients_info.get('retention_rate', 'N/A')}")
                
                # Antrenori/Terapeuți
                trainers_key = 'trainers' if 'trainers' in competitor else 'therapists' if 'therapists' in competitor else 'instructors'
                trainers = competitor.get(trainers_key, [])
                if trainers:
                    st.markdown(f"##### 👨‍🏫 {'Antrenori' if trainers_key == 'trainers' else 'Terapeuți' if trainers_key == 'therapists' else 'Instructori'}")
                    trainers_df = pd.DataFrame([
                        {
                            'Nume': t.get('name', 'N/A'),
                            'Specializare': t.get('specialization', 'N/A'),
                            'Instagram': t.get('instagram', 'N/A') if t.get('instagram') else 'N/A'
                        }
                        for t in trainers
                    ])
                    st.dataframe(trainers_df, use_container_width=True, hide_index=True)
    
    # Secțiune 11: Analiză Social Media
    st.markdown('<div id="analiza-social-media"></div>', unsafe_allow_html=True)
    st.markdown("### 📱 Analiză Social Media - Prezența Concurenților pe Instagram")
    
    social_summary = get_social_media_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Followers (toți concurenții)", f"{social_summary['total_followers']:,}")
    with col2:
        st.metric("Concurenți cu Instagram", social_summary['total_competitors_with_instagram'])
    with col3:
        st.metric("Engagement Rate Mediu", f"{social_summary.get('avg_engagement_rate', 0):.2f}%")
    with col4:
        st.metric("Postări/Săptămână (medie)", f"{social_summary.get('avg_posts_per_week', 0):.1f}")
    
    # Analiză detaliată pe categorii
    st.markdown("#### 📊 Analiză pe Categorii")
    
    category_social_data = []
    for category, cat_data in social_summary.get('by_category', {}).items():
        if cat_data['competitors_count'] > 0:
            category_social_data.append({
                'Categorie': category_names.get(category, category),
                'Total Followers': cat_data['total_followers'],
                'Număr Concurenți': cat_data['competitors_count'],
                'Engagement Rate Mediu (%)': round(cat_data.get('avg_engagement', 0), 2),
                'Postări/Săptămână (medie)': round(cat_data.get('avg_posts', 0), 1)
            })
    
    if category_social_data:
        category_social_df = pd.DataFrame(category_social_data)
        st.dataframe(category_social_df, use_container_width=True, hide_index=True)
    
    # Analiză detaliată pentru fiecare competitor
    st.markdown("#### 🔍 Analiză Detaliată per Competitor")
    
    all_competitors = []
    for category, competitors in all_competitors_data.items():
        for comp in competitors:
            social = comp.get('social_media', {}).get('instagram', {})
            if social:
                all_competitors.append({
                    'Competitor': comp['name'],
                    'Categorie': category_names.get(category, category),
                    'Instagram Handle': social.get('handle', 'N/A'),
                    'Followers': social.get('followers', 0),
                    'Postări/Săptămână': social.get('posts_per_week', 0),
                    'Engagement Rate (%)': social.get('engagement_rate', 0),
                    'Tipuri de Conținut': ', '.join(social.get('content_types', []))
                })
    
    if all_competitors:
        competitors_social_df = pd.DataFrame(all_competitors)
        competitors_social_df = competitors_social_df.sort_values('Followers', ascending=False)
        st.dataframe(competitors_social_df, use_container_width=True, hide_index=True)
        
        # Grafic comparativ followers
        fig_followers = px.bar(
            competitors_social_df,
            x='Competitor',
            y='Followers',
            color='Categorie',
            title='Număr de Followers pe Instagram - Comparație',
            labels={'Followers': 'Număr Followers', 'Competitor': 'Competitor'}
        )
        fig_followers.update_layout(height=500, xaxis_tickangle=-45)
        st.plotly_chart(fig_followers, use_container_width=True)
        
        # Grafic engagement rate
        fig_engagement = px.bar(
            competitors_social_df,
            x='Competitor',
            y='Engagement Rate (%)',
            color='Categorie',
            title='Engagement Rate pe Instagram - Comparație',
            labels={'Engagement Rate (%)': 'Engagement Rate (%)', 'Competitor': 'Competitor'}
        )
        fig_engagement.update_layout(height=500, xaxis_tickangle=-45)
        st.plotly_chart(fig_engagement, use_container_width=True)
    
    # Postări populare
    st.markdown("#### ⭐ Cele Mai Populare Postări")
    
    for category, competitors in all_competitors_data.items():
        for comp in competitors:
            social = comp.get('social_media', {}).get('instagram', {})
            top_posts = social.get('top_posts', [])
            if top_posts:
                with st.expander(f"**{comp['name']}** - Top {len(top_posts)} Postări"):
                    for idx, post in enumerate(top_posts, 1):
                        st.markdown(f"""
                        **#{idx}** - {post.get('description', 'N/A')}
                        - 👍 {post.get('likes', 0)} like-uri
                        - 💬 {post.get('comments', 0)} comentarii
                        """)
    
    st.markdown("---")
    st.markdown('<div id="concluzie-strategica"></div>', unsafe_allow_html=True)
    st.markdown("""
    **Concluzie Strategică:**
    
    Analiza per locație confirmă că majoritatea sălilor mari din zonă funcționează constant la sau peste limita optimă de confort. 
    Noua sală nu concurează cu acestea pe volum sau preț, ci ocupă un gol clar de piață, definit de control, calitate și proximitate.
    
    **Insights din Analiza Completă:**
    - Piața din Bacău este foarte diversificată, de la săli mari de fitness până la centre specializate pe terapii alternative
    - Există o oportunitate clară de a combina servicii de fitness cu servicii de recuperare și wellness
    - Prezența pe social media variază semnificativ între concurenți, oferind oportunități de diferențiere
    - Engagement-ul pe Instagram este mai ridicat pentru centrele specializate (yoga, pilates, terapii) decât pentru sălile mari de fitness
    """)
    
    # Secțiune 11: Recomandări
    st.markdown('<div id="recomandari"></div>', unsafe_allow_html=True)
    st.markdown("### 📌 Recomandări pentru Poziționarea Mobilis Vita")
    st.markdown("""
    **Locație țintă:** Strada Prieteniei nr 14, Bacău
    
    **Model:** Entry-point pentru mișcare, family-friendly, nu pentru pasionați de fitness
    
    Iată recomandări concrete bazate pe feedback-ul clientului:
    """)
    
    # 1. Poziționare strategică corectă
    st.markdown("#### 🎯 1. Poziționare Strategică Corectă")
    st.warning("""
    **EROARE CORECTATĂ:** Poziționarea inițială era greșită!
    
    **NU ne adresăm:**
    - ❌ Pasionaților de fitness
    - ❌ Celor cu experiență avansată
    - ❌ Persoanelor care caută performanță
    
    **DA, ne adresăm:**
    - ✅ Oamenilor care încep mișcarea (de la 0)
    - ✅ Oamenilor care revin la mișcare după pauză
    - ✅ Familiilor cu copii (family-friendly)
    - ✅ Mămici care caută activități pentru ele și copii
    - ✅ Bunici care doresc mișcare blândă
    - ✅ Persoanelor care nu se simt confortabile în săli tradiționale
    """)
    
    # Imagini ilustrative pentru poziționare
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        display_image("images/clase_toate_varstele.png", "Inclusivitate - Toate vârstele sunt binevenite", max_width=500)
    with col_img2:
        display_image("images/grup_miscare.png", "Comunitate - Mișcare împreună", max_width=500)
    
    # 2. Capacitate și spațiu
    st.markdown("#### 📐 2. Capacitate și spațiu - Dimensiuni Reale")
    st.markdown("""
    **Structură reală a spațiului:**
    - **Sala de Fitness:** 65-70 mp (serviciu secundar)
    - **Sala de Clase:** 50 mp (serviciu principal)
    - **Total:** ~115-120 mp
    
    **Capacitate simultană:**
    - **Sala fitness:** 8-12 persoane (pentru confort și abordare personalizată)
    - **Sala clase:** 8-15 persoane (pentru clase de mișcare)
    - **Total simultan:** 10-15 persoane (pentru a menține confortul psihic pentru începători)
    
    💡 **Recomandare:** Menține raportul **9-12 mp/utilizator** pentru a garanta spațiul sigur, fără presiune, ideal pentru entry-point.
    """)
    
    # 3. Structura serviciilor (prioritizată)
    st.markdown("#### 💡 3. Structura Serviciilor - Prioritate Corectă")
    st.markdown("""
    **SERVICIU PRINCIPAL: Clase de Mișcare (50 mp)**
    - Clase de mișcare pentru începători
    - Clase family-friendly (copii, mămici, bunici)
    - Clase de integrare mișcare în viață pentru sănătate
    - Abordare fără judecăți, ghidare de la 0
    
    **SERVICII SECUNDARE:**
    - **Masaj:** 100 RON/sesiune - relaxare și wellness
    - **Kineto/Reabilitare:** 120 RON/sesiune - recuperare medicală
    
    **SERVICIU TERȚIAR: Acces Sala Fitness (65-70 mp)**
    - Acces la echipamente fitness (serviciu secundar)
    - Nu este focus-ul principal
    - Pentru cei care doresc să completeze clasele cu fitness
    
    **Abonamente:**
    - **Clase de Mișcare:** 180 RON/lună (serviciu principal)
    - **Acces Sala Fitness:** 120 RON/lună (serviciu secundar)
    - **Abonament Complet:** 250 RON/lună (clase + fitness)
    - **Abonament Family:** 400 RON/lună (pentru 2-3 persoane)
    """)
    
    # 4. Prețuri orientative de piață
    st.markdown("#### 💰 4. Prețuri Orientative de Piață")
    st.markdown("""
    **Abonamente:**
    - **Clase de Mișcare:** 180 RON/lună (serviciu principal)
    - **Acces Sala Fitness:** 120 RON/lună (serviciu secundar)
    - **Abonament Complet:** 250 RON/lună
    - **Abonament Family:** 400 RON/lună (2-3 persoane)
    
    **Servicii per sesiune:**
    - **Masaj:** 100 RON/sesiune
    - **Kineto/Reabilitare:** 120 RON/sesiune
    """)
    
    # 5. Target corect
    st.markdown("#### 📍 5. Target Corect - Entry-Point")
    st.markdown("""
    **Public țintă principal:**
    - **Oameni care încep mișcarea (de la 0)** – entry-point, fără judecăți
    - **Oameni care revin la mișcare după pauză** – ghidare și suport
    - **Familii cu copii** – family-friendly, activități pentru toată familia
    - **Mămici** – activități pentru ele și copii
    - **Bunici** – mișcare blândă, adaptată vârstei
    - **Persoane care nu se simt confortabile în săli tradiționale** – spațiu sigur
    
    **Mesaj cheie:** "Nu te simți judecat, ci ghidat să integrezi mișcarea în viață pentru sănătate"
    """)
    
    # 6. Aplicație de Booking - Adaptată pentru Model Entry-Point
    st.markdown("#### 📱 6. Aplicație de Booking – Garantarea Spațiului și Confortului Psihic")
    st.markdown("""
    **De ce este esențială o aplicație de booking pentru modelul entry-point?**
    
    Pentru modelul **Mobilis Vita** (entry-point, family-friendly), aplicația de booking este **chiar mai importantă** decât pentru sălile tradiționale:
    
    ✅ **Garantează spațiu sigur** – Clienții (începători) văd că nu vor fi surprinși de aglomerație (intimidant pentru entry-point)
    
    ✅ **Rezervare clase de mișcare** – Clienții pot rezerva locuri la clase (serviciul principal), garantând accesul
    
    ✅ **Rezervare sala fitness** – Pentru cei care doresc să completeze cu fitness (serviciu secundar)
    
    ✅ **Rezervare masaj/kineto** – Pentru serviciile terapeutice
    
    ✅ **Family-friendly** – Părinții pot rezerva pentru ei și copii simultan
    
    ✅ **Previne aglomerația psihică** – Pentru începători, aglomerația este mai intimidantă decât pentru pasionați
    
    ✅ **Creează încredere** – Clienții știu că vor avea spațiu și nu se vor simți judecați sau stânjeniți
    
    **Funcționalități recomandate pentru aplicație (model entry-point):**
    
    - **Rezervare clase de mișcare** (serviciu principal) – programul săptămânal de clase
    - **Rezervare sala fitness** (serviciu secundar) – pe intervale orare, limitat la 8-12 persoane
    - **Rezervare masaj/kineto** – programare directă cu terapeuți
    - **Rezervare family** – părinți pot rezerva pentru ei și copii
    - **Vizualizare disponibilitate în timp real** – câți oameni sunt deja în sală/clasă
    - **Limitare automată** – sistemul previne aglomerația (critic pentru entry-point)
    - **Notificări prietenoase** – amintiri blânde, nu presiuni
    - **Istoric progres** – pentru începători, să vadă progresul (motivație)
    - **Integrare abonamente** – doar membrii activi pot rezerva
    
    **Impact asupra modelului de business (entry-point):**
    
    - **Retenție foarte crescută** – Începătorii apreciază predictibilitatea și siguranța spațiului
    - **Diferențiere clară** – "Spațiu sigur, fără judecăți" devine verificabil
    - **Comfort psihic** – Reduce anxietatea pentru începători (critic pentru entry-point)
    - **Family-friendly** – Facilitează participarea familiilor
    - **Optimizare capacitate** – Distribuie utilizatorii pentru a menține confortul psihic
    """)
    
    # Concluzie rapidă - Actualizată
    st.markdown("#### 📌 Concluzie Rapidă - Mobilis Vita")
    st.markdown("""
    👉 **Piața din Bacău este foarte diversificată:** de la săli mari de fitness până la centre specializate pe terapii.
    
    👉 **Mobilis Vita ocupă un gol clar de piață:**
    - **Entry-point pentru mișcare** – nu pentru pasionați, ci pentru începători
    - **Family-friendly** – copii, mămici, bunici bineveniți
    - **Fără judecăți** – oamenii vin pentru că nu se simt judecați, ci ghidați
    - **Clase de mișcare ca serviciu principal** (50 mp)
    - **Fitness ca serviciu secundar** (65-70 mp)
    - **Servicii terapeutice:** masaj, kineto
    
    👉 **Propunerea de valoare:**
    - "Spațiu sigur pentru a începe sau reveni la mișcare"
    - "Fără judecăți, cu ghidare de la 0"
    - "Family-friendly: pentru toată familia"
    - "Integrare mișcare în viață pentru sănătate"
    
    👉 **Aplicația de booking este esențială** pentru a garanta confortul psihic al începătorilor și a diferenția modelul entry-point.
    """)

# Tab 8: Scopul și Arhitectura Dashboard
with tab8:
    st.markdown("""
    # 📘 Scopul și Arhitectura Dashboard
    ## Analiză Potențial Spațiu Fitness & Recuperare - Bacau
    
    ---
    """)
    
    # Cuprins pentru tab Scopul și Arhitectura Dashboard
    toc_items = [
        ("scop-proiect", "🎯 Scopul Proiectului"),
        ("model-gandire", "🧠 Modelul de Gândire"),
        ("abordare-top-down", "📊 Abordarea Top-Down"),
        ("principii-baza", "📐 Principiile de Bază"),
        ("logica-calcul", "🔢 Logica de Calcul"),
        ("explicatie-rate", "📊 Explicația Detaliată a Ratelor"),
        ("model-geografic", "🗺️ Modelul Geografic"),
        ("structura-dashboard", "📊 Structura Dashboard-ului"),
        ("design-decisions", "🎨 Design Decisions"),
        ("flux-date", "🔄 Fluxul de Date"),
        ("insights-cheie", "💡 Insights Cheie"),
        ("utilizare-dashboard", "🎯 Utilizarea Dashboard-ului"),
        ("concluzii", "📝 Concluzii"),
        ("invataminte", "🎓 Învățăminte")
    ]
    st.markdown(create_table_of_contents("📑 Cuprins", toc_items), unsafe_allow_html=True)
    
    st.markdown('<div id="scop-proiect"></div>', unsafe_allow_html=True)
    st.markdown("""
    ## 🎯 Scopul Proiectului
    
    Acest dashboard a fost creat pentru a analiza potențialul unui spațiu de fitness și recuperare post-operatorie în Bacau, Aleea Prieteniei nr 14. 
    Obiectivul principal este de a răspunde la întrebări critice pentru o decizie de investiție:
    
    - **Cât venit pot genera?**
    - **Câți clienți am nevoie?**
    - **Cât de mare trebuie să fie zona de acoperire?**
    - **Ce tip de campanie de marketing trebuie să fac?**
    """)
    
    st.markdown("---")
    
    st.markdown('<div id="model-gandire"></div>', unsafe_allow_html=True)
    st.markdown("""
    ## 🧠 Modelul de Gândire
    
    <div id="abordare-top-down"></div>
    ### 1. Abordarea "De Sus în Jos" (Top-Down)
    
    Am pornit de la **obiectivul final** (venit dorit: 50,000 RON/lună) și am construit modelul înapoi pentru a determina ce este necesar:
    
    ```
    Venit Dorit (50,000 RON/lună)
        ↓
    Câți clienți sunt necesari?
        ↓
    Ce distribuție de abonamente?
        ↓
    Câtă ocupare a spațiului?
        ↓
    Câtă populație trebuie să acopăr?
        ↓
    Cât de mare trebuie să fie raza de influență?
    ```
    """)
    
    st.markdown("---")
    
    st.markdown('<div id="principii-baza"></div>', unsafe_allow_html=True)
    st.markdown("""
    ### 2. Principiile de Bază
    
    #### A. Capacitatea Spațiului
    - **Capacitate per oră**: 20 oameni
    - **Program**: 10 ore/zi × 7 zile/săptămână
    - **Capacitate maximă lunară**: ~6,062 slot-uri
    
    **De ce?** 
    - Trebuie să știm cât de mult poate produce spațiul
    - Fiecare "slot" reprezintă o oră de utilizare a spațiului
    - Aceasta este baza pentru toate calculele
    """)
    
    st.markdown("---")
    
    st.markdown("""
    #### B. Scenariile de Ocupare
    Am definit 3 scenarii pentru a acoperi diferite realități:
    
    1. **Redus (25-50%)**: Realist pentru primele luni
    2. **Mediu (50-75%)**: Realist după stabilizare
    3. **Ridicat (>75%)**: Optimist, necesită timp și marketing puternic
    
    **De ce scenarii?**
    - Nu putem prezice exact viitorul
    - Trebuie să vedem mai multe opțiuni
    - Fiecare scenariu are implicații diferite pentru marketing și investiții
    """)
    
    st.markdown("---")
    
    st.markdown("""
    #### C. Dimensionarea Spațiului – Indicatorul mp / Utilizator
    
    **Mobilis Vita - Model Entry-Point pentru Mișcare:**
    
    Spațiul este structurat în două zone principale:
    - **Sala de Clase de Mișcare:** 50 mp (SERVICIU PRINCIPAL)
    - **Sala de Fitness:** 65-70 mp (serviciu secundar)
    - **Total:** ~115-120 mp
    
    **Model de Business:**
    - **NU** pentru pasionați de fitness sau cei cu experiență avansată
    - **DA** pentru oameni care încep sau revin la mișcare (entry-point)
    - **Family-friendly:** copii, mămici, bunici bineveniți
    - **Fără judecăți:** oamenii vin pentru că nu se simt judecați, ci ghidați
    - **Integrare mișcare în viață:** pentru sănătate, nu pentru performanță
    
    **Ipoteze concrete:**
    - Suprafață totală: ~117.5 mp (67.5 mp fitness + 50 mp clase)
    - Utilizatori simultan: 10-15 persoane (interval țintă pentru confort)
    - Calcul: 117.5 mp / 12 utilizatori = **~9.8 mp/utilizator**
    
    **Formula de calcul:**
    ```
    mp/utilizator = Suprafață totală (mp) / Număr utilizatori simultan
    ```
    
    **Praguri de interpretare pentru modelul entry-point:**
    - **Sub 6 mp/utilizator**: Prea aglomerat pentru entry-point (intimidant)
    - **6-9 mp/utilizator**: Acceptabil pentru începători (confort psihic)
    - **9-12 mp/utilizator**: Ideal pentru entry-point (spațiu sigur, fără presiune)
    - **Peste 12 mp/utilizator**: Spațiu generos, dar potențial subutilizat
    
    **Legătura cu ocuparea țintă (60-70%):**
    - La ocupare 60-70%, cu 10-12 utilizatori simultan, raportul mp/utilizator rămâne în intervalul 9-12 mp
    - Ocupare peste 80% reduce raportul sub 9 mp/utilizator, afectând confortul psihic (intimidant pentru începători)
    - Ocupare sub 50% crește raportul peste 12 mp/utilizator, indicând subutilizare
    
    **Impact asupra retenției clienților (model entry-point):**
    - Raport sub 6 mp/utilizator: Risc foarte crescut de abandon (intimidant pentru începători)
    - Raport 9-12 mp/utilizator: Retenție optimă (spațiu sigur, fără presiune, confort psihic)
    - Raport peste 12 mp/utilizator: Retenție bună, dar eficiență economică redusă
    
    **Diferențierea față de sălile tradiționale:**
    - Săli mari (RedGym, CityGym): 4-6 mp/utilizator, focus pe pasionați de fitness
    - Mobilis Vita (model entry-point): 9-12 mp/utilizator, focus pe începători și familii
    - Avantaj competitiv: "Spațiu sigur, fără judecăți" vs "Avem aparate noi"
    """)
    
    st.markdown("---")
    
    st.markdown("""
    #### D. Tipurile de Abonamente
    
    Am creat 4 tipuri care acoperă diferite segmente de piață:
    
    1. **Basic Controlat (140 RON)**: Pentru clienți cu buget redus, acces controlat
    2. **Standard (200 RON)**: Abonament de bază, nelimitat
    3. **Premium / Recovery (500 RON)**: Cu servicii speciale de recuperare
    4. **PT / Reabilitare (125 RON/sesiune)**: Servicii personalizate, marjă ridicată
    
    **Logica:**
    - Diversificare = stabilitate financiară
    - Fiecare segment are nevoi diferite
    - Distribuția abonamentelor afectează direct veniturile
    - PT/Reabilitare este integrat în distribuția de 100% (nu contor separat)
    """)
    
    st.markdown("---")
    
    st.markdown('<div id="logica-calcul"></div>', unsafe_allow_html=True)
    st.markdown("""
    ## 🔢 Logica de Calcul
    
    ### 1. Calculul Clienților Necesari
    
    #### Pentru Abonamente cu Sesiuni Limitate:
    ```
    Slot-uri ocupate de tipul X = Total slot-uri ocupate × % distribuție tip X
    Clienți necesari = Slot-uri ocupate / Sesiuni per abonament
    ```
    
    #### Pentru Abonament Standard (Nelimitat):
    ```
    Presupunem: 3 vizite pe săptămână per client
    Slot-uri pe săptămână = Slot-uri standard / 4.33 săptămâni
    Clienți = Slot-uri pe săptămână / 3 vizite
    ```
    
    **De ce 3 vizite?**
    - Media industriei pentru abonamente nelimitate
    - Poate fi ajustat în funcție de date reale
    - Reflectă utilizarea reală (nu toți vin zilnic)
    
    #### Pentru PT/Reabilitare (Sesiuni):
    ```
    Sesiuni PT = Slot-uri ocupate × % PT
    Clienți PT = Sesiuni PT / 5 sesiuni per client (medie)
    ```
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 2. Calculul Veniturilor
    
    ```
    Venit Total = Σ (Clienți tip × Preț abonament tip)
    ```
    
    Pentru PT/Reabilitare:
    ```
    Venit PT = Sesiuni PT × Preț per sesiune
    ```
    
    **Simplu și direct:**
    - Fiecare client plătește prețul abonamentului său
    - Suma tuturor = venit total
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 3. Calculul Razei de Influență
    
    Aceasta este partea cea mai interesantă și utilă:
    
    ```
    Populație disponibilă per km² = Densitate populație × Rata participare
    Suprafață necesară = Clienți necesari / Populație disponibilă per km²
    Rază = √(Suprafață / π)
    ```
    
    **Exemplu concret:**
    - Ai nevoie de 300 clienți
    - Densitate: 1,000 oameni/km²
    - Participare: 10% (100 oameni disponibili/km²)
    - Suprafață necesară: 300 / 100 = 3 km²
    - Rază: √(3 / 3.14) = 0.98 km ≈ 1 km
    
    **De ce este important?**
    - Știi exact cât de mare trebuie să fie zona de marketing
    - Poți planifica campaniile geografic
    - Poți estima costurile de marketing
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 4. Calculul Dimensiunii Campaniei
    
    Logica completă pentru calcularea dimensiunii campaniei necesare:
    
    ```
    Pasul 1: Câți oameni trebuie atinși?
    Populație de atins = Clienți necesari / Rata de Conversie
    
    Pasul 2: Câtă populație interesată avem nevoie?
    Populație interesată necesară = Populație de atins / Rata de Acoperire
    
    Pasul 3: Câtă populație totală avem nevoie?
    Populație totală necesară = Populație interesată necesară / Rata de Participare
    
    Pasul 4: Ce suprafață trebuie să acoperim?
    Suprafață necesară = Populație totală necesară / Densitate populație
    
    Pasul 5: Care este raza necesară?
    Raza = √(Suprafață necesară / π)
    ```
    
    **Exemplu concret:**
    - Clienți necesari: 300
    - Rata de Conversie: 5% → Populație de atins: 300 / 0.05 = 6,000 oameni
    - Rata de Acoperire: 50% → Populație interesată necesară: 6,000 / 0.50 = 12,000 oameni
    - Rata de Participare: 10% → Populație totală necesară: 12,000 / 0.10 = 120,000 oameni
    - Densitate: 1,000 oameni/km² → Suprafață: 120,000 / 1,000 = 120 km²
    - Raza: √(120 / 3.14) ≈ 6.18 km
    """)
    
    st.markdown("---")
    
    st.markdown('<div id="explicatie-rate"></div>', unsafe_allow_html=True)
    st.markdown("""
    ### 5. Explicația Detaliată a Ratelor
    
    #### 📊 Rata de Participare a Populației
    
    **Ce înseamnă?**
    Rata de participare reprezintă procentul din populația totală dintr-o zonă care ar putea fi potențial interesați de serviciile fitness și recuperare.
    
    **Cum se calculează?**
    ```
    Populație Interesată = Populație Totală × Rata de Participare
    ```
    
    **Exemplu:**
    - Populație totală în zonă: 100,000 oameni
    - Rata de participare: 10%
    - Populație interesată: 100,000 × 10% = 10,000 oameni
    
    **Ce valori sunt realiste?**
    - **5-8%**: Conservator, pentru zone cu interes redus pentru fitness
    - **10-12%**: Realist pentru majoritatea zonelor urbane
    - **15-20%**: Optimist, pentru zone cu interes ridicat pentru fitness
    - **Peste 20%**: Foarte optimist, rar întâlnit
    
    **De ce este importantă?**
    - Determină câtă populație totală trebuie să acoperi pentru a avea suficienți oameni interesați
    - Impact direct asupra razei de influență necesare
    - Poate fi ajustată pe baza datelor reale din sondaje sau cercetări de piață
    
    **Cum să o estimezi?**
    - Sondaje în zonă
    - Date despre utilizarea sălilor existente
    - Analiză demografică (vârstă, venit, stil de viață)
    - Comparație cu zone similare
    
    ---
    
    #### 🎯 Rata de Acoperire
    
    **Ce înseamnă?**
    Rata de acoperire definește ce procent din populația interesată trebuie atins efectiv de campania de marketing pentru a obține clienții necesari.
    
    **Cum se calculează?**
    ```
    Populație de Atins = Populație Interesată × Rata de Acoperire
    ```
    
    **Exemplu:**
    - Populație interesată: 10,000 oameni
    - Rata de acoperire: 50%
    - Populație de atins: 10,000 × 50% = 5,000 oameni
    
    **Ce valori sunt realiste?**
    - **30-40%**: Campanie conservatoare, pentru zone cu concurență redusă
    - **50-60%**: Realist pentru majoritatea campaniilor
    - **70-80%**: Campanie agresivă, pentru zone competitive
    - **90-100%**: Foarte agresiv, necesită buget mare
    
    **De ce este importantă?**
    - Definește dimensiunea reală a campaniei de marketing
    - Impact direct asupra costurilor campaniei
    - Permite controlul asupra intensității campaniei
    
    **Factori care influențează rata de acoperire:**
    - **Concurența**: Zone cu mai multe săli necesită acoperire mai mare
    - **Buget disponibil**: Buget mai mare permite acoperire mai mare
    - **Strategia**: Campanie agresivă vs. graduală
    - **Calitatea mesajului**: Mesaj mai bun = acoperire mai mică necesară
    
    ---
    
    #### 💰 Rata de Conversie a Campaniei
    
    **Ce înseamnă?**
    Rata de conversie reprezintă procentul din oamenii atinși de campanie care devin efectiv clienți (se înscriu și plătesc abonamentul).
    
    **Cum se calculează?**
    ```
    Clienți Obținuți = Populație de Atins × Rata de Conversie
    ```
    
    **Exemplu:**
    - Populație de atins: 5,000 oameni
    - Rata de conversie: 5%
    - Clienți obținuți: 5,000 × 5% = 250 clienți
    
    **Ce valori sunt realiste?**
    - **2-3%**: Conservator, pentru campanii generale
    - **5-7%**: Realist pentru campanii bine targetate
    - **8-10%**: Bun, pentru campanii foarte bine targetate și mesaje puternice
    - **Peste 10%**: Excelent, rar întâlnit, necesită mesaj foarte puternic și ofertă atractivă
    
    **De ce este importantă?**
    - Determină câți oameni trebuie atinși pentru a obține numărul de clienți necesari
    - Impact direct asupra costurilor campaniei (mai mulți oameni de atins = costuri mai mari)
    - Reflectă eficiența campaniei de marketing
    
    **Factori care influențează rata de conversie:**
    - **Calitatea mesajului**: Mesaj clar și atractiv = conversie mai bună
    - **Targeting**: Campanii bine targetate = conversie mai bună
    - **Oferta**: Ofertă atractivă (preț, servicii) = conversie mai bună
    - **Momentul**: Campanii în perioade relevante = conversie mai bună
    - **Canalul de marketing**: Canale eficiente = conversie mai bună
    
    **Cum să îmbunătățești rata de conversie:**
    - Mesaj clar despre propunerea de valoare
    - Ofertă atractivă (prețuri competitive, servicii relevante)
    - Call-to-action clar
    - Ușurință în procesul de înscriere
    - Testare și optimizare continuă
    
    ---
    
    #### 🔄 Relația între Cele Trei Rate
    
    Aceste trei rate lucrează împreună pentru a determina dimensiunea campaniei:
    
    ```
    Populație Totală
        ↓ (× Rata de Participare)
    Populație Interesată
        ↓ (× Rata de Acoperire)
    Populație de Atins
        ↓ (× Rata de Conversie)
    Clienți Finali
    ```
    
    **Exemplu complet:**
    - Populație totală: 100,000 oameni
    - Rata de participare: 10% → Populație interesată: 10,000 oameni
    - Rata de acoperire: 50% → Populație de atins: 5,000 oameni
    - Rata de conversie: 5% → Clienți finali: 250 clienți
    
    **Impactul ajustărilor:**
    - **Creșterea ratei de participare** → Mai puțină populație totală necesară
    - **Creșterea ratei de acoperire** → Mai puțină populație interesată necesară
    - **Creșterea ratei de conversie** → Mai puțină populație de atins necesară
    
    **Optimizare:**
    - Poți ajusta oricare dintre rate pentru a optimiza dimensiunea campaniei
    - De obicei, este mai eficient să îmbunătățești rata de conversie decât să crești acoperirea
    - Rata de participare este cel mai greu de influențat (depinde de demografie)
    """)
    
    st.markdown("---")
    
    st.markdown("""
    st.markdown('<div id="model-geografic"></div>', unsafe_allow_html=True)
    ## 🗺️ Modelul Geografic
    
    ### De ce o Hartă?
    
    1. **Vizualizare Concretă**: Vezi exact zona de acoperire
    2. **Planificare Marketing**: Știi unde să te concentrezi
    3. **Blocuri și Cartiere**: Participare diferită bazată pe distanță
    
    ### Logica Participării pe Blocuri
    
    Am creat un model simplu dar eficient:
    
    ```
    Distanță de la sală → Participare
    - Foarte aproape (<30% rază): Participare +30%
    - Aproape (30-60% rază): Participare normală
    - Departe (60-90% rază): Participare -30%
    - Foarte departe (>90% rază): Participare -50%
    ```
    
    **De ce?**
    - Oamenii preferă să meargă la sală aproape de casă
    - Distanța afectează frecvența
    - Realitatea: mai aproape = mai mulți clienți
    
    **Notă:** Blocurile sunt reprezentate ca poligoane (chenare) pe hartă, fiecare afișând participarea necesară pentru a atinge obiectivul.
    """)
    
    st.markdown("---")
    
    st.markdown("""
    st.markdown('<div id="structura-dashboard"></div>', unsafe_allow_html=True)
    ## 📊 Structura Dashboard-ului
    
    ### De ce 8 Tab-uri?
    
    Fiecare tab răspunde la o întrebare specifică:
    
    1. **📊 Rezumat**: "Ce am în general?"
       - Vedere de ansamblu rapidă
       - Toate metricile importante într-un loc
    
    2. **💰 Venituri**: "Cât pot câștiga?"
       - Detalii pe tip de abonament
       - Comparație cu obiectivul (50,000 RON)
    
    3. **👥 Clienți & Demografie**: "Câți clienți am nevoie?"
       - Distribuție clienți
       - Parametri demografici necesari
    
    4. **📈 Comparare Scenarii**: "Care scenariu este cel mai bun?"
       - Vezi toate opțiunile simultan
       - Compară venituri, clienți, raze
    
    5. **🗺️ Hartă Participare**: "Unde trebuie să mă concentrez?"
       - Vizualizare geografică
       - Blocuri cu participare diferită
    
    6. **🎯 Campanie**: "Ce campanie trebuie să fac?"
       - Dimensiune necesară
       - Costuri estimate
       - Recomandări strategice
    
    7. **🏆 Analiză Concurențială**: "Cum mă poziționez față de concurență?"
       - Comparație capacitate, prețuri, model
       - Avantaje competitive
       - Layout și eficiență spațială
    
    8. **📘 Scopul și Arhitectura Dashboard**: "Cum funcționează totul?" (acest tab)
       - Explicații detaliate
       - Logica din spatele calculelor
       - Înțelegere completă a modelului
    """)
    
    st.markdown("---")
    
    st.markdown("""
    st.markdown('<div id="design-decisions"></div>', unsafe_allow_html=True)
    ## 🎨 Design Decisions (Decizii de Design)
    
    ### De ce Streamlit?
    
    1. **Rapid de dezvoltat**: Dashboard funcțional în timp scurt
    2. **Interactiv**: Utilizatorul poate explora scenarii
    3. **Ușor de folosit**: Nu necesită cunoștințe tehnice avansate
    4. **Gratuit**: Open source, fără costuri
    
    ### De ce Python?
    
    1. **Biblioteci puternice**: pandas, numpy pentru calcule
    2. **Vizualizări**: plotly pentru graficuri interactive
    3. **Hărți**: folium pentru hărți interactive
    4. **Comunitate mare**: Multe resurse și suport
    
    ### De ce Calcule Dinamice?
    
    - **Flexibilitate**: Utilizatorul poate explora scenarii diferite
    - **Înțelegere**: Vezi imediat impactul schimbărilor
    - **Decizii informate**: Nu doar un număr, ci o înțelegere completă
    """)
    
    st.markdown("---")
    
    st.markdown("""
    st.markdown('<div id="flux-date"></div>', unsafe_allow_html=True)
    ## 🔄 Fluxul de Date
    
    ```
    Utilizator ajustează filtre
        ↓
    Dashboard recalculează automat
        ↓
    Rezultatele se actualizează în timp real
        ↓
    Utilizator vede impactul imediat
    ```
    
    **De ce este important?**
    - Nu trebuie să rulezi scripturi separate
    - Poți explora rapid multe scenarii
    - Înțelegi relațiile între parametri
    """)
    
    st.markdown("---")
    
    st.markdown("""
    st.markdown('<div id="insights-cheie"></div>', unsafe_allow_html=True)
    ## 💡 Insights Cheie
    
    ### 1. Relația între Ocupare și Venituri
    
    - Ocupare mai mare = mai mulți clienți = mai multe venituri
    - Dar: ocupare 100% este nerealistă
    - Scenariul mediu (50-75%) este cel mai echilibrat
    
    ### 2. Impactul Distribuției Abonamentelor
    
    - Mai mulți premium = venituri mai mari
    - Dar: mai puțini clienți premium disponibili
    - Echilibrul este cheia
    
    ### 3. Importanța Razei de Influență
    
    - Rază mică (<2 km) = campanie locală, mai ieftină
    - Rază mare (>5 km) = campanie amplă, mai scumpă
    - Planifică în consecință
    
    ### 4. Rata de Participare este Critică
    
    - 10% este o estimare conservatoare
    - Dacă ai date reale, folosește-le
    - Impact direct asupra razei de influență
    - **Definiție:** Reprezintă procentul din populația totală care ar putea fi interesați de fitness
    - **Calcul:** Populație Interesată = Populație Totală × Rata de Participare
    - **Valori realiste:** 5-8% (conservator), 10-12% (realist), 15-20% (optimist)
    
    ### 5. Rata de Acoperire Definește Dimensiunea Campaniei
    
    - Controlată de tine prin slider (10-100%, default 50%)
    - Definește ce procent din populația interesată trebuie atins de campanie
    - Impact direct asupra costurilor campaniei
    - **Definiție:** Populație de Atins = Populație Interesată × Rata de Acoperire
    - **Valori realiste:** 30-40% (conservator), 50-60% (realist), 70-80% (agresiv)
    - Mai mare = campanie mai amplă, dar mai scumpă
    
    ### 6. Rata de Conversie Determină Eficiența Campaniei
    
    - Reflectă calitatea campaniei și a ofertei
    - 5% este un standard realist pentru campanii bine targetate
    - Poate fi îmbunătățită prin mesaje clare și oferte atractive
    - Impact direct asupra numărului de oameni care trebuie atinși
    - **Definiție:** Clienți Obținuți = Populație de Atins × Rata de Conversie
    - **Valori realiste:** 2-3% (conservator), 5-7% (realist), 8-10% (excelent)
    - **Cum să o îmbunătățești:** Mesaj clar, ofertă atractivă, call-to-action clar, ușurință în înscriere
    """)
    
    st.markdown("---")
    
    st.markdown("""
    st.markdown('<div id="utilizare-dashboard"></div>', unsafe_allow_html=True)
    ## 🎯 Utilizarea Dashboard-ului
    
    ### Workflow Recomandat
    
    1. **Începe cu Scenariul Mediu**
       - Cel mai realist
       - Baza pentru planificare
    
    2. **Ajustează Distribuția Abonamentelor**
       - Încearcă diferite combinații
       - Vezi impactul asupra veniturilor
    
    3. **Explorează Parametrii Demografici**
       - Schimbă rata de participare
       - Vezi cum se modifică raza de influență
    
    4. **Compară Scenariile**
       - Vezi diferențele
       - Alege cel mai potrivit pentru tine
    
    5. **Analizează Harta**
       - Vezi zona de acoperire
       - Planifică campania geografic
    
    6. **Planifică Campania**
       - Vezi dimensiunea necesară
       - Estimează costurile
    
    7. **Analizează Concurența**
       - Înțelege poziționarea ta
       - Identifică avantajele competitive
    """)
    
    st.markdown("---")
    
    st.markdown("""
    st.markdown('<div id="concluzii"></div>', unsafe_allow_html=True)
    ## 📝 Concluzii
    
    Acest dashboard este un **instrument de planificare și analiză**, nu o predicție exactă. 
    
    **Valoarea lui:**
    - Îți dă o înțelegere clară a potențialului
    - Te ajută să planifici marketing-ul
    - Te ajută să iei decizii informate
    - Poți explora scenarii diferite rapid
    
    **Limitele:**
    - Folosește presupuneri (rata participare, distribuție)
    - Nu include cheltuieli (în dezvoltare)
    - Blocurile sunt simulate (poți importa date reale)
    
    **Cum să-l folosești:**
    - Ca punct de plecare pentru analiză
    - Pentru a explora scenarii diferite
    - Pentru a planifica campaniile
    - Pentru a discuta cu investitori/parteneri
    """)
    
    st.markdown("---")
    
    st.markdown("""
    st.markdown('<div id="invataminte"></div>', unsafe_allow_html=True)
    ## 🎓 Învățăminte
    
    1. **Simplu este mai bun**: Dashboard-ul este simplu de folosit, nu complicat
    2. **Interactivitate contează**: Poți explora scenarii rapid
    3. **Vizualizările ajută**: Hărțile și graficurile fac datele mai ușor de înțeles
    4. **Documentația este esențială**: Fiecare utilizator are nevoi diferite
    
    ---
    
    **Document creat pentru a ajuta utilizatorii noi să înțeleagă nu doar "cum" funcționează dashboard-ul, ci și "de ce" a fost construit așa și "ce" înseamnă fiecare calcul.**
    
    **Succes în utilizarea dashboard-ului! 🚀**
    """)

# Tab 9: Previziuni Financiare
with tab9:
    st.markdown("""
    # 💵 Previziuni Financiare - Mobilis Vita
    
    Această secțiune prezintă previziunile financiare bazate pe datele reale ale proiectului.
    """)
    
    forecast_summary = get_financial_forecast_summary()
    forecast_df = get_financial_forecast_by_space()
    
    # Metrici principale
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Venit Total/Lună (Pesimist)",
            f"{forecast_summary['total_revenue']['pessimistic']:,.0f} RON",
            help="Venit total în scenariul pesimist (30% ocupare)"
        )
    
    with col2:
        st.metric(
            "Venit Total/Lună (Maxim)",
            f"{forecast_summary['total_revenue']['maximum']:,.0f} RON",
            help="Venit total în scenariul maxim (100% ocupare)"
        )
    
    with col3:
        st.metric(
            "Cheltuieli Totale/Lună",
            f"{forecast_summary['total_expenses']:,.0f} RON",
            help="Cheltuieli totale: salarii + chirie + utilități"
        )
    
    with col4:
        profit_pessimistic = forecast_summary['profit']['pessimistic']
        profit_maximum = forecast_summary['profit']['maximum']
        st.metric(
            "Profit/Lună (Pesimist)",
            f"{profit_pessimistic:,.0f} RON",
            delta=f"Maxim: {profit_maximum:,.0f} RON" if profit_maximum > 0 else None,
            help="Profit în scenariul pesimist"
        )
    
    # Break-even analysis
    st.markdown("### 📊 Analiză Break-Even")
    
    break_even_occupancy = forecast_summary['break_even_occupancy']
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Ocupare minimă pentru break-even:**
        
        {break_even_occupancy*100:.1f}% din capacitate maximă
        
        **Explicație:**
        - Cheltuieli totale: {forecast_summary['total_expenses']:,.0f} RON/lună
        - Venit maxim: {forecast_summary['total_revenue']['maximum']:,.0f} RON/lună
        - Pentru a acoperi cheltuielile, trebuie să atingi cel puțin {break_even_occupancy*100:.1f}% ocupare
        """)
    
    with col2:
        # Grafic break-even
        occupancy_levels = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        revenues = [r * forecast_summary['total_revenue']['maximum'] for r in occupancy_levels]
        profits = [r - forecast_summary['total_expenses'] for r in revenues]
        
        fig_break_even = go.Figure()
        fig_break_even.add_trace(go.Scatter(
            x=[o*100 for o in occupancy_levels],
            y=revenues,
            mode='lines+markers',
            name='Venituri',
            line=dict(color='green', width=3)
        ))
        fig_break_even.add_trace(go.Scatter(
            x=[o*100 for o in occupancy_levels],
            y=[forecast_summary['total_expenses']] * len(occupancy_levels),
            mode='lines',
            name='Cheltuieli (fixe)',
            line=dict(color='red', width=2, dash='dash')
        ))
        fig_break_even.add_hline(
            y=0,
            line_dash="dot",
            line_color="gray",
            annotation_text="Break-even"
        )
        fig_break_even.update_layout(
            title="Analiză Break-Even: Venituri vs Cheltuieli",
            xaxis_title="Ocupare (%)",
            yaxis_title="Sumă (RON)",
            height=400
        )
        st.plotly_chart(fig_break_even, use_container_width=True)
    
    # Tabel detaliat pe spații
    st.markdown("### 📋 Previziuni pe Spații")
    st.dataframe(forecast_df, use_container_width=True, hide_index=True)
    
    # Grafic comparativ venituri
    st.markdown("### 📈 Comparare Venituri: Pesimist vs Maxim")
    
    spaces_data = []
    for space in forecast_summary['spaces']:
        spaces_data.append({
            'Spațiu': space['name'],
            'Venit Pesimist (RON)': space['monthly_revenue_pessimistic'],
            'Venit Maxim (RON)': space['monthly_revenue_maximum']
        })
    
    spaces_df = pd.DataFrame(spaces_data)
    
    fig_revenues = go.Figure()
    fig_revenues.add_trace(go.Bar(
        x=spaces_df['Spațiu'],
        y=spaces_df['Venit Pesimist (RON)'],
        name='Venit Pesimist (30% ocupare)',
        marker_color='orange'
    ))
    fig_revenues.add_trace(go.Bar(
        x=spaces_df['Spațiu'],
        y=spaces_df['Venit Maxim (RON)'],
        name='Venit Maxim (100% ocupare)',
        marker_color='green'
    ))
    fig_revenues.update_layout(
        title="Venituri Lunare pe Spațiu - Comparație Scenarii",
        xaxis_title="Spațiu",
        yaxis_title="Venit (RON)",
        barmode='group',
        height=500,
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_revenues, use_container_width=True)
    
    # Detalii cheltuieli
    st.markdown("### 💸 Detalii Cheltuieli")
    
    expenses = forecast_summary['expenses_detail']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 💼 Salarii")
        st.write(f"**{expenses['salaries']['high_salary_count']}x** {expenses['salaries']['high_salary_amount']:,.0f} RON = {expenses['salaries']['high_salary_count'] * expenses['salaries']['high_salary_amount']:,.0f} RON")
        st.write(f"**{expenses['salaries']['low_salary_count']}x** {expenses['salaries']['low_salary_amount']:,.0f} RON = {expenses['salaries']['low_salary_count'] * expenses['salaries']['low_salary_amount']:,.0f} RON")
        st.metric("Total Salarii", f"{expenses['salaries']['total_monthly']:,.0f} RON/lună")
    
    with col2:
        st.markdown("#### 🏠 Chirie")
        exchange_rate = st.number_input(
            "Curs EUR/RON",
            min_value=4.5,
            max_value=5.5,
            value=expenses['rent']['exchange_rate'],
            step=0.1,
            key="exchange_rate_input"
        )
        rent_ron = expenses['rent']['amount_eur'] * exchange_rate
        st.write(f"**{expenses['rent']['amount_eur']} EUR** × {exchange_rate:.2f} = **{rent_ron:,.0f} RON/lună**")
        st.metric("Chirie", f"{rent_ron:,.0f} RON/lună")
    
    with col3:
        st.markdown("#### ⚡ Utilități (Iarnă)")
        st.write(f"**Minim:** {expenses['utilities']['winter_min']:,.0f} RON/lună")
        st.write(f"**Maxim:** {expenses['utilities']['winter_max']:,.0f} RON/lună")
        st.metric("Medie Utilități", f"{expenses['utilities']['average']:,.0f} RON/lună")
    
    # Recalculare cu chirie actualizată
    total_expenses_updated = (
        expenses['salaries']['total_monthly'] +
        rent_ron +
        expenses['utilities']['average']
    )
    
    profit_pessimistic_updated = forecast_summary['total_revenue']['pessimistic'] - total_expenses_updated
    profit_maximum_updated = forecast_summary['total_revenue']['maximum'] - total_expenses_updated
    
    st.markdown("### 💰 Rezumat Financiar Actualizat")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Cheltuieli Totale", f"{total_expenses_updated:,.0f} RON/lună")
    
    with col2:
        st.metric(
            "Profit Pesimist",
            f"{profit_pessimistic_updated:,.0f} RON/lună",
            delta=f"{profit_pessimistic_updated - forecast_summary['profit']['pessimistic']:,.0f} RON" if profit_pessimistic_updated != forecast_summary['profit']['pessimistic'] else None
        )
    
    with col3:
        st.metric(
            "Profit Maxim",
            f"{profit_maximum_updated:,.0f} RON/lună",
            delta=f"{profit_maximum_updated - forecast_summary['profit']['maximum']:,.0f} RON" if profit_maximum_updated != forecast_summary['profit']['maximum'] else None
        )
    
    # Capacitate
    st.markdown("### 👥 Capacitate Spațiu")
    
    capacity_info = forecast_summary.get('capacity', {})
    if capacity_info:
        st.info(f"""
        **Capacitate maximă/oră:** {capacity_info.get('max_per_hour', 'N/A')} persoane
        
        **Distribuție:**
        - Terapii individuale: {capacity_info.get('breakdown', {}).get('terapii_individuale', 'N/A')} persoane
        - Sală clase: {capacity_info.get('breakdown', {}).get('sala_clase', 'N/A')} persoane
        - Sală fitness: {capacity_info.get('breakdown', {}).get('sala_fitness', 'N/A')} persoane (6-8 persoane)
        """)
    
    # Insights
    st.markdown("### 💡 Insights Cheie")
    
    if profit_pessimistic_updated < 0:
        st.warning(f"""
        ⚠️ **Atenție:** În scenariul pesimist (30% ocupare), profitul este negativ: **{profit_pessimistic_updated:,.0f} RON/lună**
        
        **Recomandări:**
        - Focalizează-te pe atingerea a cel puțin {break_even_occupancy*100:.1f}% ocupare pentru break-even
        - Consideră strategii de marketing pentru a crește ocuparea
        - Optimizează cheltuielile dacă este posibil
        """)
    else:
        st.success(f"""
        ✅ **Scenariul pesimist este profitabil:** {profit_pessimistic_updated:,.0f} RON/lună
        
        **Potențial maxim:** {profit_maximum_updated:,.0f} RON/lună la 100% ocupare
        """)
    
    st.info(f"""
    **Break-even ocupare:** {break_even_occupancy*100:.1f}%
    
    **Marja de siguranță (scenariul pesimist):** {((forecast_summary['total_revenue']['pessimistic'] / total_expenses_updated - 1) * 100):.1f}% peste break-even
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Dashboard creat pentru analiza potențialului spațiului fitness și recuperare</p>
    <p>📍 {address}, {city}</p>
</div>
""".format(address=LOCATION['address'], city=LOCATION['city']), unsafe_allow_html=True)

