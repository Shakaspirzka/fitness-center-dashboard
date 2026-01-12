"""
Analiză concurențială și poziționare strategică
"""
from calculations import COMPETITORS, CAPACITY_PER_HOUR, HOURS_PER_DAY, calculate_max_capacity

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
