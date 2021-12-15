import os


def get_betonte_vokale():
    betonte_vokale = ["aI", "OY", "aU", "a:~", "a:", "a", "e:", "EI", "E:~", "E:", "E", "i:", "I", "o:~",
                      "o:", "O", "2:", "9", "y:", "Y", "u:", "@U", "U"]
    return betonte_vokale


def get_alle_vokale():
    unbetonte_vokale = ["@", "6"]
    alle_vok = unbetonte_vokale + get_betonte_vokale()
    return alle_vok


def get_vokale_de():
    '''
        Alle vokalischen Laute, die im Deutschen vorkommen
        oder anhand der Datei lookup.txt durch solche ersetzt werden.
    '''

    vokale_de = ["ɪ", "ɛ", "æ", "a", "ɑ", "ɔ", "ʌ", "ɒ", "ʊ", "ʏ", "œ", "iː", "eː", "εː", "aː", "ɑː", "oː", "uː", "yː",
                 "øː", "ɜ", "aɪ", "aʊ", "ɔʏ", "ɔɪ"]
    return vokale_de


def adjust_IPA(ipa_string):
    '''
        vor syllabisierten Konsonanten wird ein 'ə' hinzugefügt.
    '''

    syllabic = ipa_string.find("̩")
    if syllabic >= 0:
        ipa_string = ipa_string[:syllabic - 1] + "ə" + ipa_string[syllabic - 1] + ipa_string[syllabic + 1:]

    '''
        treten im IPA-String Vokale ohne Längungszeichen auf,
        die im Dt nur gelängt auftreten,
        so wird das Längungszeichen nachträglich hinzugefügt
    '''

    lengthened_vocals = ["i", "e", "u", "y", "ø", "o", "ɜ"]
    x = 1
    for char in ipa_string:
        if char in lengthened_vocals:
            if len(ipa_string) == x:
                ipa_string = ipa_string[:x] + "ː" + ipa_string[x:]
            elif ipa_string[x] != "ː":
                ipa_string = ipa_string[:x] + "ː" + ipa_string[x:]
                x += 1
        x += 1

    '''
        beginnt ein Wort mit einem deutschen Vokal, so wird vor diesem ein glottaler Plosiv eingefügt.
    '''

    for vok in get_vokale_de():
        if ipa_string.strip("ˈ").strip("ˌ").startswith(vok):
            ipa_string = "ʔ" + ipa_string

    return ipa_string


def IPA_to_SAMPA(ipa_string):
    ipa_string = adjust_IPA(ipa_string)

    '''
        wandelt eine gegebene Zeichenkette in
        IPA-Transkription in die entsprechende
        Zeichenkette in X-SAMPA-Transkription um.
        Hierbei wird die Datei "lookup.txt" verwendet.
        In dieser Datei stehen die X-SAMPA-Umschriften
        in der ersten Spalte, und die darauf gemappten
        IPA-Zeichen in den weiteren Spalten.
    '''

    File = open(os.path.dirname(__file__) + "\\lookup.txt", "r", encoding="utf-8").read().split('\n')
    lookuptable = []
    for x in File:
        values = x.split(",")
        lookuptable.append(values)

    sampa_str = ""
    vorne = ipa_string
    hinten = ""
    phon_liste = ["<p:>"]
    while vorne != "":
        Found = False
        for line in lookuptable:
            for i in range(1, len(line)):
                if str(line[i]) == str(vorne):        # wenn IPA gefunden werden kann
                    sampa_str += str(line[0])         # Füge SAMPA dem SAMPA-String hinzu
                    phon_liste.append(str(line[0]))
                    vorne = hinten
                    hinten = ""
                    Found = True

        if not Found:
            hinten = vorne[-1:] + hinten
            vorne = vorne[:-1]
            if vorne == "" and hinten != "":    # nicht gefundene Zeichen werden übersprungen
                vorne = hinten[1:]
                hinten = ""

    phon_liste.append("<p:>")

    return phon_liste


def create_diphones(phon_liste):
    betonte_vokale = get_betonte_vokale()
    diphones = []

    '''
        Falls der String ein Betonungszeichen enthält,
        wird das Betonungszeichen dem nächsten Vokal,
        der theoretisch betont vorkommen kann, zugewiesen.
        Wird kein solcher Vokal gefunden, verfällt das Betonungszeichen.
    '''

    i = 0
    temp = phon_liste.copy()

    for element_a in phon_liste:
        if element_a == "\"":
            index_elemb = i
            for element_b in temp[i:]:
                if element_b in betonte_vokale:
                    new_elem = "\"" + element_b
                    temp.pop(index_elemb)
                    temp.insert(index_elemb, new_elem)
                    break
                index_elemb += 1
            temp.pop(i)
            i -= 1

        i += 1

    '''
        Diphone werden als geschachtelte Arrays ausgegeben.
    '''

    for i in range(len(temp)-1):
        dip = [temp[i], temp[i + 1]]
        diphones.append(dip)
        i += 1

    return diphones


# ipa_string = "kɔmˈpjuːtɐlɪŋɡu̯ɪstɪk"
# phon_liste = IPA_to_SAMPA(ipa_string)
# print(create_diphones(phon_liste))
