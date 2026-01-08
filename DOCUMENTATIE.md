# Documentație Completă - Dashboard Analiză Fitness Center

## Prezentare Generală

Acest dashboard oferă o analiză completă a potențialului unui spațiu de fitness și recuperare post-operatorie în Bacau, Aleea Prieteniei nr 14. Sistemul calculează venituri, necesar de clienți, raza de influență necesară și dimensiunea campaniilor de marketing.

## Structura Proiectului

```
fitness_center_dashboard/
├── app.py                 # Dashboard interactiv Streamlit
├── calculations.py        # Logica de calcul și modele de date
├── export_to_excel.py     # Script pentru export Excel
├── example_usage.py        # Exemple de utilizare programatică
├── requirements.txt        # Dependențe Python
├── README.md              # Documentație de bază
├── QUICK_START.md         # Ghid rapid
└── DOCUMENTATIE.md        # Această documentație
```

## Parametri de Bază

### Capacitate Spațiu
- **Capacitate per oră**: 20 oameni
- **Ore pe zi**: 10 ore
- **Zile pe săptămână**: 7 zile
- **Săptămâni pe lună**: 4.33 (medie)
- **Capacitate maximă lunară**: ~6,062 slot-uri

### Tipuri de Abonamente

1. **Economic** (100 RON/lună)
   - 10 sesiuni/lună
   - Pentru clienți cu buget redus

2. **Standard** (150 RON/lună)
   - Abonament nelimitat
   - Abonament de bază, cel mai popular

3. **Premium** (500 RON/lună)
   - 10 sesiuni/lună cu antrenor personal
   - Pentru clienți premium

### Scenarii de Ocupare

1. **Redus**: 25-50% ocupare
   - Scenariu conservator
   - Realist pentru primele luni

2. **Mediu**: 50-75% ocupare
   - Scenariu echilibrat (recomandat)
   - Realist după stabilizare

3. **Ridicat**: >75% ocupare
   - Scenariu optimist
   - Necesită campanie amplă și timp

## Calcule Implementate

### 1. Calcul Capacitate

```python
max_capacity = 20 oameni/oră × 10 ore/zi × 7 zile/săptămână × 4.33 săptămâni/lună
occupied_slots = max_capacity × occupancy_rate
```

### 2. Calcul Clienți Necesari

**Pentru abonamente cu sesiuni limitate (Economic, Premium):**
```
clienți = slot-uri_ocupate × procentaj_abonament / sesiuni_per_abonament
```

**Pentru abonament standard (nelimitat):**
```
clienți = (slot-uri_ocupate × procentaj_abonament / săptămâni_lună) / vizite_pe_săptămână
```
Presupunere: 3 vizite pe săptămână pentru abonament standard

### 3. Calcul Venituri

```
venit_total = Σ(clienți_tip × preț_abonament_tip)
```

### 4. Calcul Raza de Influență

```
populație_disponibilă_per_km² = densitate_populație × rata_participare
suprafață_necesară = clienți_necesari / populație_disponibilă_per_km²
rază = √(suprafață_necesară / π)
```

### 5. Calcul Dimensiune Campanie

```
populație_totală = π × rază² × densitate_populație
populație_interesată = populație_totală × rata_participare
populație_țintă = clienți_necesari / rata_conversie
```

## Utilizare Dashboard

### Filtre Disponibile

1. **Scenariu Ocupare**: Selectează între Redus, Mediu, Ridicat
2. **Distribuție Abonamente**: Slider-e pentru fiecare tip (se normalizează automat)
3. **Rata Participare**: 1-30% (default: 10%)
4. **Densitate Populație**: 100-10,000 oameni/km² (default: 1,000)
5. **Rata Conversie Campanie**: 1-20% (default: 5%)

### Tab-uri Dashboard

#### 📊 Rezumat
- Capacitate spațiu
- Distribuție abonamente
- Clienți pe tip
- Raza de influență

#### 💰 Venituri
- Grafic pie chart cu distribuția veniturilor
- Comparație cu venitul dorit (50,000 RON)
- Tabel detaliat cu venituri pe tip

#### 👥 Clienți & Demografie
- Grafic cu numărul de clienți pe tip
- Parametri demografici
- Zonă de acoperire

