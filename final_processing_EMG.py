import os
import numpy as np
import pandas as pd
import scipy.signal as signal
import neurokit2 as nk


def read_csv_signal(filepath):
    """
    Legge un file CSV ed estrae solo la colonna 'Value' come numpy array.
    Salta le prime due righe di intestazione.
    """
    df = pd.read_csv(filepath)

    # Normalizza i nomi delle colonne (togli spazi e rendi lowercase)
    df.columns = df.columns.str.strip().str.lower()

    if "value" not in df.columns:
        raise ValueError(f"Colonna 'Value' non trovata in {filepath}. Colonne disponibili: {df.columns.tolist()}")

    return df["value"].values.astype(float)

# ----------------------
# FEATURE EMG
# ----------------------

def extract_features_emg(window, fs):
    """
    Estrae le feature da una finestra EMG:
    - Max amplitude
    - Min amplitude
    - Mean amplitude
    """
    window = np.asarray(window).squeeze()

    amplitude = nk.emg_amplitude(window)

    MAX_AMPLITUDE = np.max(amplitude)
    MIN_AMPLITUDE = np.min(amplitude)
    MEAN_AMPLITUDE = np.mean(amplitude)

    return MAX_AMPLITUDE, MIN_AMPLITUDE, MEAN_AMPLITUDE

# ----------------------
# ESECUZIONE
# ----------------------

if __name__ == "__main__":

    input_dir = r"C:\Users\ars_a\Downloads\flappy_emg-20250908T134950Z-1-001\csv\recorded_data_emg.csv"

    signal_array = read_csv_signal(input_dir)

    fs = 2148; #frequenza di campionamento 
    emg_signal = nk.signal_sanitize(signal_array) # Processing del segnale 
    emg_cleaned = nk.emg_clean(emg_signal, sampling_rate=fs) 

    # Butterworth filter zero phase 4th order high-pass cutoff frequency 30 Hz 
    fc = 30; #frequenza di taglio 
    order = 4; #ordine del filtro 
    [b, a] = signal.butter(order, fc/(fs/2), btype='high'); #coefficienti filtro Butterworth 
    signal_filtered = signal.filtfilt(b, a, emg_cleaned) 

    # Calcolo feature su tutto il segnale
    max_amp, min_amp, mean_amp = extract_features_emg(signal_filtered, fs)

    print(f"Segnale completo: MAX={max_amp:.4f}, MIN={min_amp:.4f}, MEAN={mean_amp:.4f}")




