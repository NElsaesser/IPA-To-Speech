import csv


def get_betontevokale():

    """
        Die Liste der betonten Vokale ist so geordnet, dass zuerst Vokale mit
        mehr Zeichen angegeben sind. So steht bspw. "aU" vor "a" und "U".
        So soll verhindert werden, dass ein Diphthong "aufgespalten" wird
        und anstelle des "aU"s das "U" als betont markiert wird.
    """

    return ["aI", "OY", "aU", "a:~", "a:", "a", "e:", "EI", "E:~", "E:", "E", "i:",
            "I", "o:~", "o:", "O", "2:", "9", "y:", "Y", "u:", "@U", "U"]


def stress_lastsyl():

    """
        In Logatomen, bei denen das aufzunehmende Diphon kein
        Endungs-Phonem ist, wird vor der letzten Silbe
        ein Betonungszeichen (") eingefügt.
        Diphone, die Endungsphoneme sind, enden mit einem "*",
        bei diesen wird die erste Silbe betont.
    """

    fileNr = []
    logatome = []
    sampa_x = []
    diphone = []
    language = []

    with open("LogatomeList_original.csv", mode="r") as csv_file:
        Liste_alt = csv.reader(csv_file, delimiter=',')

        for line in Liste_alt:
            sampa = line[2]
            diphone_now = line[3]
            if diphone_now.find("*") <= 0:
                word = sampa[:-3] + "\"" + sampa[-3:]
                fileNr.append(line[0])
                logatome.append(line[1])
                sampa_x.append(word)
                diphone.append(line[3])
                language.append(line[4])
            elif diphone_now.find("*") == len(diphone_now)-1:
                word = "\"" + sampa
                fileNr.append(line[0])
                logatome.append(line[1])
                sampa_x.append(word)
                diphone.append(line[3])
                language.append(line[4])
            else:
                fileNr.append(line[0])
                logatome.append(line[1])
                sampa_x.append(line[2])
                diphone.append(line[3])
                language.append(line[4])

    with open("logatome_unbetont.csv", mode="w", newline='') as new_file:
        liste_schreiben = csv.writer(new_file, delimiter=',', skipinitialspace=True, quotechar=None)
        for line in range(len(fileNr)):
            liste_schreiben.writerow([fileNr[line], logatome[line], sampa_x[line], diphone[line], language[line]])


def stress_diphones():

    """
        Ist ein Vokal aus betonte_vokale in dem grade betrachteten Diphon enthalten,
        soll der Vokal in der SAMPA-Umschrift betont dargestellt werden.
        Dazu wird ein " vor den jeweiligen Vokal gesetzt. Gleiches gilt für das Diphon.
        Steht der Vokal am Wortanfang, so steht das " auch am Wortanfang.
    """

    fileNr = []
    logatome = []
    sampa_x = []
    diphone = []
    language = []

    with open("LogatomeList_original.csv", mode="r") as csv_file:
        Liste_alt = csv.reader(csv_file, delimiter=',', quotechar=None)
        betonte_vokale = get_betontevokale()

        for line in Liste_alt:
            sampa = line[2]
            diphon_einzeln = line[3]
            for vok in betonte_vokale:
                if vok in diphon_einzeln:
                    if diphon_einzeln.find("*") > 0:        # Logatome, bei denen Target-Diphon am Ende steht
                        ende = (len(diphon_einzeln)-1) * -1
                        word = sampa[:ende] + "\"" + sampa[ende:]   # Diphon im Wort als betont markieren
                        diphon_betont = "\"" + diphon_einzeln       # Diphon einzeln als betont markieren
                    elif diphon_einzeln.find("*") == 0:     # Logatome, bei denen Targe-Diphon am Anfang steht
                        word = "\"" + sampa         # Betonungszeichen an den Anfang setzen
                        diphon_betont = diphon_einzeln[0] + "\"" + diphon_einzeln[1:]
                    else:
                        diphon_index = sampa.find(diphon_einzeln)   # Stelle des Diphons im Wort finden
                        betont_vok_index = sampa.find(vok, diphon_index)    # Vokal im Diphon finden
                        word = sampa[:betont_vok_index] + "\"" + sampa[betont_vok_index:]
                        diphon_betont = diphon_einzeln[:diphon_einzeln.find(vok)] + "\"" \
                                        + diphon_einzeln[diphon_einzeln.find(vok):]

                    fileNr.append(line[0])
                    logatome.append(line[1])
                    sampa_x.append(word)
                    diphone.append(diphon_betont)
                    language.append(line[4])
                    break

        with open("logatome_betont.csv", mode="w", newline='') as new_file:     # Listen als neue CSV exportieren
            liste_schreiben = csv.writer(new_file, delimiter=',', skipinitialspace=True, quotechar=None)
            for x in range(len(fileNr)):
                liste_schreiben.writerow([fileNr[x], logatome[x], sampa_x[x], diphone[x], language[x]])


