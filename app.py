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
from calculations import (
    get_scenario_analysis,
    compare_scenarios,
    OCCUPANCY_SCENARIOS,
    SUBSCRIPTION_TYPES,
    DESIRED_MONTHLY_REVENUE,
    LOCATION,
    COMPETITORS,
    CAPACITY_PER_HOUR,
    COMPETITOR_LOCATIONS
)
from competitor_analysis import (
    get_competitive_positioning,
    get_competitors_comparison,
    calculate_market_position,
    get_layout_comparison,
    get_recommended_layout,
    simulate_new_redgym_impact,
    calculate_profitability_comparison,
    COMFORT_THRESHOLDS
)

# Configurare pagină
st.set_page_config(
    page_title="Analiză Potențial Spațiu Fitness - Bacau",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
st.markdown('<h1 class="main-header">💪 Dashboard Analiză Potențial Spațiu Fitness & Recuperare</h1>', unsafe_allow_html=True)
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

# Distribuție servicii - Structură extinsă (toate formează 100%)
st.sidebar.subheader("Distribuție Servicii (%)")
st.sidebar.caption("💡 **Notă:** Valorile se normalizează automat la 100%. PT/Reabilitare ocupă slot-uri ca orice alt serviciu.")

# Toate serviciile (inclusiv PT) formează 100%
basic_pct = st.sidebar.slider(
    f"{SUBSCRIPTION_TYPES['basic']['name']} ({SUBSCRIPTION_TYPES['basic']['price']} RON/lună)",
    0, 100, 40, 5,
    help=SUBSCRIPTION_TYPES['basic']['description']
)
standard_pct = st.sidebar.slider(
    f"{SUBSCRIPTION_TYPES['standard']['name']} ({SUBSCRIPTION_TYPES['standard']['price']} RON/lună)",
    0, 100, 40, 5,
    help=SUBSCRIPTION_TYPES['standard']['description']
)
premium_pct = st.sidebar.slider(
    f"{SUBSCRIPTION_TYPES['premium']['name']} ({SUBSCRIPTION_TYPES['premium']['price']} RON/lună)",
    0, 100, 15, 5,
    help=SUBSCRIPTION_TYPES['premium']['description']
)
pt_pct = st.sidebar.slider(
    f"{SUBSCRIPTION_TYPES['pt_session']['name']} ({SUBSCRIPTION_TYPES['pt_session']['price']} RON/sesiune)",
    0, 100, 5, 5,
    help=f"{SUBSCRIPTION_TYPES['pt_session']['description']}. Fiecare sesiune ocupă 1 slot."
)

# Normalizare distribuție (toate serviciile formează 100%)
total_pct = basic_pct + standard_pct + premium_pct + pt_pct
if total_pct == 0:
    basic_pct, standard_pct, premium_pct, pt_pct = 40, 40, 15, 5
    total_pct = 100

# Calculează procentajele normalizate
basic_normalized = (basic_pct / total_pct) * 100
standard_normalized = (standard_pct / total_pct) * 100
premium_normalized = (premium_pct / total_pct) * 100
pt_normalized = (pt_pct / total_pct) * 100

# Afișează procentajele normalizate
if total_pct != 100:
    st.sidebar.info(f"📊 **Distribuție normalizată:** Basic {basic_normalized:.1f}% | Standard {standard_normalized:.1f}% | Premium {premium_normalized:.1f}% | PT {pt_normalized:.1f}%")
else:
    st.sidebar.success(f"✅ **Distribuție:** Basic {basic_normalized:.1f}% | Standard {standard_normalized:.1f}% | Premium {premium_normalized:.1f}% | PT {pt_normalized:.1f}%")

# Explicație PT
if pt_normalized > 0:
    st.sidebar.caption(f"💡 **PT/Reabilitare:** {pt_normalized:.1f}% din slot-uri ocupate = sesiuni PT/lună (calculat automat din ocupare)")

subscription_distribution = {
    'basic': basic_pct / total_pct,
    'standard': standard_pct / total_pct,
    'premium': premium_pct / total_pct,
    'pt_session': pt_pct / total_pct
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

# Calculează analiza pentru scenariul selectat
analysis = get_scenario_analysis(
    selected_scenario,
    subscription_distribution,
    participation_rate,
    population_density
)

# Ajustare pentru conversie în calculul campaniei
from calculations import calculate_campaign_scale
campaign_data = calculate_campaign_scale(
    analysis['total_clients'],
    participation_rate,
    population_density,
    conversion_rate
)
analysis['campaign'] = campaign_data

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

# Tabs pentru diferite vizualizări
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Rezumat", 
    "💰 Venituri", 
    "👥 Clienți & Demografie", 
    "📈 Comparare Scenarii",
    "🗺️ Hartă Participare",
    "🎯 Campanie",
    "🏆 Analiză Concurențială"
])

