import amfm_decompy.pYAAPT as pYAAPT
import amfm_decompy.basic_tools as basic
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import time


def create_plot_praat(audio_data, f0, times):
    '''
        Erzeugung von Grafiken zur Darstellung
        der Grundfrequenzverläufe durch Praat
    '''
    db = librosa.amplitude_to_db(np.abs(librosa.stft(audio_data, hop_length=512)), ref=np.max)
    figure, ax = plt.subplots()
    img = librosa.display.specshow(db, sr=44100, x_axis='s', y_axis='log', ax=ax, hop_length=512)
    ax.set(title='Konkat. Crossfade: Grundfrequenzschätzung mit Praat')
    figure.colorbar(img, ax=ax, format="%+2.f dB")
    ax.plot(times, f0, label='f0', color='cyan', linewidth=3)
    ax.legend(loc='upper right')
    plt.savefig(fname="Sonagramm_crossfade_praat.png")
    plt.show()


def create_plot_yaapt(audio_data, f0, frame_times, cross=False):
    '''
        Erzeugung von Grafiken zur Darstellung
        der Grundfrequenzverläufe mit YAAPT
    '''
    times = np.array([x/44100 for x in frame_times])
    db = librosa.amplitude_to_db(np.abs(librosa.stft(audio_data, hop_length=512)), ref=np.max)
    figure, ax = plt.subplots()
    img = librosa.display.specshow(db, sr=44100, x_axis='s', y_axis='log', ax=ax, hop_length=512)
    if cross:
        ax.set(title='Grundfrequenzglättung mit pYAAPT; Crossfade')
    else:
        ax.set(title='Grundfrequenzglättung mit pYAAPT; Nulldurchgang')
    figure.colorbar(img, ax=ax, format="%+2.f dB")
    ax.plot(times, f0, label='f0', color='cyan', linewidth=3)
    ax.legend(loc='upper right')
    if cross:
        plt.savefig(fname="Sonagramm_pitch_correction_crossfade_yaapt.png")
    else:
        plt.savefig(fname="Sonagramm_pitch_correction_zerocross_yaapt.png")
    plt.show()


def create_plot_yin(audio_data, f0, cross=False):
    '''
        Erzeugung von Grafiken zur Darstellung
        der Grundfrequenzverläufe mit YIN
    '''
    times = librosa.times_like(f0, sr=44100, hop_length=512)
    db = librosa.amplitude_to_db(np.abs(librosa.stft(audio_data, hop_length=512)), ref=np.max)
    figure, ax = plt.subplots()
    img = librosa.display.specshow(db, sr=44100, x_axis='s', y_axis='log', ax=ax, hop_length=512)
    if cross:
        ax.set(title='Grundfrequenzglättung mit PYIN; Crossfade')
    else:
        ax.set(title='Grundfrequenzglättung mit PYIN; Nulldurchgang')
    figure.colorbar(img, ax=ax, format="%+2.f dB")
    ax.plot(times, f0, label='f0', color='cyan', linewidth=3)
    ax.legend(loc='upper right')
    if cross:
        plt.savefig(fname="Sonagramm_pitch_correction_crossfade_yin.png")
    else:
        plt.savefig(fname="Sonagramm_pitch_correction_zerocross_yin.png")
    plt.show()


def estimate_pitch_yaapt(path_to_audio):
    '''
        Grundfrequenzschätzung mit YAAPT
    '''
    start = time.time()
    signal = basic.SignalObj(path_to_audio)
    pitch = pYAAPT.yaapt(signal)        # schätzt Grundfrequenz
    ende = time.time()
    print("Geschwindigkeit YAAPT: " + str(ende - start) + " Sekunden.")     # Berechnung der Geschwindigkeit des Algorithmus
    pitch_samples = pitch.samp_values
    pitch_samples[pitch_samples == 0] = 'nan'
    print("Mittelwert YAAPT: " + str(np.nanmean(pitch_samples, axis=0)))   # berechnet mean, ignoriert nan-Werte
    return signal.data, pitch_samples, pitch.frames_pos


def estimate_pitch_yin(path_to_audio):
    '''
        Grundfrequenzschätzung mit YIN
    '''
    start = time.time()
    audio_data, sr = librosa.load(path_to_audio, sr=44100)
    f0, voiced_flag, voiced_probs = librosa.pyin(y=audio_data, fmin=100, fmax=500, sr=44100, frame_length=512)
    ende = time.time()
    print("Geschwindigkeit YIN: " + str(ende-start) + " Sekunden.") # Berechnung der Geschwindigkeit des Algorithmus
    print("Mittelwert YIN: " + str(np.nanmean(f0, axis=0)))   # berechnet mean, ignoriert nan-Werte
    return audio_data, f0


def get_pitch_praat(textfile):
    '''
        Liest Grundfrequenzschätzung aus Praat-Textdatei aus
    '''
    pitch = np.genfromtxt(textfile, filling_values='nan')       # fehlende Werte werden mit nan aufgefüllt
    f0 = pitch[:, 1]
    times = pitch[:, 0]
    print("Mittelwert Praat: " + str(np.nanmean(f0, axis=0)))       # berechnet mean, ignoriert nan-Werte
    return f0, times


# Erstellung der Plots
for x in ["yin", "yaapt"]:
    for y in ["crossfade", "zerocross"]:
        path = "pitch_corrected_" + y + "_" + x + ".wav"
        if x == "yin":
            data, f0 = estimate_pitch_yin(path)
            if y == "crossfade":
                create_plot_yin(data, f0, True)
            else:
                create_plot_yin(data, f0)
        if x == "yaapt":
            data, f0, frames = estimate_pitch_yaapt(path)
            if y == "crossfade":
                create_plot_yaapt(data, f0, frames, True)
            else:
                create_plot_yaapt(data, f0, frames)

# f0, times = get_pitch_praat('crossfade_pitch_praat.txt')
# create_plot_praat(data, f0, times)
