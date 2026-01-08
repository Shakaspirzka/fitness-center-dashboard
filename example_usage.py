"""
Exemplu de utilizare a modulului de calcule programatic
"""
from calculations import (
    get_scenario_analysis,
    compare_scenarios,
    calculate_monthly_revenue,
    calculate_influence_radius
)

# Exemplu 1: Analiză pentru un scenariu specific
print("=" * 60)
print("EXEMPLU 1: Analiză Scenariu Mediu")
print("=" * 60)

subscription_distribution = {
    'economic': 0.4,   # 40% clienți cu abonament economic
    'standard': 0.5,   # 50% clienți cu abonament standard
    'premium': 0.1     # 10% clienți cu abonament premium
}

analysis = get_scenario_analysis(
    scenario='medium',
    subscription_distribution=subscription_distribution,
    participation_rate=0.10,  # 10% din populație
    population_density=1000   # 1000 oameni/km²
)

print(f"\nScenariu: {analysis['scenario']}")
print(f"Ocupare: {analysis['occupancy_percentage']}")
print(f"\nVenituri:")
print(f"  Total: {analysis['revenue']['total']:,.0f} RON")
print(f"  Economic: {analysis['revenue']['economic']:,.0f} RON")
print(f"  Standard: {analysis['revenue']['standard']:,.0f} RON")
print(f"  Premium: {analysis['revenue']['premium']:,.0f} RON")
print(f"\nClienți:")
print(f"  Total: {analysis['total_clients']}")
print(f"  Economic: {analysis['revenue']['clients']['economic']}")
print(f"  Standard: {analysis['revenue']['clients']['standard']}")
print(f"  Premium: {analysis['revenue']['clients']['premium']}")
print(f"\nRaza de influență: {analysis['influence_radius_km']:.2f} km")
print(f"Populație totală în zonă: {analysis['campaign']['total_population']:,}")

# Exemplu 2: Comparare toate scenariile
print("\n" + "=" * 60)
print("EXEMPLU 2: Comparare Toate Scenariile")
print("=" * 60)

comparison = compare_scenarios(
    subscription_distribution,
    participation_rate=0.10,
    population_density=1000
)

print("\n" + comparison.to_string(index=False))

# Exemplu 3: Testare diferite rate de participare
print("\n" + "=" * 60)
print("EXEMPLU 3: Impact Rata Participare")
print("=" * 60)

for participation in [0.05, 0.10, 0.15, 0.20]:
    radius = calculate_influence_radius(
        total_clients_needed=analysis['total_clients'],
        participation_rate=participation,
        population_density=1000
    )
    print(f"Rata participare {participation*100:.0f}%: Raza = {radius:.2f} km")

# Exemplu 4: Testare diferite densități de populație
print("\n" + "=" * 60)
print("EXEMPLU 4: Impact Densitate Populație")
print("=" * 60)

for density in [500, 1000, 2000, 3000]:
    radius = calculate_influence_radius(
        total_clients_needed=analysis['total_clients'],
        participation_rate=0.10,
        population_density=density
    )
    print(f"Densitate {density:,} oameni/km²: Raza = {radius:.2f} km")

print("\n" + "=" * 60)
print("Analiză completă! Folosește dashboard-ul pentru interacțiune vizuală.")
print("=" * 60)

