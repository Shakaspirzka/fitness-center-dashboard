"""
Modul pentru calculele de bază ale analizei potențialului spațiului fitness
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple


# Configurație spațiu
CAPACITY_PER_HOUR = 20  # oameni/ora
HOURS_PER_DAY = 10
DAYS_PER_WEEK = 7
WEEKS_PER_MONTH = 4.33  # medie

# Abonamente
SUBSCRIPTION_TYPES = {
    'economic': {
        'name': 'Economic',
        'price': 100,  # RON/lună
        'sessions': 10
    },
    'standard': {
        'name': 'Standard',
        'price': 150,  # RON/lună
        'sessions': None  # nelimitat
    },
    'premium': {
        'name': 'Premium',
        'price': 500,  # RON/lună
        'sessions': 10
    }
}

# Scenarii ocupare
OCCUPANCY_SCENARIOS = {
    'reduced': {
        'name': 'Redus',
        'min': 0.25,
        'max': 0.50
    },
    'medium': {
        'name': 'Mediu',
        'min': 0.50,
        'max': 0.75
    },
    'high': {
        'name': 'Ridicat',
        'min': 0.75,
        'max': 1.0
    }
}

# Locație
LOCATION = {
    'city': 'Bacau',
    'address': 'Aleea Prieteniei nr 14',
    'coordinates': (46.5712, 26.9244)  # coordonate aproximative Bacau
}

DESIRED_MONTHLY_REVENUE = 50000  # RON


def calculate_max_capacity() -> int:
    """Calculează capacitatea maximă lunară (număr de slot-uri)"""
    slots_per_day = CAPACITY_PER_HOUR * HOURS_PER_DAY
    slots_per_week = slots_per_day * DAYS_PER_WEEK
    slots_per_month = slots_per_week * WEEKS_PER_MONTH
    return int(slots_per_month)


def calculate_occupied_slots(occupancy_rate: float) -> int:
    """Calculează numărul de slot-uri ocupate pentru o rată de ocupare dată"""
    max_capacity = calculate_max_capacity()
    return int(max_capacity * occupancy_rate)


def calculate_clients_needed(
    occupancy_rate: float,
    subscription_distribution: Dict[str, float]
) -> Dict[str, int]:
    """
    Calculează numărul de clienți necesari pentru fiecare tip de abonament
    
    Args:
        occupancy_rate: Rata de ocupare (0-1)
        subscription_distribution: Dict cu procentajele pentru fiecare tip de abonament
                                  {'economic': 0.4, 'standard': 0.5, 'premium': 0.1}
    
    Returns:
        Dict cu numărul de clienți pentru fiecare tip
    """
    occupied_slots = calculate_occupied_slots(occupancy_rate)
    
    # Calculăm câte slot-uri sunt ocupate de fiecare tip de abonament
    economic_slots = occupied_slots * subscription_distribution.get('economic', 0)
    premium_slots = occupied_slots * subscription_distribution.get('premium', 0)
    standard_slots = occupied_slots * subscription_distribution.get('standard', 0)
    
    # Pentru abonamentele cu sesiuni limitate (economic și premium):
    # Calculăm câți clienți sunt necesari pentru a acoperi slot-urile
    # Presupunem că fiecare client folosește toate sesiunile sale într-o lună
    
    # Clienți economic: slot-uri / sesiuni per abonament
    if subscription_distribution.get('economic', 0) > 0:
        economic_clients = max(1, int(np.ceil(economic_slots / SUBSCRIPTION_TYPES['economic']['sessions'])))
    else:
        economic_clients = 0
    
    # Clienți premium: slot-uri / sesiuni per abonament
    if subscription_distribution.get('premium', 0) > 0:
        premium_clients = max(1, int(np.ceil(premium_slots / SUBSCRIPTION_TYPES['premium']['sessions'])))
    else:
        premium_clients = 0
    
    # Pentru abonamentul standard (nelimitat):
    # Presupunem că fiecare client vine în medie de 3 ori pe săptămână
    # Slot-uri pe săptămână = standard_slots / WEEKS_PER_MONTH
    # Clienți = slot-uri pe săptămână / vizite pe săptămână per client
    avg_visits_per_week = 3  # Presupunere: 3 vizite pe săptămână pentru abonament standard
    if subscription_distribution.get('standard', 0) > 0:
        slots_per_week = standard_slots / WEEKS_PER_MONTH
        standard_clients = max(1, int(np.ceil(slots_per_week / avg_visits_per_week)))
    else:
        standard_clients = 0
    
    return {
        'economic': economic_clients,
        'standard': standard_clients,
        'premium': premium_clients
    }


def calculate_monthly_revenue(
    occupancy_rate: float,
    subscription_distribution: Dict[str, float]
) -> Dict[str, float]:
    """
    Calculează veniturile lunare
    
    Returns:
        Dict cu venituri totale și pe tip de abonament
    """
    clients = calculate_clients_needed(occupancy_rate, subscription_distribution)
    
    revenue_economic = clients['economic'] * SUBSCRIPTION_TYPES['economic']['price']
    revenue_standard = clients['standard'] * SUBSCRIPTION_TYPES['standard']['price']
    revenue_premium = clients['premium'] * SUBSCRIPTION_TYPES['premium']['price']
    
    total_revenue = revenue_economic + revenue_standard + revenue_premium
    
    return {
        'total': total_revenue,
        'economic': revenue_economic,
        'standard': revenue_standard,
        'premium': revenue_premium,
        'clients': clients
    }


def calculate_influence_radius(
    total_clients_needed: int,
    participation_rate: float,
    population_density: float  # oameni/km²
) -> float:
    """
    Calculează raza de influență necesară (în km)
    
    Args:
        total_clients_needed: Numărul total de clienți necesari
        participation_rate: Rata de participare a populației (0-1, ex: 0.10 = 10%)
        population_density: Densitatea populației (oameni/km²)
    
    Returns:
        Raza de influență în km
    """
    if participation_rate == 0 or population_density == 0:
        return 0
    
    # Populația disponibilă per km²
    available_population_per_km2 = population_density * participation_rate
    
    # Suprafața necesară (km²)
    area_needed = total_clients_needed / available_population_per_km2
    
    # Raza (presupunând zonă circulară)
    radius = np.sqrt(area_needed / np.pi)
    
    return radius


def calculate_campaign_scale(
    total_clients_needed: int,
    participation_rate: float,
    population_density: float,
    conversion_rate: float = 0.05  # 5% conversie din cei interesați
) -> Dict[str, float]:
    """
    Calculează dimensiunea necesară a unei campanii la nivel de cartier
    
    Args:
        total_clients_needed: Numărul total de clienți necesari
        participation_rate: Rata de participare a populației
        population_density: Densitatea populației (oameni/km²)
        conversion_rate: Rata de conversie a campaniei (0-1)
    
    Returns:
        Dict cu informații despre campanie
    """
    radius = calculate_influence_radius(total_clients_needed, participation_rate, population_density)
    area = np.pi * radius ** 2
    total_population = area * population_density
    interested_population = total_population * participation_rate
    target_population = total_clients_needed / conversion_rate if conversion_rate > 0 else 0
    
    return {
        'radius_km': radius,
        'area_km2': area,
        'total_population': int(total_population),
        'interested_population': int(interested_population),
        'target_population': int(target_population),
        'conversion_rate': conversion_rate
    }


def get_scenario_analysis(
    scenario: str,
    subscription_distribution: Dict[str, float],
    participation_rate: float = 0.10,
    population_density: float = 1000
) -> Dict:
    """
    Obține analiza completă pentru un scenariu
    
    Args:
        scenario: 'reduced', 'medium', sau 'high'
        subscription_distribution: Distribuția abonamentelor
        participation_rate: Rata de participare (default 10%)
        population_density: Densitatea populației (default 1000 oameni/km²)
    
    Returns:
        Dict cu toate rezultatele analizei
    """
    scenario_config = OCCUPANCY_SCENARIOS[scenario]
    
    # Folosim rata medie pentru scenariu
    avg_occupancy = (scenario_config['min'] + scenario_config['max']) / 2
    
    # Calculează venituri
    revenue_data = calculate_monthly_revenue(avg_occupancy, subscription_distribution)
    
    # Calculează clienți totali
    total_clients = sum(revenue_data['clients'].values())
    
    # Calculează raza de influență
    radius = calculate_influence_radius(total_clients, participation_rate, population_density)
    
    # Calculează dimensiunea campaniei
    campaign_data = calculate_campaign_scale(total_clients, participation_rate, population_density)
    
    return {
        'scenario': scenario_config['name'],
        'occupancy_rate': avg_occupancy,
        'occupancy_percentage': f"{scenario_config['min']*100:.0f}% - {scenario_config['max']*100:.0f}%",
        'max_capacity': calculate_max_capacity(),
        'occupied_slots': calculate_occupied_slots(avg_occupancy),
        'revenue': revenue_data,
        'total_clients': total_clients,
        'influence_radius_km': radius,
        'campaign': campaign_data,
        'participation_rate': participation_rate,
        'population_density': population_density
    }


def compare_scenarios(
    subscription_distribution: Dict[str, float],
    participation_rate: float = 0.10,
    population_density: float = 1000
) -> pd.DataFrame:
    """
    Compară toate scenariile și returnează un DataFrame
    """
    results = []
    
    for scenario in ['reduced', 'medium', 'high']:
        analysis = get_scenario_analysis(scenario, subscription_distribution, participation_rate, population_density)
        results.append({
            'Scenariu': analysis['scenario'],
            'Ocupare': analysis['occupancy_percentage'],
            'Venit Total (RON)': analysis['revenue']['total'],
            'Clienți Totali': analysis['total_clients'],
            'Raza Influență (km)': round(analysis['influence_radius_km'], 2),
            'Populație Totală': analysis['campaign']['total_population'],
            'Populație Țintă': analysis['campaign']['target_population']
        })
    
    return pd.DataFrame(results)

