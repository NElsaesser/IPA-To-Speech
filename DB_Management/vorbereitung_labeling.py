import csv
from pydub import AudioSegment, effects


def create_csv():

    '''
        Erstellung einer CSV-Datei für den Web-Service MAUS.
        Erzeugt wird für jedes aufgenommene Logatom genau eine Datei
        mit zwei Spalten, in denen die erste Spalte die orthographische
        Umschrift (mediaitem) und in der zweiten Spalte die
        X-SAMPA-Umschrift (recinstructions) der Logatome beinhaltet.
        
        Die CSV-Dateien sind NICHT auf Github, da sie für das System
        keinen Nutzen besitzen, können aber durch ausführen der
        Funktion erstellt werden.
    '''

    with open("IPATS_Datenbank_script.xml", mode="r", encoding="latin-1") as file:
        file = file.read().split('\n')
        i = 0
        write = False
        find = False
        orto = ""
        pron = ""
        for line in file:
            if "itemcode" in line and "File-nr" not in line:
                i += 1
                write = True
            if "mediaitem" in line:
                for x in line:
                    if x == "<":
                        find = False
                    if find:
                        orto += x
                    if x == ">":
                        find = True
                find = False
            if "recinstructions" in line:
                for x in line:
                    if x == "<":
                        find = False
                    if find:
                        pron += x
                    if x == ">":
                        find = True
                find = False
                pron = pron.replace("Q", "?")	# korrektes SAMPA-Zeichen für glottalen Plositv einsetzen
            if "</recording>" in line and write:
                file_name = "RECS_copy\\0001" + str(i) + ".csv"
                with open(file_name, mode="w", encoding="latin-1") as csv_file:
                    new_csv = csv.writer(csv_file, delimiter=';', skipinitialspace=True, quotechar=None)
                    new_csv.writerow([orto, pron])
                    print(file_name + " created.")
                orto = ""
                pron = ""


def normalize():

    '''
        Noramlisierung aller aufgenommenen Audiodateien
    '''

    for i in range(1, 4822):
        path = "RECS_copy\\0001" + str(i) + ".wav"
        raw = AudioSegment.from_file(path, format="wav")
        norm = effects.normalize(raw)
        norm.export(path, format="wav")


# create_csv()
# normalize()
