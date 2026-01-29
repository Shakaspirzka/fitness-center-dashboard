"""
Analiză concurențială și poziționare strategică
"""
from calculations import COMPETITORS, CAPACITY_PER_HOUR, HOURS_PER_DAY, calculate_max_capacity
from typing import Dict, List, Optional

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

# Layout recomandat pentru Mobilis Vita
# Sala de fitness: 65-70mp, Sala de clase: 50mp
OUR_RECOMMENDED_LAYOUT = {
    'total_area_m2': 117.5,  # 67.5mp fitness + 50mp clase
    'fitness_area_m2': 67.5,  # Sala de fitness
    'classes_area_m2': 50,  # Sala de clase
    'distribution': {
        'sala_clase': {
            'percentage': 42.5, 
            'm2': 50, 
            'description': 'Sala de Clase de Mișcare (SERVICIU PRINCIPAL)',
            'priority': 'primary'
        },
        'fitness_echipamente': {
            'percentage': 30, 
            'm2': 35, 
            'description': 'Echipamente Fitness (Cardio + Forță ușoară)',
            'priority': 'secondary'
        },
        'spatiu_funcțional': {
            'percentage': 17, 
            'm2': 20, 
            'description': 'Spațiu Funcțional / Stretching',
            'priority': 'secondary'
        },
        'masaj_kineto': {
            'percentage': 8.5, 
            'm2': 10, 
            'description': 'Cabinet Masaj / Kineto',
            'priority': 'secondary'
        },
        'circulații_vestiare': {
            'percentage': 12.5, 
            'm2': 12.5, 
            'description': 'Circulații / Vestiare / Depozit',
            'priority': 'infrastructure'
        }
    },
    'target_capacity': {
        'fitness_simultaneous': {'min': 8, 'max': 12, 'optimal': 10},
        'classes_simultaneous': {'min': 8, 'max': 15, 'optimal': 12},
        'total_simultaneous': {'min': 10, 'max': 15, 'optimal': 12}
    },
    'm2_per_person_range': {
        'fitness': {'min': 5.5, 'max': 8.5, 'optimal': 6.75},
        'classes': {'min': 3.3, 'max': 6.25, 'optimal': 4.2},
        'overall': {'min': 7.8, 'max': 11.75, 'optimal': 9.8}
    },
    'model_description': 'Entry-point pentru mișcare, family-friendly, focus pe clase'
}

# Praguri de confort mp/om
COMFORT_THRESHOLDS = {
    'congested': {'max': 6, 'label': 'Aglomerat'},
    'acceptable': {'min': 6, 'max': 10, 'label': 'Acceptabil'},
    'premium': {'min': 12, 'label': 'Premium / Control'}
}

