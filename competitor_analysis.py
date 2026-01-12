"""
Analiză concurențială și poziționare strategică
"""
from calculations import COMPETITORS, CAPACITY_PER_HOUR, HOURS_PER_DAY, calculate_max_capacity
from typing import Dict, List

# Date despre suprafață și layout pentru fiecare concurent
COMPETITOR_DETAILS = {
    'redgym': {
        'name': 'RedGym',
        'locations': [
            {
                'name': 'RedGym Standard',
                'area_m2': 600,
                'capacity_simultaneous': 140,
                'm2_per_person': 600 / 140,
                'experience': 'Aglomerat',
                'color': 'red'
            },
            {
                'name': 'RedGym Premium',
                'area_m2': 800,
                'capacity_simultaneous': 160,
                'm2_per_person': 800 / 160,
                'experience': 'Aglomerat',
                'color': 'red'
            }
        ],
        'avg_price': 150,
        'members': 1000,
        'monthly_revenue': 150000,
        'revenue_per_m2': 150000 / 1200  # media dintre cele 2 locații
    },
    'citygym': {
        'name': 'City Gym / 18GYM',
        'locations': [
            {
                'name': 'City Gym Mall',
                'area_m2': 1400,
                'capacity_simultaneous': 260,
                'm2_per_person': 1400 / 260,
                'experience': 'Foarte aglomerat',
                'color': 'blue'
            },
            {
                'name': '18GYM Central',
                'area_m2': 1500,
                'capacity_simultaneous': 240,
                'm2_per_person': 1500 / 240,
                'experience': 'Suportabil',
                'color': 'blue'
            }
        ],
        'avg_price': 150,
        'members': 1250,
        'monthly_revenue': 187500,
        'revenue_per_m2': 187500 / 1450  # media
    },
    'local_small': {
        'name': 'Săli Locale Mici',
        'locations': [
            {
                'name': 'Sală Locală Mică',
                'area_m2': 300,
                'capacity_simultaneous': 50,
                'm2_per_person': 300 / 50,
                'experience': 'OK',
                'color': 'green'
            }
        ],
        'avg_price': 130,
        'members': 225,
        'monthly_revenue': 29250,
        'revenue_per_m2': 29250 / 300
    }
}

# Layout recomandat pentru sala noastră
OUR_RECOMMENDED_LAYOUT = {
    'total_area_m2': 400,  # 350-450 mp
    'distribution': {
        'forță_funcțional': {'percentage': 57.5, 'm2': 230, 'description': 'Forță / Funcțional'},
        'cardio': {'percentage': 15, 'm2': 60, 'description': 'Cardio'},
        'recuperare': {'percentage': 10, 'm2': 40, 'description': 'Recuperare / Stretching / Postural'},
        'circulații': {'percentage': 10, 'm2': 40, 'description': 'Circulații (FOARTE IMPORTANT)'},
        'vestiare_depozit': {'percentage': 7.5, 'm2': 30, 'description': 'Vestiare / Depozit'}
    },
    'target_capacity': {'min': 40, 'max': 60, 'optimal': 50},
    'm2_per_person_range': {'min': 8, 'max': 11, 'optimal': 8.5}
}

# Praguri de confort mp/om
COMFORT_THRESHOLDS = {
    'congested': {'max': 6, 'label': 'Aglomerat'},
    'acceptable': {'min': 6, 'max': 10, 'label': 'Acceptabil'},
    'premium': {'min': 12, 'label': 'Premium / Control'}
}

