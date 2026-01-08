# 📘 Ghid Instalare pentru Începători (Fără Python)

Acest ghid te va ajuta să instalezi și să rulezi dashboard-ul chiar dacă nu ai folosit niciodată Python.

## ✅ Verificare Python

Primul pas este să verifici dacă ai Python instalat:

1. Deschide **PowerShell** sau **Command Prompt**:
   - Apasă `Win + X` și selectează "Windows PowerShell"
   - SAU apasă `Win + R`, scrie `cmd` și apasă Enter

2. Scrie următoarea comandă:
   ```powershell
   python --version
   ```

3. **Dacă vezi un număr de versiune** (ex: Python 3.11.0):
   - ✅ Ai Python instalat! Poți sări la secțiunea "Instalare Dashboard"

4. **Dacă vezi eroarea "python nu este recunoscut"**:
   - ❌ Nu ai Python instalat
   - Continuă cu secțiunea "Instalare Python" de mai jos

## 📥 Instalare Python (Dacă nu ai)

### Pasul 1: Descarcă Python

1. Deschide browser-ul și mergi la: **https://www.python.org/downloads/**
2. Apasă butonul mare **"Download Python"** (va descărca ultima versiune)
3. Așteaptă să se descarce fișierul (va fi ceva de genul `python-3.11.x.exe`)

### Pasul 2: Instalează Python

1. **Dublu-click** pe fișierul descărcat pentru a începe instalarea
2. **FOARTE IMPORTANT**: Bifează opțiunea **"Add Python to PATH"** în partea de jos a ferestrei de instalare
   - Această opțiune permite sistemului să găsească Python automat
3. Apasă **"Install Now"**
4. Așteaptă să se termine instalarea (1-2 minute)
5. Când vezi "Setup was successful", apasă **"Close"**

### Pasul 3: Verifică Instalarea

1. **Închide** și **redeschide** PowerShell/Command Prompt (important!)
2. Scrie din nou:
   ```powershell
   python --version
   ```
3. Ar trebui să vezi versiunea Python instalată

## 🚀 Instalare Dashboard

### Pasul 1: Navighează la Folderul Dashboard

1. Deschide **File Explorer** (Exploratorul de fișiere)
2. Mergi la folderul `fitness_center_dashboard` (probabil pe Desktop)
3. **Click dreapta** pe folder și selectează **"Open in Terminal"** sau **"Open PowerShell window here"**
   - SAU copiază calea folderului și scrie în PowerShell:
   ```powershell
   cd C:\Users\D\Desktop\fitness_center_dashboard
   ```
   (Ajustează calea dacă folderul este în alt loc)

### Pasul 2: Instalează Dependențele

În PowerShell, scrie:
```powershell
pip install -r requirements.txt
```

**Dacă primești erori:**
- Încearcă: `python -m pip install -r requirements.txt`
- SAU: `python -m pip install --user -r requirements.txt`

Așteaptă să se termine instalarea (poate dura 2-5 minute). Vei vedea multe mesaje - este normal!

**Ce se instalează:**
- `streamlit` - Framework pentru dashboard
- `folium` și `streamlit-folium` - Pentru hărțile interactive (tab-ul "🗺️ Hartă Participare")
- `pandas`, `numpy` - Pentru calcule
- `plotly` - Pentru graficuri
- Alte dependențe necesare

**Notă:** Toate dependențele pentru hartă sunt incluse automat - nu trebuie instalate separat!

### Pasul 3: Rulează Dashboard-ul

În același terminal, scrie:
```powershell
python -m streamlit run app.py
```

**Prima dată:**
- Vei vedea un mesaj despre email (opțional)
- **Apasă Enter** fără să scrii nimic
- Dashboard-ul se va deschide automat în browser

**Dacă nu se deschide automat:**
- Deschide manual browser-ul (Chrome, Firefox, Edge)
- Scrie în bara de adresă: `http://localhost:8501`

## 🛑 Oprire Dashboard

Când vrei să oprești dashboard-ul:
- În terminal, apasă **`Ctrl + C`**
- Confirmă cu **`Y`** dacă se cere

## ❓ Probleme Frecvente

### "python nu este recunoscut"
**Soluție:**
1. Reinstalează Python și asigură-te că bifezi "Add Python to PATH"
2. SAU folosește: `py -m streamlit run app.py` în loc de `python`

### "pip nu este recunoscut"
**Soluție:**
- Folosește: `python -m pip install -r requirements.txt`

### "Port 8501 deja folosit"
**Soluție:**
- Oprește alte instanțe Streamlit (Ctrl+C în alte terminale)
- SAU rulează pe alt port: `python -m streamlit run app.py --server.port 8502`

### Dashboard nu se deschide
**Soluție:**
- Deschide manual browser-ul și accesează: `http://localhost:8501`
- Verifică dacă firewall-ul blochează conexiunea

### Erori la instalare pachete
**Soluție:**
- Asigură-te că ai conexiune la internet
- Încearcă: `python -m pip install --user -r requirements.txt`
- SAU instalează pachetele unul câte unul

### Harta nu apare sau apare eroare
**Soluție:**
- **Verifică conexiunea la internet** - Harta necesită internet pentru a funcționa
- Verifică dacă `folium` și `streamlit-folium` sunt instalate:
  ```powershell
  pip list | findstr folium
  ```
- Dacă nu apar, reinstalează:
  ```powershell
  pip install folium streamlit-folium
  ```
- Reîmprospătează pagina în browser (F5)

## 📞 Ajutor Suplimentar

Dacă întâmpini probleme:
1. Verifică că ai urmărit toți pașii
2. Asigură-te că ai conexiune la internet
3. Verifică că ai bifezat "Add Python to PATH" la instalare
4. Consultă `README.md` pentru mai multe detalii

## ✅ Verificare Finală

După instalare, ar trebui să poți:
- ✅ Rula `python --version` și să vezi o versiune
- ✅ Rula `pip --version` și să vezi o versiune
- ✅ Rula dashboard-ul și să vezi interfața în browser

**Succes! 🎉**

