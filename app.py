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
    LOCATION
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

# Distribuție abonamente
st.sidebar.subheader("Distribuție Abonamente (%)")
economic_pct = st.sidebar.slider(
    f"{SUBSCRIPTION_TYPES['economic']['name']} ({SUBSCRIPTION_TYPES['economic']['price']} RON)",
    0, 100, 40, 5
)
standard_pct = st.sidebar.slider(
    f"{SUBSCRIPTION_TYPES['standard']['name']} ({SUBSCRIPTION_TYPES['standard']['price']} RON)",
    0, 100, 50, 5
)
premium_pct = st.sidebar.slider(
    f"{SUBSCRIPTION_TYPES['premium']['name']} ({SUBSCRIPTION_TYPES['premium']['price']} RON)",
    0, 100, 10, 5
)

# Normalizare distribuție
total_pct = economic_pct + standard_pct + premium_pct
if total_pct == 0:
    economic_pct, standard_pct, premium_pct = 33.33, 33.33, 33.34
    total_pct = 100

subscription_distribution = {
    'economic': economic_pct / total_pct,
    'standard': standard_pct / total_pct,
    'premium': premium_pct / total_pct
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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Rezumat", 
    "💰 Venituri", 
    "👥 Clienți & Demografie", 
    "📈 Comparare Scenarii",
    "🗺️ Hartă Participare",
    "🎯 Campanie"
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
        dist_df = pd.DataFrame({
            'Tip Abonament': [SUBSCRIPTION_TYPES[k]['name'] for k in subscription_distribution.keys()],
            'Procentaj': [f"{v*100:.1f}%" for v in subscription_distribution.values()],
            'Preț (RON)': [SUBSCRIPTION_TYPES[k]['price'] for k in subscription_distribution.keys()]
        })
        st.dataframe(dist_df, use_container_width=True, hide_index=True)
    
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
                SUBSCRIPTION_TYPES['economic']['name']: '#2ecc71',
                SUBSCRIPTION_TYPES['standard']['name']: '#3498db',
                SUBSCRIPTION_TYPES['premium']['name']: '#e74c3c'
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
        revenue_df = pd.DataFrame({
            'Tip Abonament': [SUBSCRIPTION_TYPES[k]['name'] for k in ['economic', 'standard', 'premium']],
            'Venit (RON)': [
                revenue_data['economic'],
                revenue_data['standard'],
                revenue_data['premium']
            ]
        })
        
        fig_revenue = px.pie(
            revenue_df,
            values='Venit (RON)',
            names='Tip Abonament',
            title="Distribuție Venituri pe Tip Abonament",
            color='Tip Abonament',
            color_discrete_map={
                SUBSCRIPTION_TYPES['economic']['name']: '#2ecc71',
                SUBSCRIPTION_TYPES['standard']['name']: '#3498db',
                SUBSCRIPTION_TYPES['premium']['name']: '#e74c3c'
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
        revenue_detail = pd.DataFrame({
            'Tip Abonament': [SUBSCRIPTION_TYPES[k]['name'] for k in ['economic', 'standard', 'premium']],
            'Clienți': [
                revenue_data['clients']['economic'],
                revenue_data['clients']['standard'],
                revenue_data['clients']['premium']
            ],
            'Preț/Abonament (RON)': [
                SUBSCRIPTION_TYPES['economic']['price'],
                SUBSCRIPTION_TYPES['standard']['price'],
                SUBSCRIPTION_TYPES['premium']['price']
            ],
            'Venit Total (RON)': [
                revenue_data['economic'],
                revenue_data['standard'],
                revenue_data['premium']
            ]
        })
        revenue_detail.loc[len(revenue_detail)] = ['TOTAL', revenue_detail['Clienți'].sum(), '', revenue_data['total']]
        st.dataframe(revenue_detail, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Analiză Clienți & Demografie")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Necesar Clienți")
        clients_df = pd.DataFrame({
            'Tip Abonament': [SUBSCRIPTION_TYPES[k]['name'] for k in ['economic', 'standard', 'premium']],
            'Număr Clienți': [
                analysis['revenue']['clients']['economic'],
                analysis['revenue']['clients']['standard'],
                analysis['revenue']['clients']['premium']
            ]
        })
        
        fig_clients_detailed = px.bar(
            clients_df,
            x='Tip Abonament',
            y='Număr Clienți',
            text='Număr Clienți',
            color='Tip Abonament',
            color_discrete_map={
                SUBSCRIPTION_TYPES['economic']['name']: '#2ecc71',
                SUBSCRIPTION_TYPES['standard']['name']: '#3498db',
                SUBSCRIPTION_TYPES['premium']['name']: '#e74c3c'
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
    
    # Adaugă marker pentru locația salii
    folium.Marker(
        [center_lat, center_lon],
        popup=f"<b>💪 Sala Fitness & Recuperare</b><br>{LOCATION['address']}<br>{LOCATION['city']}",
        tooltip="Locația Salii",
        icon=folium.Icon(color='red', icon='info-sign')
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
                bottom: 50px; right: 50px; width: 200px; height: 180px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4 style="margin-top:0">Legendă Participare</h4>
    <p><span style="color:green">●</span> Ridicată (>120%)</p>
    <p><span style="color:blue">●</span> Medie (100%)</p>
    <p><span style="color:orange">●</span> Moderată (80%)</p>
    <p><span style="color:red">●</span> Redusă (<80%)</p>
    <p><span style="color:red">📍</span> Sala Fitness</p>
    <p><span style="color:#3186cc">○</span> Raza influență</p>
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

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Dashboard creat pentru analiza potențialului spațiului fitness și recuperare</p>
    <p>📍 {address}, {city}</p>
</div>
""".format(address=LOCATION['address'], city=LOCATION['city']), unsafe_allow_html=True)

