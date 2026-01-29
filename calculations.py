"""
Modul pentru calculele de bază ale analizei potențialului spațiului fitness
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple


# Configurație spațiu - Mobilis Vita
# Sala de fitness: 65-70 mp
# Sala de clase: 50 mp
# Total: ~115-120 mp
FITNESS_AREA_M2 = 67.5  # medie între 65-70 mp
CLASSES_AREA_M2 = 50
TOTAL_AREA_M2 = FITNESS_AREA_M2 + CLASSES_AREA_M2  # ~117.5 mp

# Capacitate ajustată pentru spațiu mai mic și model entry-point, family-friendly
# Nu pentru pasionați de fitness, ci pentru oameni care încep sau revin la mișcare
CAPACITY_PER_HOUR = 12  # oameni/ora (redus pentru confort și abordare personalizată)
HOURS_PER_DAY = 10
DAYS_PER_WEEK = 7
WEEKS_PER_MONTH = 4.33  # medie

# Abonamente - Mobilis Vita: Entry-point pentru mișcare, family-friendly
# Model: Nu pentru pasionați de fitness, ci pentru oameni care încep sau revin la mișcare
SUBSCRIPTION_TYPES = {
    'clase_miscare': {
        'name': 'Clase de Mișcare',
        'price': 180,  # RON/lună - serviciul principal
        'sessions': None,  # nelimitat la clase
        'description': 'Acces nelimitat la clase de mișcare (entry-point principal)'
    },
    'fitness_access': {
        'name': 'Acces Sala Fitness',
        'price': 120,  # RON/lună - serviciu secundar
        'sessions': None,  # nelimitat dar spațiu limitat
        'description': 'Acces la sala de fitness (65-70mp), serviciu secundar'
    },
    'complet': {
        'name': 'Abonament Complet',
        'price': 250,  # RON/lună - clase + fitness
        'sessions': None,  # nelimitat
        'description': 'Acces complet: clase de mișcare + sala fitness'
    },
    'family': {
        'name': 'Abonament Family',
        'price': 400,  # RON/lună - pentru 2-3 persoane (copii, părinți, bunici)
        'sessions': None,  # nelimitat pentru toată familia
        'description': 'Family-friendly: pentru copii, mămici, bunici'
    },
    'masaj': {
        'name': 'Masaj (per sesiune)',
        'price': 100,  # RON/sesiune
        'sessions': 1,  # per sesiune
        'description': 'Masaj de relaxare sau terapeutic',
        'is_session_based': True
    },
    'kineto': {
        'name': 'Kineto / Reabilitare (per sesiune)',
        'price': 120,  # RON/sesiune
        'sessions': 1,  # per sesiune
        'description': 'Kinetoterapie și reabilitare',
        'is_session_based': True
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
    conversion_rate: float = 0.05,  # 5% conversie din cei atinși
    coverage_rate: float = 0.50  # 50% din populația interesată trebuie atinsă
) -> Dict[str, float]:
    """
    Calculează dimensiunea necesară a unei campanii la nivel de cartier
    
    Logica corectă:
    1. Calculăm câți oameni trebuie atinși de campanie: total_clients_needed / conversion_rate
    2. Calculăm câtă populație interesată avem nevoie: people_to_reach / coverage_rate
    3. Calculăm câtă populație totală avem nevoie: interested_population_needed / participation_rate
    4. Calculăm suprafața necesară: total_population_needed / population_density
    5. Calculăm raza necesară: sqrt(area_needed / π)
    
    Args:
        total_clients_needed: Numărul total de clienți necesari
        participation_rate: Rata de participare a populației (0-1)
        population_density: Densitatea populației (oameni/km²)
        conversion_rate: Rata de conversie a campaniei (0-1) - ce % din cei atinși devin clienți
        coverage_rate: Rata de acoperire (0-1) - ce % din populația interesată trebuie atinsă
    
    Returns:
        Dict cu informații despre campanie
    """
    if conversion_rate == 0 or participation_rate == 0 or population_density == 0 or coverage_rate == 0:
        return {
            'radius_km': 0,
            'area_km2': 0,
            'total_population': 0,
            'interested_population': 0,
            'people_to_reach': 0,
            'coverage_rate': coverage_rate,
            'conversion_rate': conversion_rate
        }
    
    # Pasul 1: Câți oameni trebuie atinși de campanie pentru a obține clienții necesari
    people_to_reach_needed = total_clients_needed / conversion_rate
    
    # Pasul 2: Câtă populație interesată avem nevoie pentru a atinge numărul necesar
    # Dacă vrem să atingem X oameni și rata de acoperire este Y%, atunci avem nevoie de X/Y oameni interesați
    interested_population_needed = people_to_reach_needed / coverage_rate
    
    # Pasul 3: Calculăm câtă populație totală avem nevoie
    # pentru a avea suficienți oameni interesați
    total_population_needed = interested_population_needed / participation_rate
    
    # Pasul 4: Calculăm suprafața necesară
    area_needed = total_population_needed / population_density
    
    # Pasul 5: Calculăm raza necesară (presupunând zonă circulară)
    radius = np.sqrt(area_needed / np.pi)
    
    # Acum calculăm valorile finale bazate pe raza corectă
    area = np.pi * radius ** 2
    total_population = area * population_density
    interested_population = total_population * participation_rate
    
    # Populația de atins este procentul din populația interesată definit de coverage_rate
    people_to_reach = int(interested_population * coverage_rate)
    
    return {
        'radius_km': radius,
        'area_km2': area,
        'total_population': int(total_population),
        'interested_population': int(interested_population),
        'people_to_reach': people_to_reach,
        'coverage_rate': coverage_rate,
        'conversion_rate': conversion_rate
    }


def get_scenario_analysis(
    scenario: str,
    subscription_distribution: Dict[str, float],
    participation_rate: float = 0.10,
    population_density: float = 1000,
    conversion_rate: float = 0.05,
    coverage_rate: float = 0.50
) -> Dict:
    """
    Obține analiza completă pentru un scenariu
    
    Args:
        scenario: 'reduced', 'medium', sau 'high'
        subscription_distribution: Distribuția abonamentelor
        participation_rate: Rata de participare (default 10%)
        population_density: Densitatea populației (default 1000 oameni/km²)
        conversion_rate: Rata de conversie a campaniei (default 5%)
    
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
    
    # Calculează dimensiunea campaniei (care include raza corectă calculată cu conversie și acoperire)
    campaign_data = calculate_campaign_scale(total_clients, participation_rate, population_density, conversion_rate, coverage_rate)
    
    # Folosim raza din campanie (care este calculată corect ținând cont de conversie)
    radius = campaign_data['radius_km']
    
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
    population_density: float = 1000,
    conversion_rate: float = 0.05,
    coverage_rate: float = 0.50
) -> pd.DataFrame:
    """
    Compară toate scenariile și returnează un DataFrame
    """
    results = []
    
    for scenario in ['reduced', 'medium', 'high']:
        analysis = get_scenario_analysis(scenario, subscription_distribution, participation_rate, population_density, conversion_rate, coverage_rate)
        results.append({
            'Scenariu': analysis['scenario'],
            'Ocupare': analysis['occupancy_percentage'],
            'Venit Total (RON)': analysis['revenue']['total'],
            'Clienți Totali': analysis['total_clients'],
            'Raza Influență (km)': round(analysis['influence_radius_km'], 2),
            'Populație Totală': analysis['campaign']['total_population'],
            'Populație de Atins': analysis['campaign']['people_to_reach']
        })
    
    return pd.DataFrame(results)


