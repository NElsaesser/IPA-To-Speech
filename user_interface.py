import os
from tkinter import*
from tkinter import messagebox
import pygame
import mmap
from IPA2diphones import IPAtoSAMPA
from Unitselection import select_diphones
from Concatenation import concat_final


file = None


def send_input():
    ipa_string = str(textinput.get())                   # zu synthetisierenden IPA-Text einlesen
    phon_liste = IPAtoSAMPA.IPA_to_SAMPA(ipa_string)    # zu SAMPA umwandeln
    diphones = IPAtoSAMPA.create_diphones(phon_liste)   # in Diphone umwandeln
    arr = select_diphones.select(diphones)              # Diphone aus DB auswählen

    if not arr:
        messagebox.showinfo("Error", "It seems like there's something wrong with your input. "
                                     "Try again with another word!")
        return

    # Konkatenation abhängig vom gewählten Modus
    if mode.get() == 1:
        concat_method = concat_final.simple_concatenation(arr)
    elif mode.get() == 2:
        concat_method = concat_final.concatenation_zerocross(arr)
    else:
        concat_method = concat_final.concatenation_crossfade(arr)

    try:
        # eventuelle Grundfrequenzglättung durchführen
        if pitch_estimation.get() == 1:
            f0 = concat_final.estimate_pitch_yin(concat_method)
            new_f0 = concat_final.calculate_new_pitch(f0)
            final = concat_final.smooth_pitch(concat_method, new_f0)
        elif pitch_estimation.get() == 2:
            f0 = concat_final.estimate_pitch_yaapt(concat_method)
            new_f0 = concat_final.calculate_new_pitch(f0)
            final = concat_final.smooth_pitch(concat_method, new_f0)
        else:
            final = concat_method

    except ValueError:
        messagebox.showinfo("Error", "It seems like there's something wrong with your input. "
                                     "Try again with another word!")
        return

    concat_final.export(final)      # AUdiodatei exportieren


def play():
    try:
        # Audiodatei öffnen und abspielen

        global file
        target = open("concatenated_word.wav")
        file = mmap.mmap(target.fileno(), 0, access=mmap.ACCESS_READ)
        pygame.mixer.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play(loops=0)
    except FileNotFoundError:
        messagebox.showinfo("Error", "Please enter a word for the synthesis first.")


def on_closing():
    if messagebox.askokcancel("Quit", "Do you really want to leave the IPA-To-Speech-System?"):
        display.destroy()

        # Datei löschen, damit sie beim nächsten Benutzen des Systems nicht abgespielt wird/werden kann
        if os.path.exists("concatenated_word.wav"):
            global file
            if file:
                file.close()
            os.remove("concatenated_word.wav")


display = Tk()
display.title('IPA-To-Speech')      # Überschrift
display.geometry("800x500")         # Fenstergröße

title = Label(display, text="IPA-To-Speech", bd=9, relief=GROOVE, font=("Helvetica", 30, "bold"), bg="white", fg="black")
title.pack(side=TOP, fill=X)

Label(display, text="Insert your IPA-Text here:").pack()

# Textinput
textinput = Entry(display)
send_button = Button(display, text="Synthesize!", command=textinput.bind("<Return>", send_input))
textinput.pack()
send_button.pack()

# Anlegen der Radiobuttons
radio_frame_mode = Frame(display, width=400)
radio_frame_pitch = Frame(display, width=400)
button_frame = Frame(display)

radio_frame_mode.pack(side="left", fill="both", expand=True)
radio_frame_pitch.pack(side="right", fill="both", expand=True)
button_frame.pack(side="bottom", fill="both", expand=True)

# Radiobuttons zur Konkatenation (links)
mode = IntVar()
simple = Radiobutton(radio_frame_mode, text="Simple Concatenation", variable=mode, value=1).pack()
zerocross = Radiobutton(radio_frame_mode, text="Zerocrossing Concatenation", variable=mode, value=2).pack()
crossfade = Radiobutton(radio_frame_mode, text="Crossfade Concatenation", variable=mode, value=3).pack()
mode.set(3)

# Radiobuttons zur Grundfrequenzglättung (rechts)
pitch_estimation = IntVar()
yin = Radiobutton(radio_frame_pitch, text="PYIN", variable=pitch_estimation, value=1).pack()
yaapt = Radiobutton(radio_frame_pitch, text="pYAAPT", variable=pitch_estimation, value=2).pack()
no_pitch_correct = Radiobutton(radio_frame_pitch, text="No Pitch Correction", variable=pitch_estimation, value=3).pack()
pitch_estimation.set(2)

play_button = Button(button_frame, text="Play IPA", font=("Helvetica", 32), command=play)
play_button.pack(side="left")

# Schließen des Programmes
display.protocol("WM_DELETE_WINDOW", on_closing)

display.mainloop()