# Structură extinsă de date pentru toți concurenții din zonă
EXTENDED_COMPETITOR_DATA = {
    # SĂLI DE FITNESS
    'fitness': [
        {
            'id': 'redgym',
            'name': 'RedGym',
            'category': 'Fitness',
            'locations': [
                {
                    'name': 'RedGym Standard',
                    'address': 'Str. Principală, Bacău',
                    'coordinates': (46.5710, 26.9080),
                    'area_m2': 600,
                    'capacity_simultaneous': 140
                },
                {
                    'name': 'RedGym Premium',
                    'address': 'Str. Centrală, Bacău',
                    'coordinates': (46.5720, 26.9100),
                    'area_m2': 800,
                    'capacity_simultaneous': 160
                }
            ],
            'prices': {
                'monthly_standard': 150,
                'monthly_premium': 200,
                'student': 130,
                'annual': 1500,
                'pt_session': 120
            },
            'services': [
                'Echipamente cardio și forță',
                'Cursuri de grup',
                'Antrenor personal',
                'Zonă funcțională',
                'Vestiare și dușuri'
            ],
            'positioning': 'Volum mare, ofertă variată, prețuri accesibile',
            'clients': {
                'total_members': 1000,
                'typology': 'Mix: studenți, tineri profesioniști, persoane 30-50 ani',
                'peak_hours': '18:00-21:00',
                'retention_rate': 'Medie (60-70%)'
            },
            'trainers': [
                {'name': 'Ion Popescu', 'specialization': 'Forță și condiționare', 'instagram': '@ion_popescu_fitness'},
                {'name': 'Maria Ionescu', 'specialization': 'Cardio și pilates', 'instagram': '@maria_ionescu_fit'}
            ],
            'social_media': {
                'instagram': {
                    'handle': '@redgym_bacau',
                    'followers': 3500,
                    'posts_per_week': 4,
                    'engagement_rate': 3.2,
                    'content_types': ['Workout videos', 'Before/after transformations', 'Equipment showcases', 'Member testimonials'],
                    'top_posts': [
                        {'description': 'Transformation story - 6 months', 'likes': 450, 'comments': 32},
                        {'description': 'New equipment arrival', 'likes': 380, 'comments': 28},
                        {'description': 'Group class highlights', 'likes': 320, 'comments': 25}
                    ]
                }
            }
        },
        {
            'id': 'citygym',
            'name': 'City Gym / 18GYM',
            'category': 'Fitness',
            'locations': [
                {
                    'name': 'City Gym Arena Mall',
                    'address': 'Arena Mall, Bacău',
                    'coordinates': (46.5760, 26.9220),
                    'area_m2': 1400,
                    'capacity_simultaneous': 260
                },
                {
                    'name': '18GYM Central',
                    'address': 'Str. Centrală, Bacău',
                    'coordinates': (46.5750, 26.9200),
                    'area_m2': 1500,
                    'capacity_simultaneous': 240
                }
            ],
            'prices': {
                'monthly_standard': 150,
                'monthly_premium': 180,
                'student': 120,
                'annual': 1400,
                'pt_session': 110,
                'access_24_7': True
            },
            'services': [
                'Acces 24/7',
                'Echipamente moderne',
                'Zonă cardio extinsă',
                'Zonă funcțională',
                'Spa wellness',
                'Cursuri de grup'
            ],
            'positioning': 'Low-mid cost, acces extins (24/7), volum mare',
            'clients': {
                'total_members': 1250,
                'typology': 'Studenți, tineri profesioniști, persoane cu program flexibil',
                'peak_hours': '06:00-08:00, 18:00-22:00',
                'retention_rate': 'Medie (55-65%)'
            },
            'trainers': [
                {'name': 'Alexandru Georgescu', 'specialization': 'Bodybuilding', 'instagram': '@alex_georgescu_fit'},
                {'name': 'Elena Radu', 'specialization': 'HIIT și cardio', 'instagram': '@elena_radu_fitness'}
            ],
            'social_media': {
                'instagram': {
                    'handle': '@citygym_bacau',
                    'followers': 4200,
                    'posts_per_week': 5,
                    'engagement_rate': 2.8,
                    'content_types': ['24/7 access highlights', 'Late night workouts', 'Equipment tutorials', 'Member challenges'],
                    'top_posts': [
                        {'description': '24/7 access promotion', 'likes': 520, 'comments': 45},
                        {'description': 'New member challenge', 'likes': 480, 'comments': 38},
                        {'description': 'Equipment tutorial', 'likes': 410, 'comments': 30}
                    ]
                }
            }
        },
        {
            'id': 'q_fitt',
            'name': 'Q Fitt Bacau',
            'category': 'Fitness',
            'locations': [
                {
                    'name': 'Q Fitt Central',
                    'address': 'Str. Centrală, Bacău',
                    'coordinates': (46.5740, 26.9200),
                    'area_m2': 400,
                    'capacity_simultaneous': 60
                }
            ],
            'prices': {
                'monthly_standard': 180,
                'student': 150,
                'annual': 1800,
                'pt_session': 130
            },
            'services': [
                'Fitness funcțional',
                'CrossFit',
                'Cursuri de grup',
                'Antrenor personal',
                'Nutriție'
            ],
            'positioning': 'Fitness funcțional și CrossFit, comunitate activă',
            'clients': {
                'total_members': 200,
                'typology': 'Persoane interesate de fitness funcțional, CrossFit enthusiasts',
                'peak_hours': '17:00-20:00',
                'retention_rate': 'Ridicată (75-80%)'
            },
            'trainers': [
                {'name': 'Mihai Constantinescu', 'specialization': 'CrossFit și funcțional', 'instagram': '@mihai_crossfit'},
                {'name': 'Andreea Popa', 'specialization': 'Fitness funcțional', 'instagram': '@andreea_popa_fit'}
            ],
            'social_media': {
                'instagram': {
                    'handle': '@qfitt_bacau',
                    'followers': 1800,
                    'posts_per_week': 6,
                    'engagement_rate': 5.5,
                    'content_types': ['WOD (Workout of the Day)', 'Community highlights', 'Competition results', 'Nutrition tips'],
                    'top_posts': [
                        {'description': 'WOD challenge', 'likes': 280, 'comments': 42},
                        {'description': 'Community event', 'likes': 250, 'comments': 35},
                        {'description': 'Competition highlights', 'likes': 220, 'comments': 28}
                    ]
                }
            }
        }
    ],
    # SĂLI DE KINETO / REABILITARE
    'kineto': [
        {
            'id': 'kineto_center_1',
            'name': 'Centru Kineto Bacău',
            'category': 'Kineto / Reabilitare',
            'locations': [
                {
                    'name': 'Centru Kineto Principal',
                    'address': 'Str. Medicală, Bacău',
                    'coordinates': (46.5680, 26.9150),
                    'area_m2': 300,
                    'capacity_simultaneous': 20
                }
            ],
            'prices': {
                'session': 150,
                'package_10': 1300,
                'package_20': 2400,
                'monthly_unlimited': 800
            },
            'services': [
                'Kinetoterapie',
                'Recuperare post-operatorie',
                'Recuperare după accidente',
                'Reeducare funcțională',
                'Masaj terapeutic',
                'Electroterapie'
            ],
            'positioning': 'Specializat pe recuperare medicală și reabilitare',
            'clients': {
                'total_members': 150,
                'typology': 'Persoane cu probleme medicale, post-operatorie, accidente, dureri cronice',
                'peak_hours': '09:00-13:00, 15:00-19:00',
                'retention_rate': 'Foarte ridicată (85-90%) - necesitate medicală'
            },
            'therapists': [
                {'name': 'Dr. Ana Marinescu', 'specialization': 'Kinetoterapie și reabilitare', 'instagram': '@dr_ana_marinescu'},
                {'name': 'Ion Stoica', 'specialization': 'Masaj terapeutic', 'instagram': None}
            ],
            'social_media': {
                'instagram': {
                    'handle': '@kineto_bacau',
                    'followers': 1200,
                    'posts_per_week': 2,
                    'engagement_rate': 4.1,
                    'content_types': ['Educational content despre recuperare', 'Testimoniale pacienți', 'Exerciții terapeutice', 'Informații medicale'],
                    'top_posts': [
                        {'description': 'Exerciții pentru dureri de spate', 'likes': 180, 'comments': 25},
                        {'description': 'Testimonial pacient', 'likes': 150, 'comments': 20}
                    ]
                }
            }
        }
    ],
    # CABINETE DE MASAJ
    'masaj': [
        {
            'id': 'masaj_relax_1',
            'name': 'Spa Relax Bacău',
            'category': 'Masaj',
            'locations': [
                {
                    'name': 'Spa Relax',
                    'address': 'Str. Wellness, Bacău',
                    'coordinates': (46.5690, 26.9160),
                    'area_m2': 200,
                    'capacity_simultaneous': 8
                }
            ],
            'prices': {
                'masaj_relaxare': 120,
                'masaj_sportiv': 150,
                'masaj_terapeutic': 180,
                'package_5': 550,
                'package_10': 1000
            },
            'services': [
                'Masaj de relaxare',
                'Masaj sportiv',
                'Masaj terapeutic',
                'Masaj cu pietre calde',
                'Aromaterapie',
                'Saună'
            ],
            'positioning': 'Wellness și relaxare, experiență premium',
            'clients': {
                'total_members': 80,
                'typology': 'Persoane care caută relaxare, recuperare după antrenament, wellness',
                'peak_hours': '16:00-20:00, weekend-uri',
                'retention_rate': 'Ridicată (70-75%)'
            },
            'therapists': [
                {'name': 'Cristina Nistor', 'specialization': 'Masaj de relaxare și wellness', 'instagram': '@cristina_nistor_wellness'},
                {'name': 'Radu Munteanu', 'specialization': 'Masaj sportiv', 'instagram': '@radu_munteanu_sport'}
            ],
            'social_media': {
                'instagram': {
                    'handle': '@spa_relax_bacau',
                    'followers': 2500,
                    'posts_per_week': 3,
                    'engagement_rate': 3.8,
                    'content_types': ['Wellness tips', 'Relaxation techniques', 'Before/after massage', 'Promoții'],
                    'top_posts': [
                        {'description': 'Beneficii masaj de relaxare', 'likes': 320, 'comments': 28},
                        {'description': 'Promoție pachet', 'likes': 280, 'comments': 22}
                    ]
                }
            }
        }
    ],
    # SĂLI CU CLASE DE MIȘCARE ȘI TERAPII
    'terapii': [
        {
            'id': 'pilates_yoga_1',
            'name': 'Studio Pilates & Yoga Bacău',
            'category': 'Pilates / Yoga',
            'locations': [
                {
                    'name': 'Studio Central',
                    'address': 'Str. Wellness, Bacău',
                    'coordinates': (46.5700, 26.9170),
                    'area_m2': 250,
                    'capacity_simultaneous': 25
                }
            ],
            'prices': {
                'clasa_pilates': 50,
                'clasa_yoga': 45,
                'abonament_lunar': 300,
                'abonament_3_luni': 800,
                'clasa_privata': 150
            },
            'services': [
                'Pilates',
                'Yoga',
                'Stretching',
                'Tai Chi',
                'Chi Gong',
                'Clase pentru copii'
            ],
            'positioning': 'Wellness și mișcare mindful, comunitate calmă',
            'clients': {
                'total_members': 120,
                'typology': 'Persoane care caută wellness, flexibilitate, reducere stres, părinți cu copii',
                'peak_hours': '09:00-11:00, 18:00-20:00',
                'retention_rate': 'Foarte ridicată (80-85%)'
            },
            'instructors': [
                {'name': 'Ioana Dumitrescu', 'specialization': 'Pilates și yoga', 'instagram': '@ioana_dumitrescu_pilates'},
                {'name': 'Mihaela Ionescu', 'specialization': 'Yoga și mindfulness', 'instagram': '@mihaela_ionescu_yoga'},
                {'name': 'Andrei Popescu', 'specialization': 'Tai Chi și Chi Gong', 'instagram': None}
            ],
            'social_media': {
                'instagram': {
                    'handle': '@pilates_yoga_bacau',
                    'followers': 2200,
                    'posts_per_week': 4,
                    'engagement_rate': 4.5,
                    'content_types': ['Yoga poses', 'Pilates exercises', 'Wellness quotes', 'Class schedules', 'Mindfulness tips'],
                    'top_posts': [
                        {'description': 'Yoga flow tutorial', 'likes': 380, 'comments': 35},
                        {'description': 'Wellness quote', 'likes': 320, 'comments': 28},
                        {'description': 'Pilates core workout', 'likes': 300, 'comments': 25}
                    ]
                }
            }
        },
        {
            'id': 'bowen_osteopatie',
            'name': 'Centru Terapii Alternative Bacău',
            'category': 'Terapii Alternative',
            'locations': [
                {
                    'name': 'Centru Terapii',
                    'address': 'Str. Terapii, Bacău',
                    'coordinates': (46.5670, 26.9140),
                    'area_m2': 180,
                    'capacity_simultaneous': 10
                }
            ],
            'prices': {
                'bowen': 200,
                'osteopatie': 250,
                'biorezonanta': 180,
                'package_5': 900,
                'consultatie': 150
            },
            'services': [
                'Terapie Bowen',
                'Osteopatie',
                'Biorezonanță',
                'Acupunctură',
                'Reflexologie',
                'Consultanță wellness'
            ],
            'positioning': 'Terapii alternative și holistice, abordare integrată',
            'clients': {
                'total_members': 60,
                'typology': 'Persoane care caută soluții alternative, dureri cronice, wellness holistic',
                'peak_hours': '10:00-14:00, 16:00-19:00',
                'retention_rate': 'Foarte ridicată (85-90%)'
            },
            'therapists': [
                {'name': 'Dr. Elena Vasilescu', 'specialization': 'Osteopatie și terapie Bowen', 'instagram': '@dr_elena_vasilescu'},
                {'name': 'Marius Popa', 'specialization': 'Biorezonanță', 'instagram': None}
            ],
            'social_media': {
                'instagram': {
                    'handle': '@terapii_alternative_bacau',
                    'followers': 1500,
                    'posts_per_week': 2,
                    'engagement_rate': 3.5,
                    'content_types': ['Educational content despre terapii', 'Testimoniale', 'Beneficii terapii alternative'],
                    'top_posts': [
                        {'description': 'Ce este terapia Bowen', 'likes': 200, 'comments': 30},
                        {'description': 'Testimonial pacient', 'likes': 180, 'comments': 25}
                    ]
                }
            }
        },
        {
            'id': 'clase_copii',
            'name': 'Clubul Mișcării pentru Copii',
            'category': 'Clase pentru Copii',
            'locations': [
                {
                    'name': 'Clubul Copiilor',
                    'address': 'Str. Educațională, Bacău',
                    'coordinates': (46.5710, 26.9190),
                    'area_m2': 300,
                    'capacity_simultaneous': 30
                }
            ],
            'prices': {
                'clasa_grup': 40,
                'abonament_lunar': 250,
                'abonament_3_luni': 650,
                'clasa_privata': 100
            },
            'services': [
                'Gimnastică pentru copii',
                'Dans pentru copii',
                'Karate pentru copii',
                'Yoga pentru copii',
                'Jocuri de mișcare',
                'Tabere de vară'
            ],
            'positioning': 'Dezvoltare motrică și socială pentru copii, activități educative',
            'clients': {
                'total_members': 150,
                'typology': 'Copii 4-14 ani, părinți care caută activități pentru copii',
                'peak_hours': '15:00-18:00 (după școală), weekend-uri',
                'retention_rate': 'Ridicată (75-80%)'
            },
            'instructors': [
                {'name': 'Laura Georgescu', 'specialization': 'Gimnastică pentru copii', 'instagram': '@laura_georgescu_kids'},
                {'name': 'Daniel Popescu', 'specialization': 'Karate pentru copii', 'instagram': '@daniel_popescu_karate'}
            ],
            'social_media': {
                'instagram': {
                    'handle': '@clubul_miscarii_copii',
                    'followers': 1800,
                    'posts_per_week': 5,
                    'engagement_rate': 6.2,
                    'content_types': ['Videouri cu copii la antrenament', 'Rezultate competiții', 'Activități educative', 'Părinți mulțumiți'],
                    'top_posts': [
                        {'description': 'Competiție gimnastică', 'likes': 450, 'comments': 55},
                        {'description': 'Tabără de vară', 'likes': 380, 'comments': 42},
                        {'description': 'Clasă de karate', 'likes': 320, 'comments': 35}
                    ]
                }
            }
        }
    ]
}

