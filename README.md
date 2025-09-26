# 🦅 EMG-Controlled Bird Game (Flappy Birds Style)

Questo progetto unisce l'acquisizione di dati elettromiografici (EMG) con un semplice gioco in stile Flappy Birds, permettendo all'utente di controllare l'uccellino con le contrazioni muscolari.

---

## 🎯 Obiettivo del Progetto

L'obiettivo è trasformare l'attività muscolare registrata dai sensori **Delsys Trigno** in un comando di gioco *one-shot* (impulso singolo). Una contrazione muscolare che supera una soglia predefinita genera un impulso di "salto" nel gioco.

---

## 📂 Struttura della Repository

La repository è composta da due script Python principali che devono essere eseguiti in parallelo e da cartelle di supporto:

| File/Cartella | Descrizione |
| :--- | :--- |
| **`my_flappy.py`** | **Script del Gioco.** Contiene la logica di Pygame (movimento, tubi, gravità). **Legge** lo stato del comando dal file `emg_state.txt`. |
| **`emg_sensor_flag.py`** | **Script del Sensore Delsys.** Gestisce la connessione con la base Delsys Trigno, l'acquisizione dei dati EMG e l'elaborazione della soglia. **Scrive** lo stato del comando nel file `emg_state.txt`. |
| **`emg_state.txt`** | **File di Stato (Flag).** Un semplice file di testo che contiene lo stato corrente del comando EMG (`True` o `False`). Quando l'attività muscolare supera la soglia, questo file viene impostato su `True`, innescando il salto nel gioco. |
| **`Python/`** | Contiene i moduli e le librerie personalizzate (`AeroPy`, `TrignoBase`, `DataManager`) necessarie per l'interazione con i sensori Delsys. |
| **`assets/`** | Contiene le risorse grafiche (`.png`) e i font (`.ttf`) utilizzati da Pygame. |

---

## 🚀 Istruzioni per l'Avvio

Per utilizzare il sistema, è essenziale avviare entrambi gli script contemporaneamente:

### 1. Preparazione Fisica della Base

**Connessione Base:** Collega la Base di Ricarica (o Delsys Trigno Base Station) al PC tramite USB. Assicurati anche che l'unità Trigno Center (il componente che gestisce il wireless) sia collegata.

**Accensione:** Accendi l'unità Trigno Center. La luce di stato dovrebbe cambiare, passando generalmente da blu ad arancione, indicando che è alimentata e in attesa di connessione.

### 2. Attivazione e Accoppiamento dei Sensori

**Sblocco dei Sensori:** Estrai i sensori dalla base di ricarica.

    Inizialmente, il sensore mostrerà una luce viola (modalità sleep).

**Attivazione:** Passa il sensore sul magnetometro della base (di solito una piccola area designata). La luce cambierà in blu (ricerca base) o arancione/verde (accoppiato). Questo li rende "sbloccati" e attivi.

**Configurazione Software:** Lo script emg_sensor_flag.py gestirà la configurazione software, connettendosi alla base, scoprendo i sensori attivi e impostando la modalità di campionamento su 'EMG raw (2148 Hz)'.

### 3. Avvio degli Script

Apri due finestre di terminale separate nella directory principale del progetto:

| Terminale | Comando | Note |
| :--- | :--- | :--- |
| **Terminale 1** | `python emg_sensor_flag.py` | Avvia il monitoraggio dei sensori. |
| **Terminale 2** | `python my_flappy.py` |