# Previziuni financiare - Mobilis Vita (din fișierul Word)
FINANCIAL_FORECAST = {
    'spaces': [
        {
            'id': 'sala_clase',
            'name': 'Sală clase',
            'hours_per_day': 12,
            'revenue_per_hour': 100,  # RON
            'days_per_month': 24,
            'occupancy_pessimistic': 0.30,  # 30%
            'occupancy_maximum': 1.00,  # 100%
            'monthly_revenue_pessimistic': 8640,  # RON
            'monthly_revenue_maximum': 28800  # RON
        },
        {
            'id': 'sala_fitness',
            'name': 'Sală fitness',
            'hours_per_day': 12,
            'revenue_per_hour': 80,  # RON
            'days_per_month': 24,
            'occupancy_pessimistic': 0.30,  # 30%
            'occupancy_maximum': 1.00,  # 100%
            'monthly_revenue_pessimistic': 6912,  # RON
            'monthly_revenue_maximum': 23040  # RON
        },
        {
            'id': 'sala_terapii_1',
            'name': 'Sală terapii 1',
            'hours_per_day': 12,
            'revenue_per_hour': 80,  # RON
            'days_per_month': 24,
            'occupancy_pessimistic': 0.30,  # 30%
            'occupancy_maximum': 1.00,  # 100%
            'monthly_revenue_pessimistic': 6912,  # RON
            'monthly_revenue_maximum': 23040  # RON
        },
        {
            'id': 'sala_terapii_2',
            'name': 'Sală terapii 2',
            'hours_per_day': 12,
            'revenue_per_hour': 80,  # RON
            'days_per_month': 24,
            'occupancy_pessimistic': 0.30,  # 30%
            'occupancy_maximum': 1.00,  # 100%
            'monthly_revenue_pessimistic': 6912,  # RON
            'monthly_revenue_maximum': 23040  # RON
        },
        {
            'id': 'sala_terapii_3',
            'name': 'Sală terapii 3',
            'hours_per_day': 12,
            'revenue_per_hour': 80,  # RON
            'days_per_month': 24,
            'occupancy_pessimistic': 0.30,  # 30%
            'occupancy_maximum': 1.00,  # 100%
            'monthly_revenue_pessimistic': 6912,  # RON
            'monthly_revenue_maximum': 23040  # RON
        }
    ],
    'capacity': {
        'max_per_hour': 20,  # 20-22 persoane max/oră
        'breakdown': {
            'terapii_individuale': 2,
            'sala_clase': 12,
            'sala_fitness': 6  # 6-8 persoane
        }
    },
    'expenses': {
        'salaries': {
            'high_salary_count': 3,
            'high_salary_amount': 4850,  # RON/lună
            'low_salary_count': 1,
            'low_salary_amount': 2800,  # RON/lună
            'total_monthly': 3 * 4850 + 1 * 2800  # 17350 RON
        },
        'rent': {
            'amount_eur': 900,
            'exchange_rate': 5.0,  # RON/EUR (ajustabil)
            'amount_ron': 900 * 5.0  # 4500 RON (ajustabil)
        },
        'utilities': {
            'winter_min': 1500,  # RON/lună
            'winter_max': 2000,  # RON/lună
            'average': 1750  # RON/lună
        }
    }
}