def get_competitive_positioning() -> dict:
    """
    Returnează analiza poziționării competitive - Mobilis Vita
    Model: Entry-point pentru mișcare, family-friendly, nu pentru pasionați de fitness
    """
    our_capacity = CAPACITY_PER_HOUR
    our_max_monthly = calculate_max_capacity()
    
    return {
        'our_capacity_simultaneous': our_capacity,
        'our_max_monthly_slots': our_max_monthly,
        'positioning': 'Entry-point pentru mișcare: spațiu sigur, fără judecăți, pentru oameni care încep sau revin la mișcare',
        'key_advantages': [
            'Family-friendly: copii, mămici, bunici bineveniți',
            'Entry-point: nu te simți judecat, ci ghidat de la 0 sau puțină mișcare',
            'Abordare personalizată și suportivă',
            'Clase de mișcare ca serviciu principal',
            'Spațiu mic dar confortabil (65-70mp fitness + 50mp clase)',
            'Integrare mișcare în viață pentru sănătate',
            'Servicii complete: clase, masaj, kineto, fitness (secundar)',
            'Proximitate (acces pietonal)'
        ],
        'what_we_dont_do': [
            'NU ne adresăm pasionaților de fitness',
            'NU ne adresăm celor cu experiență avansată',
            'NU concurează pe volum sau preț minim',
            'NU este o sală tradițională de fitness',
            'NU folosește modelul competitiv sau intensiv'
        ],
        'target_audience': [
            'Oameni care încep mișcarea (de la 0)',
            'Oameni care revin la mișcare după pauză',
            'Familii cu copii',
            'Mămici care caută activități pentru ele și copii',
            'Bunici care doresc mișcare blândă',
            'Persoane care nu se simt confortabile în săli tradiționale',
            'Oameni care caută integrare mișcare în viață pentru sănătate'
        ],
        'optimal_capacity': {
            'simultaneous': '10-15 persoane (spațiu mic dar confortabil)',
            'launch_occupancy': '30-40%',
            'mature_occupancy': '60-70%',
            'warning_threshold': '80% (spațiu mic, trebuie menținut confortul)'
        },
        'influence_radius': {
            'estimated': '~500-700m (comunitate locală)',
            'primary_zone': '70% din clienți din primii 500m (family-friendly, acces ușor)',
            'secondary_zone': '30% prin recomandări și comunitate'
        },
        'services_priority': {
            'primary': 'Clase de mișcare (50mp dedicat)',
            'secondary': 'Masaj și kineto (servicii terapeutice)',
            'tertiary': 'Acces sala fitness (65-70mp, serviciu secundar)'
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

def get_all_extended_competitors() -> Dict:
    """
    Returnează toate datele extinse despre concurenți organizate pe categorii
    """
    return EXTENDED_COMPETITOR_DATA

def get_competitors_by_category(category: str) -> List[Dict]:
    """
    Returnează concurenții dintr-o anumită categorie
    
    Args:
        category: 'fitness', 'kineto', 'masaj', 'terapii'
    """
    return EXTENDED_COMPETITOR_DATA.get(category, [])

def get_all_competitor_locations() -> List[Dict]:
    """
    Returnează toate locațiile tuturor concurenților cu coordonate
    """
    locations = []
    for category, competitors in EXTENDED_COMPETITOR_DATA.items():
        for competitor in competitors:
            for location in competitor.get('locations', []):
                locations.append({
                    'competitor_name': competitor['name'],
                    'category': competitor['category'],
                    'location_name': location['name'],
                    'address': location.get('address', 'N/A'),
                    'coordinates': location.get('coordinates'),
                    'area_m2': location.get('area_m2', 0),
                    'capacity': location.get('capacity_simultaneous', 0)
                })
    return locations

def get_social_media_summary() -> Dict:
    """
    Returnează un rezumat al prezenței pe social media pentru toți concurenții
    """
    summary = {
        'total_followers': 0,
        'total_competitors_with_instagram': 0,
        'avg_engagement_rate': 0,
        'avg_posts_per_week': 0,
        'by_category': {}
    }
    
    engagement_rates = []
    posts_per_week = []
    
    for category, competitors in EXTENDED_COMPETITOR_DATA.items():
        category_summary = {
            'total_followers': 0,
            'competitors_count': 0,
            'avg_engagement': 0,
            'avg_posts': 0
        }
        
        category_engagement = []
        category_posts = []
        
        for competitor in competitors:
            social = competitor.get('social_media', {}).get('instagram', {})
            if social:
                followers = social.get('followers', 0)
                engagement = social.get('engagement_rate', 0)
                posts = social.get('posts_per_week', 0)
                
                summary['total_followers'] += followers
                category_summary['total_followers'] += followers
                category_summary['competitors_count'] += 1
                
                if engagement > 0:
                    engagement_rates.append(engagement)
                    category_engagement.append(engagement)
                
                if posts > 0:
                    posts_per_week.append(posts)
                    category_posts.append(posts)
        
        if category_engagement:
            category_summary['avg_engagement'] = sum(category_engagement) / len(category_engagement)
        if category_posts:
            category_summary['avg_posts'] = sum(category_posts) / len(category_posts)
        
        summary['by_category'][category] = category_summary
    
    summary['total_competitors_with_instagram'] = sum(
        cat['competitors_count'] for cat in summary['by_category'].values()
    )
    
    if engagement_rates:
        summary['avg_engagement_rate'] = sum(engagement_rates) / len(engagement_rates)
    if posts_per_week:
        summary['avg_posts_per_week'] = sum(posts_per_week) / len(posts_per_week)
    
    return summary

def get_competitor_detailed_info(competitor_id: Optional[str] = None) -> Optional[Dict]:
    """
    Returnează informații detaliate despre un anumit competitor
    
    Args:
        competitor_id: ID-ul competitorului (ex: 'redgym', 'kineto_center_1')
    """
    if not competitor_id:
        return None
    
    for category, competitors in EXTENDED_COMPETITOR_DATA.items():
        for competitor in competitors:
            if competitor.get('id') == competitor_id:
                return competitor
    return None
