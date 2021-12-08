import os
import pygame
import numpy as np
import librosa
import psola
import soundfile
from pydub import AudioSegment
import amfm_decompy.pYAAPT as pYAAPT
import amfm_decompy.basic_tools as basic


def get_db():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'DB_Management'))


def get_sr():
    '''
        feste Sampling-Rate für alle Audiodateien
    '''
    return 44100


def audioseg_to_np(audioseg):
    '''
        wandelt ein AudioSegment-Objekt in einen
        Numpy-Array um
    '''
    samples = audioseg.get_array_of_samples()
    return np.array(samples).astype(np.float32) / 32768     # Werte der Samples zwischen -1 und 1 bringen


def get_start_and_end(timestamps, last_elem):
    '''
        gibt Diphongrenzen in Sampleangaben zurück
    '''
    if timestamps[1] == 0:
        start = timestamps[1] + timestamps[2] - 50      # füge 50 Samples extra am Anfang der Audio hinzu
        end = 0.5 * (timestamps[1] + timestamps[2] + timestamps[3])
    elif last_elem:
        start = timestamps[1] + (timestamps[2] / 2)
        end = timestamps[1] + timestamps[2] + 200       # füge 200 Samples extra am Ende der Audio hinzu
    else:
        start = timestamps[1] + (timestamps[2] / 2)
        end = 0.5 * (timestamps[1] + timestamps[2] + timestamps[3])

    return int(start), int(end)


def samples_to_ms(samples):
    '''
        wandelt Angaben in Samples zu
        Millisekunden-Angaben um
    '''
    return int(samples / (get_sr() / 1000))


def smooth_pitch(audio, f0):
    '''
        passt die Grundfrequenz einer Audiodatei dem Grundfrequenzverlauf
        des Arrays f0 an.
    '''
    vocoded = psola.vocode(audio=audio, sample_rate=get_sr(), target_pitch=f0, fmin=150, fmax=500)
    return vocoded


def calculate_new_pitch(f0_values):
    '''
        Zur Glättung der Grundfrequenz wird ein zweites Array angefertigt,
        das die geglätteten Werte enthält
        Falls in dem Grundfrequenzverlauf große (> 2%) Sprünge gefunden werden,
        werden diese neu berechnet.
    '''

    for i in range(len(f0_values)):
        if i != 0:
            this = f0_values[i]
            previous = f0_values[i - 1]
            if previous != 0 and f0_values[i] != 0:
                if this - this * 0.02 > previous:
                    f0_values[i] = this - this * 0.02
                elif this + this * 0.02 < previous:
                    f0_values[i] = this + this * 0.02

    return f0_values


def estimate_pitch_yin(audio):
    '''
        Grundfrequenz-Schätzung mit PYIN
    '''
    pitch, voiced_flag, voiced_probs = librosa.pyin(y=audio, fmin=100, fmax=500, sr=get_sr(), frame_length=512)
    return pitch


def estimate_pitch_yaapt(audio):
    '''
        Grundfrequenz-Schätzung mit YAAPT
    '''
    signal = basic.SignalObj(audio, get_sr())
    pitch = pYAAPT.yaapt(signal)        # schätzt Grundfrequenz

    return pitch.samp_values.copy()


def find_zerocrossings(audio, konkat_punkt):
    '''
        Findet das nächste Sample, bei dem ein Nulldurchgang
        in der Wellenform der Audiodatei gefunden werden kann.
        Der Nulldurchgang sollte vom positiven ins negative verlaufen.
    '''
    zeros = librosa.zero_crossings(audio)
    index = np.nonzero(zeros)
    index = index[0]

    # in next_zero wird von konkat_punkt aus gesehen das näheste Zerocrossing gespeichert
    next_zero = min(index, key=lambda x: abs(x - konkat_punkt))

    for i in range(len(index)):
        # Nulldurchgänge von pos nach neg
        if audio[next_zero - 1] < audio[next_zero] or audio[next_zero + 1] > audio[next_zero]:
            index_next_zero = np.where(index == next_zero)
            next_zero = index[index_next_zero[0][0] + 1]
        else:
            break

    return next_zero


