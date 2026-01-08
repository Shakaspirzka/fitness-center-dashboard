# Ghid Rapid de Utilizare

## Instalare

1. Instalează dependențele:
```bash
pip install -r requirements.txt
```

## Rulare Dashboard

```bash
streamlit run app.py
```

Dashboard-ul se va deschide automat în browser la adresa `http://localhost:8501`

## Utilizare Dashboard

### 1. Selectare Scenariu
În sidebar, selectează scenariul de ocupare:
- **Redus**: 25-50% ocupare
- **Mediu**: 50-75% ocupare (recomandat)
- **Ridicat**: >75% ocupare

### 2. Ajustare Distribuție Abonamente
Folosește slider-ele pentru a seta procentajul fiecărui tip de abonament:
- **Economic** (100 RON/lună): Pentru clienți cu buget redus
- **Standard** (150 RON/lună): Abonament de bază, nelimitat
- **Premium** (500 RON/lună): Cu antrenor personal

### 3. Parametri Demografici
- **Rata Participare**: Procentul din populație interesat de servicii fitness/recuperare (default: 10%)
- **Densitate Populație**: Numărul de oameni pe km² în zonă (default: 1000)

### 4. Analiză Rezultate
Dashboard-ul afișează automat:
- Venituri lunare estimate
- Număr clienți necesari
- Raza de influență necesară
- Dimensiunea campaniei de marketing

## Tab-uri Dashboard

### 📊 Rezumat
Vedere generală cu toate metricile importante

### 💰 Venituri
Analiză detaliată a veniturilor pe tip de abonament și comparație cu venitul dorit (50,000 RON)

### 👥 Clienți & Demografie
Distribuția clienților și parametrii demografici necesari

### 📈 Comparare Scenarii
Compară toate cele 3 scenarii simultan pentru a vedea diferențele

### 🗺️ Hartă Participare
Hartă interactivă care arată:
- Locația exactă a salii (Aleea Prieteniei nr 14)
- Cercul de influență calculat
- Blocuri și cartiere colorate după nivelul de participare
- Popup-uri cu detalii pentru fiecare zonă
- Tabel cu statistici pentru toate blocurile

**Culori participare:**
- 🟢 Verde - Participare ridicată (zone apropiate)
- 🔵 Albastru - Participare medie
- 🟠 Portocaliu - Participare moderată
- 🔴 Roșu - Participare redusă (zone îndepărtate)

### 🎯 Campanie
Analiză detaliată pentru campania de marketing:
- Populație țintă
- Raza de acoperire
- Costuri estimate
- Recomandări strategice

## Export în Excel

Pentru a exporta datele în Excel, folosește scriptul:

```python
from export_to_excel import export_analysis_to_excel

subscription_dist = {
    'economic': 0.4,
    'standard': 0.5,
    'premium': 0.1
}

export_analysis_to_excel(
    subscription_dist,
    participation_rate=0.10,
    population_density=1000,
    filename="analiza_fitness_center.xlsx"
)
```

## Exemple de Scenarii

### Scenariu Conservator
- Ocupare: Redus (25-50%)
- Distribuție: 50% Economic, 40% Standard, 10% Premium
- Rata participare: 8%
- Rezultat: Venituri mai mici, dar mai realist pentru început

### Scenariu Optimist
- Ocupare: Ridicat (>75%)
- Distribuție: 30% Economic, 50% Standard, 20% Premium
- Rata participare: 15%
- Rezultat: Venituri mari, necesită campanie amplă

### Scenariu Echilibrat (Recomandat)
- Ocupare: Mediu (50-75%)
- Distribuție: 40% Economic, 50% Standard, 10% Premium
- Rata participare: 10%
- Rezultat: Balanță între realism și potențial

## Sfaturi

1. **Începe cu scenariul Mediu** pentru a obține o estimare realistă
2. **Ajustează rata de participare** în funcție de cercetările de piață locale
3. **Verifică densitatea populației** pentru zona specifică (Aleea Prieteniei, Bacau)
4. **Folosește tab-ul Comparare Scenarii** pentru a vedea toate opțiunile simultan
5. **Analizează tab-ul Campanie** pentru a planifica strategia de marketing

## Date de Referință

- **Capacitate maximă**: 20 oameni/oră × 10 ore/zi × 7 zile/săptămână × 4.33 săptămâni/lună = ~6,062 slot-uri/lună
- **Venit dorit**: 50,000 RON/lună
- **Locație**: Aleea Prieteniei nr 14, Bacau