#### 📈 Comparare Scenarii
- Tabel comparativ cu toate scenariile
- Grafic venituri pe scenarii
- Grafic rază influență pe scenarii
- Evoluție clienți

#### 🎯 Campanie
- Metrici campanie (populație țintă, rază, conversie)
- Funnel de conversie
- Estimare costuri
- Recomandări strategice bazate pe rază

## Interpretare Rezultate

### Venituri

- **Peste 50,000 RON**: Scenariu viabil, atinge obiectivul
- **40,000-50,000 RON**: Aproape de obiectiv, poate necesita ajustări
- **Sub 40,000 RON**: Poate necesita:
  - Creștere ocupare
  - Ajustare distribuție abonamente (mai mulți premium)
  - Creștere rata participare prin marketing

### Raza de Influență

- **< 2 km**: Campanie locală (cartier)
  - Flyere, parteneriate locale, rețele sociale locale
  
- **2-5 km**: Campanie extinsă
  - Combinație local + digital (Facebook/Google Ads geo-targetate)
  
- **> 5 km**: Campanie amplă
  - Campanii digitale extinse, parteneriate cu clinici, colaborări

### Clienți Necesari

Numărul de clienți necesari depinde de:
- Rata de ocupare
- Distribuția abonamentelor
- Tipul de abonament (sesiuni limitate vs nelimitat)

## Exemple de Scenarii

### Scenariu 1: Conservator (Primele 6 luni)
```
Ocupare: Redus (25-50%)
Distribuție: 50% Economic, 40% Standard, 10% Premium
Rata participare: 8%
Densitate: 800 oameni/km²

Rezultat estimat:
- Venit: ~30,000-35,000 RON/lună
- Clienți: ~150-200
- Rază: 3-4 km
```

### Scenariu 2: Echilibrat (După stabilizare)
```
Ocupare: Mediu (50-75%)
Distribuție: 40% Economic, 50% Standard, 10% Premium
Rata participare: 10%
Densitate: 1000 oameni/km²

Rezultat estimat:
- Venit: ~45,000-55,000 RON/lună
- Clienți: ~250-350
- Rază: 2.5-3.5 km
```

### Scenariu 3: Optimist (După 1 an)
```
Ocupare: Ridicat (>75%)
Distribuție: 30% Economic, 50% Standard, 20% Premium
Rata participare: 15%
Densitate: 1200 oameni/km²

Rezultat estimat:
- Venit: ~60,000-75,000 RON/lună
- Clienți: ~400-500
- Rază: 2-3 km
```

## Limitări și Presupuneri

### Presupuneri

1. **Abonament Standard**: Presupunem 3 vizite pe săptămână per client
2. **Distribuție Uniformă**: Clienții folosesc abonamentele uniform pe parcursul lunii
3. **Zonă Circulară**: Raza de influență presupune o zonă circulară perfectă
4. **Rata Participare**: Constantă în toată zona (nu ține cont de diferențe locale)

### Limitări

1. **Nu include cheltuieli**: Doar venituri (vor fi adăugate ulterior)
2. **Nu ține cont de sezonalitate**: Calculele sunt pentru o lună medie
3. **Nu include competiția**: Nu analizează concurența din zonă
4. **Densitate uniformă**: Presupune densitate uniformă în toată zona

## Extinderi Viitoare

1. **Adăugare cheltuieli**: Personal, chirie, utilități, marketing
2. **Analiză profitabilitate**: Venituri - Cheltuieli
3. **Sezonalitate**: Calcule pentru fiecare lună
4. **Analiză competiție**: Impactul concurenței
5. **Hărți interactive**: Folium pentru vizualizare geografică
6. **Simulări Monte Carlo**: Analiză risc cu multiple scenarii
7. **Optimizare prețuri**: Găsirea distribuției optime de abonamente

## Suport și Întrebări

Pentru întrebări sau sugestii de îmbunătățire, consultă:
- `QUICK_START.md` pentru ghid rapid
- `example_usage.py` pentru exemple de cod
- `calculations.py` pentru detalii despre calcule

## Licență

Acest proiect este creat pentru analiza potențialului unui spațiu de fitness și recuperare.