def get_financial_forecast_summary() -> Dict:
    """
    Returnează un rezumat al previziunilor financiare
    """
    total_revenue_pessimistic = sum(space['monthly_revenue_pessimistic'] for space in FINANCIAL_FORECAST['spaces'])
    total_revenue_maximum = sum(space['monthly_revenue_maximum'] for space in FINANCIAL_FORECAST['spaces'])
    
    total_expenses = (
        FINANCIAL_FORECAST['expenses']['salaries']['total_monthly'] +
        FINANCIAL_FORECAST['expenses']['rent']['amount_ron'] +
        FINANCIAL_FORECAST['expenses']['utilities']['average']
    )
    
    profit_pessimistic = total_revenue_pessimistic - total_expenses
    profit_maximum = total_revenue_maximum - total_expenses
    
    return {
        'total_revenue': {
            'pessimistic': total_revenue_pessimistic,
            'maximum': total_revenue_maximum
        },
        'total_expenses': total_expenses,
        'profit': {
            'pessimistic': profit_pessimistic,
            'maximum': profit_maximum
        },
        'break_even_occupancy': total_expenses / total_revenue_maximum if total_revenue_maximum > 0 else 0,
        'spaces': FINANCIAL_FORECAST['spaces'],
        'expenses_detail': FINANCIAL_FORECAST['expenses'],
        'capacity': FINANCIAL_FORECAST['capacity']
    }

def get_financial_forecast_by_space() -> pd.DataFrame:
    """
    Returnează un DataFrame cu previziunile financiare pe spațiu
    """
    data = []
    for space in FINANCIAL_FORECAST['spaces']:
        data.append({
            'Spațiu': space['name'],
            'Ore/Zi': space['hours_per_day'],
            'Venit Mediu/Oră (RON)': space['revenue_per_hour'],
            'Zile/Lună': space['days_per_month'],
            'Ocupare Pesimist (%)': f"{space['occupancy_pessimistic']*100:.0f}%",
            'Ocupare Maxim (%)': f"{space['occupancy_maximum']*100:.0f}%",
            'Venit/Lună Pesimist (RON)': space['monthly_revenue_pessimistic'],
            'Venit/Lună Maxim (RON)': space['monthly_revenue_maximum']
        })
    
    # Adaugă total
    total_pessimistic = sum(s['monthly_revenue_pessimistic'] for s in FINANCIAL_FORECAST['spaces'])
    total_maximum = sum(s['monthly_revenue_maximum'] for s in FINANCIAL_FORECAST['spaces'])
    
    data.append({
        'Spațiu': 'TOTAL',
        'Ore/Zi': '',
        'Venit Mediu/Oră (RON)': '',
        'Zile/Lună': '',
        'Ocupare Pesimist (%)': '',
        'Ocupare Maxim (%)': '',
        'Venit/Lună Pesimist (RON)': total_pessimistic,
        'Venit/Lună Maxim (RON)': total_maximum
    })
    
    return pd.DataFrame(data)