with tab1:
    st.subheader("Rezumat Analiză")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Capacitate Spațiu")
        st.write(f"**Capacitate maximă lunară:** {analysis['max_capacity']:,} slot-uri")
        st.write(f"**Slot-uri ocupate:** {analysis['occupied_slots']:,} slot-uri")
        st.write(f"**Rata ocupare:** {analysis['occupancy_rate']*100:.1f}%")
        
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
        st.markdown("### Clienți pe Tip Abonament")
        clients_data = analysis['revenue']['clients']
        clients_df = pd.DataFrame({
            'Tip Abonament': [SUBSCRIPTION_TYPES[k]['name'] for k in clients_data.keys()],
            'Număr Clienți': list(clients_data.values())
        })
        
        fig_clients = px.bar(
            clients_df,
            x='Tip Abonament',
            y='Număr Clienți',
            color='Tip Abonament',
            color_discrete_map={
                SUBSCRIPTION_TYPES['basic']['name']: '#2ecc71',
                SUBSCRIPTION_TYPES['standard']['name']: '#3498db',
                SUBSCRIPTION_TYPES['premium']['name']: '#e74c3c',
                SUBSCRIPTION_TYPES['pt_session']['name']: '#9b59b6'
            }
        )
        fig_clients.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig_clients, use_container_width=True)
        
        st.markdown("### Raza de Influență")
        st.info(f"""
        Pentru a atinge **{analysis['total_clients']} clienți** cu:
        - Rata participare: **{participation_rate*100:.1f}%**
        - Densitate populație: **{population_density:,} oameni/km²**
        
        Este necesară o rază de influență de **{analysis['influence_radius_km']:.2f} km**
        """)

