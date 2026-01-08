# Dashboard Analiză Potențial Spațiu Fitness & Recuperare - Bacau

Dashboard interactiv pentru analiza potențialului unui spațiu de fitness și recuperare post-operatorie în Bacau, Aleea Prieteniei nr 14.

## 🌐 Versiune Live

Dacă dashboard-ul este deployat pe Streamlit Cloud, poate fi accesat live la:
- **Link**: https://fintess-prieteniei.streamlit.app

Pentru instrucțiuni de deploy, vezi: [`DEPLOY_GITHUB.md`](DEPLOY_GITHUB.md)

## 📋 Cerințe Sistem

### Pentru utilizatori cu Python deja instalat:
- Python 3.8 sau mai nou
- pip (inclus în Python)

### Pentru utilizatori fără Python instalat:

**Opțiunea 1: Instalare Python (Recomandat)**
1. Descarcă Python de la: https://www.python.org/downloads/
2. La instalare, **bifează opțiunea "Add Python to PATH"** (foarte important!)
3. Instalează Python
4. Deschide PowerShell sau Command Prompt
5. Verifică instalarea: `python --version`
6. Continuă cu pașii de mai jos

**Opțiunea 2: Utilizare fără instalare (avansat)**
- Poți folosi Python portabil sau Anaconda
- Consultă documentația Python pentru detalii

## 🚀 Instalare și Rulare

### Pasul 1: Deschide Terminal/PowerShell
- **Windows**: Apasă `Win + X` și selectează "Windows PowerShell" sau "Terminal"
- Navighează la folderul proiectului:
  ```powershell
  cd C:\Users\D\Desktop\fitness_center_dashboard
  ```
  (sau calea unde ai salvat folderul)

### Pasul 2: Instalează Dependențele
```bash
pip install -r requirements.txt
```

**Dacă primești erori de permisiuni pe Windows:**
```bash
python -m pip install --user -r requirements.txt
```

**Dependențe importante:**
- `streamlit` - Framework pentru dashboard
- `folium` - Pentru crearea hărților interactive
- `streamlit-folium` - Integrare Folium cu Streamlit (pentru tab-ul "🗺️ Hartă Participare")
- `pandas`, `numpy` - Pentru calcule și manipulare date
- `plotly` - Pentru graficuri interactive
- `openpyxl` - Pentru export Excel

**Notă:** Toate dependențele necesare pentru hartă (folium, streamlit-folium) sunt incluse automat în `requirements.txt`. Nu este nevoie de instalare separată.

### Pasul 3: Rulează Dashboard-ul
```bash
python -m streamlit run app.py
```

**Prima dată când rulezi Streamlit:**
- Vei vedea un mesaj care cere email-ul (opțional)
- Apasă **Enter** fără să introduci nimic pentru a continua
- Dashboard-ul se va deschide automat în browser la `http://localhost:8501`

**Dacă nu se deschide automat:**
- Deschide manual browser-ul (Chrome, Firefox, Edge)
- Accesează: `http://localhost:8501`

### Pasul 4: Oprește Dashboard-ul
- În terminal, apasă `Ctrl + C` pentru a opri serverul

## 📊 Caracteristici

- **3 Scenarii de ocupare**: Redus (25-50%), Mediu (50-75%), Ridicat (>75%)
- **3 Tipuri de abonamente**: 
  - Economic: 100 RON/lună (10 ședințe)
  - Standard: 150 RON/lună
  - Premium: 500 RON/lună (cu antrenor, 10 ședințe)
- **Analiză bazată pe locație**: Calcul raza de influență bazată pe densitatea populației
- **Hărți interactive**: Vizualizare zonă de influență și participare pe blocuri
- **Calcule dinamice**: Venituri, necesar clienți, dimensiune raza de influență
- **Vizualizări interactive**: Graficuri, tabele, hărți

## 🎯 Utilizare

1. **Selectează scenariul de ocupare** din sidebar (Redus/Mediu/Ridicat)
2. **Ajustează distribuția abonamentelor** cu slider-ele (procentajele se normalizează automat)
3. **Modifică parametrii demografici**:
   - Rata participare populație (1-30%)
   - Densitate populație (oameni/km²)