def simple_concatenation(arr):
    '''
        einfacher Verbund der Diphone direkt an den Diphongrenzen
    '''
    concatenate = np.empty(shape=(), dtype='float32')
    last_elem = False
    for elem in range(0, len(arr)):
        diphone = arr[elem]
        if elem == len(arr)-1:
            last_elem = True
        start, end = get_start_and_end(diphone, last_elem)      # Diphongrenzen berechnen
        path = get_db() + "\\IPATS_emuDB\\0000_ses\\0001" + diphone[0] + "_bndl\\0001" + diphone[0] + ".wav"
        sound, sr = soundfile.read(file=path)

        slices = sound[start:end]                       # Diphon aus Audiodatei heraus kopieren
        concatenate = np.append(concatenate, slices)    # Diphone ohne Anpassungen aneinander hängen

    return concatenate


def concatenation_zerocross(arr):
    '''
        Verbund der Diphone direkt an Nulldurchgängen
    '''
    concatenate = np.empty(shape=(), dtype='float32')
    last_elem = False
    for elem in range(0, len(arr)):
        diphone = arr[elem]
        if elem == len(arr)-1:
            last_elem = True
        start, end = get_start_and_end(diphone, last_elem)      # Diphongrenzen berechnen
        path = get_db() + "\\IPATS_emuDB\\0000_ses\\0001" + diphone[0] + "_bndl\\0001" + diphone[0] + ".wav"
        sound, sr = soundfile.read(file=path)

        start = find_zerocrossings(sound, start)    # näheste Nulldurchgänge an Diphongrenzen finden
        end = find_zerocrossings(sound, end)

        slices = sound[start:end]                       # Diphon aus Audiodatei heraus kopieren
        concatenate = np.append(concatenate, slices)    # Diphone an Nulldurchgängen aneinander hängen

    return concatenate


def concatenation_crossfade(arr):
    '''
        Verbund der Diphone mit kurzen Überblendungen
    '''
    concatenate = AudioSegment.empty()
    cross_new = 0
    last_elem = False
    for elem in range(0, len(arr)):
        diphone = arr[elem]
        if elem == len(arr)-1:
            last_elem = True
        start, end = get_start_and_end(diphone, last_elem)      # Diphongrenzen berechnen
        path = get_db() + "\\IPATS_emuDB\\0000_ses\\0001" + diphone[0] + "_bndl\\0001" + diphone[0] + ".wav"
        sound = AudioSegment.from_file(path, format="wav")

        numpy_arr = audioseg_to_np(sound)       # Umwandlung von AudioSegment-Obj zu Numpy-Array
        start_ms = samples_to_ms(find_zerocrossings(numpy_arr, start))      # zusätzlich Nulldurchgänge berechnen
        end_ms = samples_to_ms(find_zerocrossings(numpy_arr, end))

        if len(concatenate) < cross_new:            # vermeiden, dass crossfade zu lang ist
            cross_old = len(concatenate) * 0.1
        elif int((end_ms - start_ms)) < cross_new:
            cross_old = int((end_ms - start_ms) * 0.1)
        else:
            cross_old = cross_new

        cross_new = int((end_ms - start_ms) * 0.1)  # Berechnung der Crossfade-Dauer (10% der Unit)

        slices = sound[start_ms:end_ms]                                 # Diphon aus Audiodatei heraus kopieren
        concatenate = concatenate.append(slices, crossfade=cross_old)   # Diphone mit Crossfade überblenden

    return audioseg_to_np(concatenate)


def export(numpy_array):
    '''
        exportiert einen Numpy-Array als WAVE-Datei
    '''
    save = os.path.join(os.path.dirname(__file__), '..')
    try:
        soundfile.write(file=save + "\\concatenated_word.wav", data=numpy_array, samplerate=get_sr())
        return
    except RuntimeError:        # für den Fall, dass die Audiodatei noch geöffnet ist
        pygame.mixer.music.unload()
        os.remove(save + "\\concatenated_word.wav")
        soundfile.write(file=save + "\\concatenated_word.wav", data=numpy_array, samplerate=get_sr())
        return