def get_competitive_positioning() -> dict:
    """
    Returnează analiza poziționării competitive
    """
    our_capacity = CAPACITY_PER_HOUR
    our_max_monthly = calculate_max_capacity()
    
    return {
        'our_capacity_simultaneous': our_capacity,
        'our_max_monthly_slots': our_max_monthly,
        'positioning': 'Sală controlată, fără haos, orientată spre rezultate reale',
        'key_advantages': [
            'Dimensiune medie optimă',
            'Poziționare mid-premium',
            'Control strict al capacității',
            'Experiență calmă și predictibilă',
            'Relație personală',
            'Servicii de recuperare și postural',
            'Proximitate (acces pietonal)'
        ],
        'what_we_dont_do': [
            'Nu concurează pe preț minim',
            'Nu concurează pe suprafață',
            'Nu concurează pe număr de aparate',
            'Nu folosește modelul 24/7 orientat exclusiv pe volum'
        ],
        'optimal_capacity': {
            'simultaneous': '40-60 persoane',
            'launch_occupancy': '30-40%',
            'mature_occupancy': '55-65%',
            'warning_threshold': '70% (depășirea afectează experiența)'
        },
        'influence_radius': {
            'estimated': '~1 km',
            'primary_zone': '60% din clienți din primii 500-700m',
            'secondary_zone': '40% prin recomandări și retenție'
        }
    }

def get_competitors_comparison() -> list:
    """
    Returnează lista de concurenți pentru comparație
    """
    competitors_list = []
    for key, comp in COMPETITORS.items():
        competitors_list.append({
            'name': comp['name'],
            'capacity': comp['capacity_simultaneous'],
            'members': comp['active_members'],
            'model': comp['model'],
            'limitation': comp['limitation'],
            'proximity': comp['proximity'],
            'color': comp['color']
        })
    return competitors_list

def calculate_market_position(our_clients: int, our_capacity: int) -> dict:
    """
    Calculează poziționarea în piață relativ la concurenți
    """
    total_competitor_capacity = sum(c['capacity'] for c in get_competitors_comparison())
    total_competitor_members = sum(c['members'] for c in get_competitors_comparison())
    
    our_market_share_capacity = (our_capacity / (total_competitor_capacity + our_capacity)) * 100
    our_market_share_members = (our_clients / (total_competitor_members + our_clients)) * 100
    
    return {
        'our_capacity': our_capacity,
        'total_competitor_capacity': total_competitor_capacity,
        'market_share_capacity_pct': round(our_market_share_capacity, 1),
        'our_members': our_clients,
        'total_competitor_members': total_competitor_members,
        'market_share_members_pct': round(our_market_share_members, 1),
        'positioning_note': 'Poziționare optimă: anti-aglomerație, nu anti-preț'
    }

def get_layout_comparison(our_area_m2: float = 400, our_capacity: int = 50) -> List[Dict]:
    """
    Returnează comparația layout (mp/om) pentru toate locațiile
    """
    comparison = []
    
    # Adaugă toate locațiile concurenților
    for comp_key, comp_data in COMPETITOR_DETAILS.items():
        for location in comp_data['locations']:
            comparison.append({
                'Locație': location['name'],
                'Suprafață (mp)': location['area_m2'],
                'Oameni Simultan': location['capacity_simultaneous'],
                'mp/om': round(location['m2_per_person'], 1),
                'Experiență': location['experience'],
                'Tip': 'Concurent',
                'Color': location['color']
            })
    
    # Adaugă sala noastră
    our_m2_per_person = our_area_m2 / our_capacity
    experience = 'Clar diferențiator'
    if our_m2_per_person < 6:
        experience = 'Aglomerat'
    elif our_m2_per_person < 8:
        experience = 'Acceptabil'
    elif our_m2_per_person < 12:
        experience = 'Premium / Control'
    else:
        experience = 'Clar diferențiator'
    
    comparison.append({
        'Locație': 'Sala Noastră (Aleea Prieteniei)',
        'Suprafață (mp)': our_area_m2,
        'Oameni Simultan': our_capacity,
        'mp/om': round(our_m2_per_person, 1),
        'Experiență': experience,
        'Tip': 'Noi',
        'Color': 'purple'
    })
    
    return comparison

def get_recommended_layout() -> Dict:
    """
    Returnează layout-ul recomandat pentru sala noastră
    """
    return OUR_RECOMMENDED_LAYOUT