with tab2:
    st.subheader("Analiză Venituri")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Grafic venituri pe tip abonament
        revenue_data = analysis['revenue']
        # Obține doar tipurile cu venit > 0
        active_types = [k for k in ['basic', 'standard', 'premium', 'pt_session'] 
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
            color_discrete_map={
                SUBSCRIPTION_TYPES['basic']['name']: '#2ecc71',
                SUBSCRIPTION_TYPES['standard']['name']: '#3498db',
                SUBSCRIPTION_TYPES['premium']['name']: '#e74c3c',
                SUBSCRIPTION_TYPES['pt_session']['name']: '#9b59b6'
            }
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Necesar Clienți")
        clients_data = analysis['revenue']['clients']
        active_client_types = [k for k in ['basic', 'standard', 'premium', 'pt_session'] 
                              if k in clients_data and clients_data.get(k, 0) > 0]
        
        clients_df = pd.DataFrame({
            'Tip Abonament': [SUBSCRIPTION_TYPES[k]['name'] for k in active_client_types],
            'Număr Clienți/Sesiuni': [clients_data.get(k, 0) for k in active_client_types]
        })
        
        fig_clients_detailed = px.bar(
            clients_df,
            x='Tip Abonament',
            y='Număr Clienți/Sesiuni',
            text='Număr Clienți/Sesiuni',
            color='Tip Abonament',
            color_discrete_map={
                SUBSCRIPTION_TYPES['basic']['name']: '#2ecc71',
                SUBSCRIPTION_TYPES['standard']['name']: '#3498db',
                SUBSCRIPTION_TYPES['premium']['name']: '#e74c3c',
                SUBSCRIPTION_TYPES['pt_session']['name']: '#9b59b6'
            }
        )
        fig_clients_detailed.update_traces(textposition='outside')
        fig_clients_detailed.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_clients_detailed, use_container_width=True)
    
    with col2:
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
        population_density
    )
    
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
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
    
    # Creează hartă centrată pe locație
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
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
    
    # Generează blocuri/cartiere cu participare diferită
    # Simulăm blocuri în jurul locației cu participare bazată pe distanță
    
    for i in range(num_blocks):
        # Generează coordonate aleatorii în jurul centrului
        angle = (2 * math.pi * i) / num_blocks
        distance_factor = 0.3 + (i % 4) * 0.2  # Distanțe variate
        block_lat = center_lat + (distance_factor * radius_km / 111) * math.cos(angle)
        block_lon = center_lon + (distance_factor * radius_km / 111) * math.sin(angle) / math.cos(math.radians(center_lat))
        
        # Calculează distanța de la centru
        distance = haversine_distance(center_lat, center_lon, block_lat, block_lon)
        
        # Participare bazată pe distanță (mai aproape = participare mai mare)
        if distance <= radius_km * 0.3:
            participation = participation_rate * 1.2  # +20% pentru zone apropiate
            color = 'green'
            intensity = 'Ridicată'
        elif distance <= radius_km * 0.6:
            participation = participation_rate * 1.0  # Participare normală
            color = 'blue'
            intensity = 'Medie'
        elif distance <= radius_km * 0.9:
            participation = participation_rate * 0.8  # -20% pentru zone mai îndepărtate
            color = 'orange'
            intensity = 'Moderată'
        else:
            participation = participation_rate * 0.6  # -40% pentru zone la margine
            color = 'red'
            intensity = 'Redusă'
        
        # Limitează participarea
        participation = min(participation, 0.30)
        
        # Populație estimată pentru bloc (bazată pe densitate)
        block_area_km2 = 0.1  # Presupunem fiecare bloc are ~0.1 km²
        block_population = int(block_area_km2 * population_density)
        interested_population = int(block_population * participation)
        
        blocks_data.append({
            'lat': block_lat,
            'lon': block_lon,
            'distance': distance,
            'participation': participation,
            'population': block_population,
            'interested': interested_population,
            'color': color,
            'intensity': intensity
        })
        
        # Adaugă marker pentru bloc cu culoare bazată pe participare
        folium.CircleMarker(
            location=[block_lat, block_lon],
            radius=8 + int(participation * 100),  # Mărime bazată pe participare
            popup=folium.Popup(
                f"""
                <b>Bloc/Cartier #{i+1}</b><br>
                <b>Distanță:</b> {distance:.2f} km<br>
                <b>Participare:</b> {participation*100:.1f}% ({intensity})<br>
                <b>Populație:</b> {block_population:,} oameni<br>
                <b>Populație interesată:</b> {interested_population:,} oameni
                """,
                max_width=250
            ),
            tooltip=f"Bloc #{i+1}: {intensity} participare ({participation*100:.1f}%)",
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.6,
            weight=2
        ).add_to(m)
    
    # Adaugă legendă
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 220px; height: 280px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:13px; padding: 10px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.2)">
    <h4 style="margin-top:0; font-size:14px">Legendă</h4>
    <p style="margin:5px 0"><b>Participare:</b></p>
    <p style="margin:2px 0"><span style="color:green; font-size:16px">●</span> Ridicată (>120%)</p>
    <p style="margin:2px 0"><span style="color:blue; font-size:16px">●</span> Medie (100%)</p>
    <p style="margin:2px 0"><span style="color:orange; font-size:16px">●</span> Moderată (80%)</p>
    <p style="margin:2px 0"><span style="color:red; font-size:16px">●</span> Redusă (<80%)</p>
    <hr style="margin:8px 0">
    <p style="margin:5px 0"><b>Locații:</b></p>
    <p style="margin:2px 0"><span style="color:green; font-size:16px">🏠</span> Sala Noastră</p>
    <p style="margin:2px 0"><span style="color:red; font-size:16px">🏋️</span> Concurenți</p>
    <p style="margin:2px 0"><span style="color:#3186cc; font-size:16px">○</span> Raza influență</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Afișează hartă
    st.info("💡 **Notă:** Harta necesită conexiune la internet pentru a se încărca. Dacă nu apare, verifică conexiunea.")
    
    try:
        # Salvează harta temporar și o afișează
        map_data = st_folium(m, width=1200, height=600, returned_objects=[])
    except Exception as e:
        st.error(f"⚠️ Eroare la afișarea hărții: {str(e)}")
        st.info("💡 **Soluții:**\n1. Verifică conexiunea la internet\n2. Reîmprospătează pagina (F5)\n3. Verifică dacă firewall-ul blochează conexiunea")
        
        # Alternativă: afișează informații despre hartă
        st.markdown("### Informații despre Hartă")
        st.write(f"**Locație:** {LOCATION['address']}, {LOCATION['city']}")
        st.write(f"**Coordonate:** {center_lat:.4f}, {center_lon:.4f}")
        st.write(f"**Raza de influență:** {radius_km:.2f} km")
        st.write(f"**Număr blocuri/cartiere:** {num_blocks}")
    
    # Tabel cu detalii blocuri
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
    
    campaign = analysis['campaign']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Populație Țintă",
            f"{campaign['target_population']:,}",
            help="Populația care trebuie atinsă de campanie"
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
            help="Rata de conversie a campaniei"
        )
    
    with col4:
        st.metric(
            "Suprafață (km²)",
            f"{campaign['area_km2']:.2f}",
            help="Suprafața acoperită de campanie"
        )
    
    st.markdown("### Detalii Campanie")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Dimensiune Campanie:**
        - Populație totală în zonă: **{campaign['total_population']:,}** oameni
        - Populație interesată: **{campaign['interested_population']:,}** oameni
        - Populație țintă (pentru conversie): **{campaign['target_population']:,}** oameni
        
        **Acoperire Geografică:**
        - Raza: **{campaign['radius_km']:.2f} km**
        - Suprafață: **{campaign['area_km2']:.2f} km²**
        """)
    
    with col2:
        # Grafic piramida conversiei
        conversion_stages = pd.DataFrame({
            'Etapă': [
                'Populație Totală',
                'Populație Interesată',
                'Populație Țintă',
                'Clienți Finali'
            ],
            'Număr': [
                campaign['total_population'],
                campaign['interested_population'],
                campaign['target_population'],
                analysis['total_clients']
            ]
        })
        
        fig_funnel = px.funnel(
            conversion_stages,
            x='Număr',
            y='Etapă',
            title="Funnel Conversie Campanie"
        )
        st.plotly_chart(fig_funnel, use_container_width=True)
    
    st.markdown("### Recomandări Campanie")
    
    if campaign['radius_km'] <= 2:
        st.success("✅ **Campanie locală:** Raza de influență este mică (< 2 km). Recomandăm campanii la nivel de cartier: distribuție de flyere, parteneriate cu magazine locale, rețele sociale locale.")
    elif campaign['radius_km'] <= 5:
        st.warning("⚠️ **Campanie extinsă:** Raza de influență este medie (2-5 km). Recomandăm o combinație de campanii locale și digitale: Facebook/Google Ads geo-targetate, parteneriate cu centre comerciale, evenimente locale.")
    else:
        st.error("🔴 **Campanie amplă:** Raza de influență este mare (> 5 km). Recomandăm campanii digitale extinse: Google Ads, Facebook Ads, parteneriate cu clinici medicale, colaborări cu antrenori personali.")
    
    # Calcul cost estimativ campanie
    st.markdown("### Estimare Cost Campanie")
    
    cost_per_person = st.number_input(
        "Cost per persoană atinsă (RON)",
        min_value=0.1,
        max_value=10.0,
        value=1.0,
        step=0.1,
        help="Costul estimat pentru a atinge o persoană prin campanie"
    )
    
    estimated_campaign_cost = campaign['target_population'] * cost_per_person
    
    st.metric(
        "Cost Total Estimativ Campanie",
        f"{estimated_campaign_cost:,.0f} RON",
        help="Costul estimat pentru a atinge populația țintă"
    )

with tab7:
    st.subheader("🏆 Analiză Concurențială & Poziționare Strategică")
    
    positioning = get_competitive_positioning()
    competitors = get_competitors_comparison()
    market_pos = calculate_market_position(analysis['total_clients'], CAPACITY_PER_HOUR)
    
    # Secțiune 1: Poziționare Strategică
    st.markdown("### 🎯 Poziționare Strategică")
    st.info(f"**{positioning['positioning']}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ Avantaje Competitive")
        for advantage in positioning['key_advantages']:
            st.write(f"• {advantage}")
    
    with col2:
        st.markdown("#### ❌ Ce NU Facem")
        for item in positioning['what_we_dont_do']:
            st.write(f"• {item}")
    
    # Secțiune 2: Capacitate Optimă
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
    st.markdown("### 📐 Layout Comparativ (mp/om)")
    
    st.markdown("""
    **De ce contează mp/om?**
    
    În fitness, confortul perceput ≠ mp total, ci: **câți metri pătrați revin fiecărui utilizator simultan**
    
    - **Sub ~6 mp/om** → Aglomerație
    - **8–10 mp/om** → Acceptabil
    - **12+ mp/om** → Premium / Control
    """)
    
    # Input pentru suprafața noastră
    our_area_m2 = st.number_input(
        "Suprafața Sălii Noastre (mp)",
        min_value=300,
        max_value=500,
        value=400,
        step=10,
        help="Suprafața totală a sălii (350-450 mp recomandat)",
        key="our_area_m2"
    )
    
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
    st.markdown("### 🏗️ Layout Recomandat pentru Sala Noastră")
    
    layout_recommended = get_recommended_layout()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Suprafață totală:** {layout_recommended['total_area_m2']} mp")
        st.markdown(f"**Capacitate țintă:** {layout_recommended['target_capacity']['min']}-{layout_recommended['target_capacity']['max']} persoane")
        st.markdown(f"**mp/om țintă:** {layout_recommended['m2_per_person_range']['min']}-{layout_recommended['m2_per_person_range']['max']} mp/om")
    
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
    
    # Secțiune 10: Verdict Final
    st.markdown("### ✅ Verdict Final")
    
    verdict_items = [
        "✅ Locația este validată",
        "✅ Capacitatea este corect dimensionată",
        "✅ Modelul este matur și sustenabil",
        "✅ Poziționarea optimă este anti-aglomerație, nu anti-preț"
    ]
    
    for item in verdict_items:
        st.write(item)
    
    st.markdown("---")
    st.markdown("""
    **Concluzie Strategică:**
    
    Analiza per locație confirmă că majoritatea sălilor mari din zonă funcționează constant la sau peste limita optimă de confort. 
    Noua sală nu concurează cu acestea pe volum sau preț, ci ocupă un gol clar de piață, definit de control, calitate și proximitate.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Dashboard creat pentru analiza potențialului spațiului fitness și recuperare</p>
    <p>📍 {address}, {city}</p>
</div>
""".format(address=LOCATION['address'], city=LOCATION['city']), unsafe_allow_html=True)