4. **Explorează tab-urile**:
   - 📊 **Rezumat** - Vedere generală cu toate metricile importante
   - 💰 **Venituri** - Analiză detaliată venituri pe tip de abonament
   - 👥 **Clienți & Demografie** - Analiză clienți și parametri demografici
   - 📈 **Comparare Scenarii** - Compară toate scenariile simultan
   - 🗺️ **Hartă Participare** - Vizualizare geografică interactivă cu participare pe blocuri și cartiere
   - 🎯 **Campanie** - Analiză campanie marketing cu recomandări strategice

## ❓ Probleme Frecvente

### "python nu este recunoscut ca comandă"
- Python nu este în PATH
- Reinstalează Python și bifează "Add Python to PATH"
- Sau folosește: `py -m streamlit run app.py` în loc de `python`

### "pip nu este recunoscut"
- Folosește: `python -m pip install -r requirements.txt`

### Port 8501 deja folosit
- Oprește alte instanțe Streamlit: `Ctrl + C` în terminal
- Sau rulează pe alt port: `streamlit run app.py --server.port 8502`

### Dashboard nu se deschide în browser
- Deschide manual: `http://localhost:8501`
- Verifică dacă firewall-ul blochează conexiunea

### Harta nu apare sau apare eroare
- **Verifică conexiunea la internet** - Harta necesită internet pentru a încărca tile-urile
- Verifică dacă `folium` și `streamlit-folium` sunt instalate:
  ```bash
  pip list | findstr folium
  ```
- Dacă lipsesc, reinstalează:
  ```bash
  pip install folium streamlit-folium
  ```
- Reîmprospătează pagina în browser (F5)

## 📁 Structura Proiectului

```
fitness_center_dashboard/
├── app.py                          # Dashboard principal
├── calculations.py                 # Logica de calcul
├── requirements.txt                # Dependențe Python
├── .gitignore                      # Fișiere ignorate de Git
├── README.md                       # Acest fișier
├── QUICK_START.md                  # Ghid rapid
├── DOCUMENTATIE.md                 # Documentație detaliată
├── MODEL_DE_GANDIRE.md             # Model de gândire și arhitectură
├── INSTALARE_PENTRU_INCEPATORI.md  # Ghid pentru începători
└── DEPLOY_GITHUB.md                # Ghid deploy pe GitHub/Streamlit Cloud
```

## 📞 Suport

Pentru întrebări sau probleme, consultă:
- `QUICK_START.md` - Ghid rapid de utilizare
- `DOCUMENTATIE.md` - Documentație completă cu exemple
- `MODEL_DE_GANDIRE.md` - **Model de gândire și arhitectură** (recomandat pentru utilizatori noi)
- `INSTALARE_PENTRU_INCEPATORI.md` - Ghid pas cu pas pentru începători

## 🗺️ Funcționalități Hărți

Tab-ul **"🗺️ Hartă Participare"** oferă:
- **Hartă interactivă** cu locația exactă a salii (Aleea Prieteniei nr 14, Bacau)
- **Cercul de influență** vizualizat pe hartă (raza calculată)
- **Blocuri și cartiere** colorate după nivelul de participare:
  - 🟢 **Verde** - Participare ridicată (zone apropiate)
  - 🔵 **Albastru** - Participare medie
  - 🟠 **Portocaliu** - Participare moderată
  - 🔴 **Roșu** - Participare redusă (zone îndepărtate)
- **Popup-uri informative** pentru fiecare bloc cu detalii despre participare și populație
- **Tabel detaliat** cu toate blocurile și statistici

## 📝 Note Importante

1. **Conexiune Internet**: Dashboard-ul necesită conexiune la internet pentru a încărca hărțile interactive (Folium folosește tile-uri online)

2. **Date Simulate**: Blocurile și cartierele de pe hartă sunt simulate pentru demonstrație. Pentru date reale, poți importa date geografice specifice zonei

3. **Participare pe Blocuri**: Participarea este calculată automat bazată pe distanța de la locația centrală - blocurile mai aproape au participare mai ridicată

