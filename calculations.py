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

# Abonamente - Structură extinsă conform analizei concurențiale
SUBSCRIPTION_TYPES = {
    'basic': {
        'name': 'Basic Controlat',
        'price': 140,  # RON/lună (130-150 RON)
        'sessions': None,  # nelimitat dar controlat
        'description': 'Atragere public local, acces controlat'
    },
    'standard': {
        'name': 'Standard',
        'price': 200,  # RON/lună (180-220 RON)
        'sessions': None,  # nelimitat
        'description': 'Bază financiară, acces complet'
    },
    'premium': {
        'name': 'Premium / Recovery',
        'price': 500,  # RON/lună (400-600 RON)
        'sessions': None,  # nelimitat cu servicii speciale
        'description': 'Diferențiator, servicii de recuperare'
    },
    'pt_session': {
        'name': 'PT / Reabilitare (per sesiune)',
        'price': 125,  # RON/sesiune (100-150 RON)
        'sessions': 1,  # per sesiune
        'description': 'Marjă ridicată, servicii personalizate',
        'is_session_based': True  # se plătește per sesiune, nu lunar
    }
}

# Concurenți
COMPETITORS = {
    'redgym': {
        'name': 'RedGym',
        'capacity_simultaneous': 150,  # 120-180
        'active_members': 1000,  # 800-1200
        'model': 'Volum mare, ofertă variată',
        'limitation': 'Supraaglomerare la orele de vârf, experiență impersonală',
        'proximity': 'Ridicată',
        'color': 'red'
    },
    'citygym': {
        'name': 'City Gym / 18GYM',
        'capacity_simultaneous': 240,  # 180-300
        'active_members': 1250,  # 1000-1500
        'model': 'Low-mid cost, acces extins (24/7)',
        'limitation': 'Crowding sever, lipsă personalizare',
        'proximity': 'Zona mall',
        'color': 'blue'
    },
    'local_small': {
        'name': 'Săli Locale Mici',
        'capacity_simultaneous': 45,  # 30-60
        'active_members': 225,  # 150-300
        'model': 'Comunitate restrânsă',
        'limitation': 'Imposibilitate de scalare, dotări limitate',
        'proximity': 'Local',
        'color': 'green'
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
    'address': 'Strada Prieteniei nr 14',
    'coordinates': (46.5700, 26.9130)  # Coordonate corecte pentru Strada Prieteniei nr 14, Bacău (lângă Carrefour Express, în spatele Școlii Gimnaziale Mihai Drăgan)
}

# Coordonate concurenți (din analiza concurențială)
# Coordonate corectate pentru a reflecta pozițiile reale pe hartă
COMPETITOR_LOCATIONS = {
    'redgym': {
        'name': 'RedGym',
        'coordinates': (46.5710, 26.9080),  # Zona centrală Bacău, corectat
        'color': 'red',
        'icon': 'dumbbell'
    },
    'citygym': {
        'name': 'City Gym Arena Mall',
        'coordinates': (46.5760, 26.9220),  # Zona mall/comercială, corectat
        'color': 'blue',
        'icon': 'shopping-cart'
    },
    'gymnastic_club': {
        'name': 'Gymnastic Club',
        'coordinates': (46.5660, 26.9020),  # Zona sud-vest, corectat
        'color': 'orange',
        'icon': 'star'
    },
    'pole_fitness': {
        'name': 'Pole Fitness Bacau',
        'coordinates': (46.5730, 26.9170),  # Zona centrală, corectat
        'color': 'purple',
        'icon': 'heart'
    },
    'q_fitt': {
        'name': 'Q Fitt Bacau',
        'coordinates': (46.5740, 26.9200),  # Zona centrală, corectat
        'color': 'darkred',
        'icon': 'fire'
    }
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
        subscription_distribution: Dict cu procentajele pentru fiecare tip de serviciu
                                  Toate procentajele formează 100% (inclusiv PT)
    
    Returns:
        Dict cu numărul de clienți/sesiuni pentru fiecare tip
    """
    occupied_slots = calculate_occupied_slots(occupancy_rate)
    
    clients = {}
    
    # Pentru fiecare tip de serviciu (inclusiv PT)
    for sub_type, pct in subscription_distribution.items():
        if pct > 0 and sub_type in SUBSCRIPTION_TYPES:
            sub_info = SUBSCRIPTION_TYPES[sub_type]
            # Slot-uri ocupate de acest tip = slot-uri totale × procentaj
            sub_slots = occupied_slots * pct
            
            if sub_info.get('is_session_based', False):
                # PT/Reabilitare: fiecare slot = 1 sesiune
                # Numărul de sesiuni = numărul de slot-uri ocupate
                num_sessions = max(0, int(np.round(sub_slots)))
                # Pentru a calcula clienți: presupunem că fiecare client face în medie 4-6 sesiuni/lună
                # Folosim 5 sesiuni/lună per client ca medie pentru reabilitare
                avg_sessions_per_client = 5
                num_clients = max(0, int(np.ceil(num_sessions / avg_sessions_per_client)))
                # Returnăm numărul de clienți, nu sesiuni (pentru consistență cu celelalte servicii)
                clients[sub_type] = num_clients
                # Stocăm și numărul de sesiuni pentru calculele de venit
                clients[f'{sub_type}_sessions'] = num_sessions
            elif sub_info.get('sessions') is None:
                # Abonamente nelimitate (standard, basic, premium)
                # Presupunem 3 vizite pe săptămână per client
                avg_visits_per_week = 3
                slots_per_week = sub_slots / WEEKS_PER_MONTH
                num_clients = max(0, int(np.ceil(slots_per_week / avg_visits_per_week)))
                clients[sub_type] = num_clients
            else:
                # Abonamente cu sesiuni limitate (dacă ar exista)
                num_clients = max(0, int(np.ceil(sub_slots / sub_info['sessions'])))
                clients[sub_type] = num_clients
        else:
            clients[sub_type] = 0
    
    return clients


def calculate_monthly_revenue(
    occupancy_rate: float,
    subscription_distribution: Dict[str, float]
) -> Dict[str, float]:
    """
    Calculează veniturile lunare
    
    Returns:
        Dict cu venituri totale și pe tip de serviciu
    """
    clients = calculate_clients_needed(occupancy_rate, subscription_distribution)
    
    revenues = {}
    total_revenue = 0
    
    # Calculează venituri pentru fiecare tip de abonament
    for sub_type, num_clients in clients.items():
        # Ignoră cheile care sunt doar pentru sesiuni (ex: 'pt_session_sessions')
        if sub_type.endswith('_sessions'):
            continue
            
        if sub_type in SUBSCRIPTION_TYPES and num_clients > 0:
            sub_info = SUBSCRIPTION_TYPES[sub_type]
            if sub_info.get('is_session_based', False):
                # PT/Reabilitare: se plătește per sesiune
                # Folosim numărul de sesiuni, nu clienți
                num_sessions = clients.get(f'{sub_type}_sessions', num_clients * 5)  # Fallback: 5 sesiuni per client
                revenues[sub_type] = num_sessions * sub_info['price']
            else:
                # Abonamente lunare
                revenues[sub_type] = num_clients * sub_info['price']
            total_revenue += revenues[sub_type]
        else:
            revenues[sub_type] = 0
    
    revenues['total'] = total_revenue
    revenues['clients'] = clients
    
    return revenues


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