def simulate_new_redgym_impact() -> Dict:
    """
    Simulează impactul dacă RedGym deschide o nouă locație
    """
    return {
        'scenario': 'RedGym deschide sală nouă la 1-2 km',
        'assumptions': {
            'capacity': '700-900 abonați',
            'price': 'Similar',
            'area': 'Similară'
        },
        'what_doesnt_happen': [
            'Nu "fură" clienții tăi direcți',
            'Nu scade cererea totală',
            'Nu rezolvă problema aglomerației (doar o mută)'
        ],
        'what_happens': {
            'effect_1_fragmentation': {
                'title': 'Efectul 1 - Fragmentare',
                'description': 'O parte din clienți migrează',
                'details': [
                    'DAR: modelul rămâne de volum',
                    'Aglomerarea revine în 3-6 luni'
                ]
            },
            'effect_2_education': {
                'title': 'Efectul 2 - Educație de Piață',
                'description': 'Mai mulți oameni intră în fitness',
                'details': [
                    'Cresc așteptările',
                    'Oamenii încep să caute: mai aproape, mai liber, mai personal',
                    'Sala ta devine "next step" natural'
                ]
            }
        },
        'impact_estimates': {
            'without_new_redgym': {
                'total_demand': '100%',
                'volume_pressure': 'Mare',
                'our_advantage': 'Bun'
            },
            'with_new_redgym': {
                'total_demand': '115-125%',
                'volume_pressure': 'Și mai mare',
                'our_advantage': 'FOARTE BUN'
            }
        },
        'paradox': 'Deschiderea unei săli mari te ajută, dacă NU concurezi pe volum.'
    }

def calculate_profitability_comparison(our_revenue: float, our_clients: int, our_area_m2: float = 400) -> Dict:
    """
    Calculează comparația de profitabilitate: Profit/abonat vs Profit/mp
    """
    # Date pentru săli mari (media RedGym + CityGym)
    big_gym_avg = {
        'members': 1125,  # media dintre 1000 și 1250
        'avg_price': 150,
        'monthly_revenue': 168750,  # media
        'area_m2': 1325,  # media
        'revenue_per_m2': 168750 / 1325
    }
    
    # Date pentru sala noastră
    our_avg_price = our_revenue / our_clients if our_clients > 0 else 0
    our_revenue_per_m2 = our_revenue / our_area_m2 if our_area_m2 > 0 else 0
    
    return {
        'big_gym': {
            'members': big_gym_avg['members'],
            'avg_price': big_gym_avg['avg_price'],
            'monthly_revenue': big_gym_avg['monthly_revenue'],
            'area_m2': big_gym_avg['area_m2'],
            'revenue_per_m2': round(big_gym_avg['revenue_per_m2'], 2)
        },
        'our_gym': {
            'members': our_clients,
            'avg_price': round(our_avg_price, 2),
            'monthly_revenue': round(our_revenue, 2),
            'area_m2': our_area_m2,
            'revenue_per_m2': round(our_revenue_per_m2, 2)
        },
        'comparison': {
            'profit_per_member': {
                'big_gym': 'Mic',
                'our_gym': 'Mediu-Mare',
                'note': 'Sala noastră are profit mai mare per abonat'
            },
            'profit_per_m2': {
                'big_gym': 'Mediu',
                'our_gym': 'Mare',
                'note': 'Sala noastră generează mai mult venit pe mp'
            },
            'volatility': {
                'big_gym': 'Mare',
                'our_gym': 'Mică',
                'note': 'Modelul nostru este mai stabil'
            },
            'operational_burnout': {
                'big_gym': 'Mare',
                'our_gym': 'Mic',
                'note': 'Mai puțin stres operațional'
            }
        },
        'conclusion': {
            'dont_win_by': [
                'Mai mult spațiu',
                'Mai mulți oameni'
            ],
            'win_by': [
                'Control',
                'Densitate mică',
                'Venit/mp mare',
                'Servicii cu marjă mare'
            ]
        }
    }