def stress_second_vowel():

    """
        Einige Diphone bestehen aus zwei Vokalen, die beide betont vorkommen können.
        In diesen Fällen muss ein weiteres Logatom hinzugefügt werden, in dem
        der zweite Vokal als betont markiert wird.
    """

    fileNr = []
    logatome = []
    sampa_x = []
    diphone = []
    language = []

    with open("logatome_betont.csv", mode="r") as csv_file:
        Liste_alt = csv.reader(csv_file, delimiter=',', quotechar=None)
        betonte_vokale = get_betontevokale()
        diphthonge = ["aI", "OY", "aU", "EI", "@U"]

        for line in Liste_alt:
            sampa = line[2]
            diphon_einzeln = line[3]
            for vok in betonte_vokale:
                if vok in diphon_einzeln:
                    vok_index = diphon_einzeln.find(vok)
                    if diphon_einzeln[vok_index-1:vok_index+1] in diphthonge:
                        vok = diphon_einzeln[vok_index-1:vok_index+1]
                    if diphon_einzeln.find("\"" + vok) < 0:
                        sampa = sampa.replace("\"", "")
                        diphon_einzeln = diphon_einzeln.replace("\"", "")
                        diphon_index = sampa.find(diphon_einzeln)
                        betont_vok_index = sampa.find(vok, diphon_index)
                        word = sampa[:betont_vok_index] + "\"" + sampa[betont_vok_index:]
                        diphon_betont = diphon_einzeln[:diphon_einzeln.find(vok)] + "\"" \
                                        + diphon_einzeln[diphon_einzeln.find(vok):]

                        fileNr.append(line[0])
                        logatome.append(line[1])
                        sampa_x.append(word)
                        diphone.append(diphon_betont)
                        language.append(line[4])
                        break

    with open("logatome_betont_2vokale.csv", mode="w", newline='') as new_file:
        liste_schreiben = csv.writer(new_file, delimiter=',', skipinitialspace=True, quotechar=None)
        for x in range(len(fileNr)):
            liste_schreiben.writerow([fileNr[x], logatome[x], sampa_x[x], diphone[x], language[x]])


def find_wrong_end():

    """
        Bei einigen Logatomen stand die letzte Silbe der orthographischen Umschrift
        im Widerspruch zur SAMPA-Umschrift, weswegen die orthographische Umschrift
        im Folgenden angepasst wird.
        Des Weiteren werden alle Logatome (unbetonte Diphone + betonte Diphone)
        in einer Datei zusammen gefasst.
    """

    fileNr = []
    logatome = []
    sampa_x = []
    diphone = []
    language = []

    with open("logatome_unbetont.csv", mode="r", encoding="utf-8") as csv_file:
        Liste_alt = csv.reader(csv_file, delimiter=',', skipinitialspace=True, quotechar=None)

        for line in Liste_alt:
            logatom = line[1]
            if line[2].endswith("daU") and not line[1].endswith("DAU"):
                logatom = logatom[:-3] + "DAU"
                print("Logatom " + line[0] + ": " + line[2] + " -- " + line[1] + ", ersetzt mit " + logatom)

            fileNr.append(line[0])
            logatome.append(logatom)
            sampa_x.append(line[2])
            diphone.append(line[3])
            language.append(line[4])

        i = int(fileNr[-1])

        with open("logatome_betont.csv", mode="r", encoding="utf-8") as csv_file:
            Liste_alt = csv.reader(csv_file, delimiter=',', skipinitialspace=True, quotechar=None)

            for line in Liste_alt:
                i += 1
                logatom = line[1]
                if line[2].endswith("daU") and not line[1].endswith("DAU"):
                    logatom = logatom[:-3] + "DAU"
                    print("Logatom " + line[0] + ": " + line[2] + " -- " + line[1] + ", ersetzt mit " + logatom)

                fileNr.append(i)
                logatome.append(logatom)
                sampa_x.append(line[2])
                diphone.append(line[3])
                language.append(line[4])

        i = int(fileNr[-1])

        with open("logatome_betont_2vokale.csv", mode="r", encoding="utf-8") as csv_file:
            Liste_alt = csv.reader(csv_file, delimiter=',', skipinitialspace=True, quotechar=None)

            for line in Liste_alt:
                i += 1
                logatom = line[1]
                if line[2].endswith("daU") and not line[1].endswith("DAU"):
                    logatom = logatom[:-3] + "DAU"
                    print("Logatom " + line[0] + ": " + line[2] + " -- " + line[1] + ", ersetzt mit " + logatom)

                fileNr.append(i)
                logatome.append(logatom)
                sampa_x.append(line[2])
                diphone.append(line[3])
                language.append(line[4])

        with open("LogatomeList_final.csv", mode="w", newline='') as new_file:
            liste_schreiben = csv.writer(new_file, delimiter=',', skipinitialspace=True, quotechar=None)
            for x in range(len(fileNr)):
                liste_schreiben.writerow([fileNr[x], logatome[x], sampa_x[x], diphone[x], language[x]])


# stress_lastsyl()
# stress_diphones()
# stress_second_vowel()
# find_wrong_end()
