# Cod pentru tab-ul de analiză concurențială - de inserat în app.py înainte de footer

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
    
    competitors_df = pd.DataFrame(competitors)
    competitors_df['Tip'] = competitors_df['name']
    competitors_df['Capacitate Simultană'] = competitors_df['capacity']
    competitors_df['Abonați Activi'] = competitors_df['members']
    competitors_df['Model'] = competitors_df['model']
    competitors_df['Limitări'] = competitors_df['limitation']
    
    # Adaugă și noastre date
    our_data = {
        'Tip': 'Sala Noastră (Aleea Prieteniei)',
        'Capacitate Simultană': CAPACITY_PER_HOUR,
        'Abonați Activi': analysis['total_clients'],
        'Model': positioning['positioning'],
        'Limitări': 'N/A - Model optimizat',
        'color': 'purple'
    }
    
    display_df = competitors_df[['Tip', 'Capacitate Simultană', 'Abonați Activi', 'Model', 'Limitări']].copy()
    
    # Grafic comparativ capacitate
    fig_capacity = go.Figure()
    
    colors_map = {'red': '#e74c3c', 'blue': '#3498db', 'green': '#2ecc71', 'purple': '#9b59b6'}
    
    for idx, comp in enumerate(competitors):
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
    
    # Secțiune 6: Verdict Final
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
