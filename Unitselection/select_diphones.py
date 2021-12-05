import os
import csv
import json


def get_ipa():
    '''
        gibt das IPA als verschachtelte und durchsuchbare Dictionaries aus
        None Werte stehen für Phoneme im IPA, die (im Deutschen) nicht existieren
    '''
    plosiv = {0: ["p", "b"], 4: ["t", "d"], 7: ["k", "g"], 9: ["?", None]}
    nasal = {0: [None, "m"], 4: [None, "n"], 7: [None, "N"]}
    trill = {4: [None, "r"], 8: [None, "R"]}
    frikativ = {1: ["f", "v"], 2: [None, "w"], 3: ["T", "D"], 4: ["t", "d"],
                5: ["S", "Z"], 7: ["x", None]}
    approximant = {6: [None, "j"]}
    lateral_approximant = {4: [None, "l"], 6: [None, "L"]}
    affrikat = {0: ["pf", None], 4: ["ts", None], 5: "tS"}
    vok_front = {
        0: [None, "i:", None, None, "\"i:", None, None, "y:", None, None, "\"y:", None],
        1: ["I", None, None, "\"I", None, None, "Y", None, None, "\"Y", None, None],
        2: [None, "e:", None, None, "\"e:", None, None, "2:", None, None, "\"2:", None],
        4: ["E", "E:", "E:~", "\"E", "\"E:", "\"E:~", "9", None, None, "\"9", None, None],
        6: ["a", "a:", "a:~", "\"a", "\"a:", "\"a:~", None, None, None, None, None, None]
    }
    vok_central = {3: ["@"], 5: ["6"]}
    vok_back = {
        0: [None, None, None, None, None, None, None, "u:", None, None, "\"u:", None],
        1: [None, None, None, "U", None, None, "\"U", None, None, None, None, None, None],
        2: [None, None, None, None, "o:", "o:~", None, None, None, None, "\"o:", "\"o:~"],
        4: [None, None, None, "O", None, None, None, None, None, "\"O", None, None]
    }
    diphthonge = {0: ["EI", "aI", "aU", "OY", "@U"], 1: ["\"EI", "\"aI", "\"aU", "\"OY", "\"@U"]}
    pause = {0: ["<p:>"]}

    ipa = {"konsonanten": {0: plosiv, 1: nasal, 2: trill, 3: frikativ, 4: approximant, 5: lateral_approximant, 6: affrikat},
           "vokale": {0: vok_front, 1: vok_central, 2: vok_back}, "anderes": {0: diphthonge, 1: pause}}

    return ipa


def find_file_nrs(list):
    '''
        sucht nach den benötigten Diphonen
        und gibt die zugehörigen Dateinummern zurück
    '''
    with open(os.path.dirname(__file__) + "\\logatome_lookup.csv", mode="r", encoding="latin-1") as file:
        file = csv.reader(file, delimiter=',', skipinitialspace=True, quotechar=None)
        logatome = []
        for line in file:
            logatome.append(line)

        file_nrs = []

        for item in list:
            found = False
            diphone = item[0] + item[1]
            for line in logatome:
                if diphone == line[3]:
                    file_nrs.append(line[0])
                    found = True
                    break
            if not found:
                file_nrs.append(None)

        return file_nrs


def find_timestamps(path, di_li):
    '''
        durchsucht die _annot.json-Dateien der Logatome
        und gibt die Timestamps der Diphone zurück.
        Die _annot.json-Datei wird mit Hilfe des json-Moduls
        als verschachtelte Dictionaries eingelesen.
    '''
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'DB_Management')) + path) as json_file:
        data = json.load(json_file)
        found = False
        start_di, duration, end_di = 0, 0, 0

        for defs in data["levels"]:
            if defs["name"] == "MAU":
                for x in defs["items"]:
                    for y in x["labels"]:
                        if found:
                            # in den Annotationsdateien fehlen die Betonungszeichen
                            if y["value"] == di_li[1].replace("\"", ""):
                                end_di = int(x["sampleStart"]) + int(x["sampleDur"])
                                return [start_di, duration, end_di]
                            else:
                                found = False
                        # in den Annotationsdateien fehlen die Betonungszeichen
                        if y["value"] == di_li[0].replace("\"", ""):
                            start_di = int(x["sampleStart"])
                            duration = int(x["sampleDur"])
                            found = True


found = []
phon_eins = ""
phon_zwei = ""


def ersatzdiphon(dictionary, phon1, phon2):
    '''
        Falls das ermittelte Diphon in der Datenbank nicht gefunden werden kann,
        wird hier ein Ersatzdiphon ermittelt und zurückgegeben, das dem eingegebenen
        Diphon im IPA möglichst nahe ist.
    '''

    global phon_eins
    global phon_zwei
    global found
    for key, values in dictionary.items():
        if isinstance(values, dict):
            '''
                Da das IPA in verschachtelten Dictionaries hinterlegt ist,
                werden diese Dictionaries top-down durchsucht.
                Dies geschieht rekursiv, indem so lange gesucht wird,
                bis in einem Dictionary kein weiteres Dictionary mehr enthalten ist.
            '''
            if found:
                return
            ersatzdiphon(values, phon1, phon2)
        else:
            if phon1 != "<p:>":         # erstes Phon des Diphons wird betrachtet (sofern es keine Pause ist)
                for element in values:  # überprüfen, ob das Phon im grade betrachteten Array enthalten ist
                    if element == phon1:
                        index_ges = values.index(element)
                        for key in dictionary:
                            li = dictionary[key]                # "Reihe", in der das Phon steht
                            for i in range(0, len(li)):         # IPA wird horizontal durchsucht
                                index_gef = index_ges - i       # In "Reihe" wird i Schritte links des Phons gesucht.
                                if li[index_gef] is not None:   # ob ein Phon gefunden werden kann
                                    phon_eins = li[index_gef]
                                    phon_zwei = phon2 + ""      # theoretisch mögliches Diphon wird generiert
                                    if None not in find_file_nrs([[phon_eins, phon_zwei]]): # Überprüfung, ob neues Diphon in Datenbank vorkommt
                                        found = find_file_nrs([[phon_eins, phon_zwei]])
                                        return found
            if phon2 != "<p:>":     # Vorgehensweise analog zu der des ersten Phons
                for element in values:
                    if element == phon2:
                        index_ges = values.index(element)
                        for key in dictionary:
                            li = dictionary[key]
                            for i in range(0, len(li)):
                                index_gef = index_ges - i
                                if li[index_gef] is not None:
                                    phon_zwei = li[index_gef]
                                    phon_eins = phon1 + ""
                                    if None not in find_file_nrs([[phon_eins, phon_zwei]]):
                                        found = find_file_nrs([[phon_eins, phon_zwei]])
                                        return found
            if phon1 == "<p:>" and phon2 == "<p:>":
                return [None]
        if found:
            return [found[0], phon_eins, phon_zwei]
    return [None]


def select(di_list):
    '''
        speichert alle benötigten Dateinummern und die
        zu den Diphonen gehörenden Timestamps in der
        benötigten Reihenfolge in einem Dictionary.
    '''

    all_file_nrs = find_file_nrs(di_list)
    di_array = []
    i = 0
    for nr in all_file_nrs:
        diphon = di_list[i]
        if nr is None:      # Diphon konnte nicht gefunden werden & wird ersetzt

            global found
            global phon_eins
            global phon_zwei

            found = []      # falls globale Var verändert wurden, werden sie hier wieder "zurückgesetzt"
            phon_eins = ""  # wichtig falls zB 2 Diphone in 1 Wort ersetzt werden müssen
            phon_zwei = ""

            ersatz = ersatzdiphon(get_ipa(), diphon[0], diphon[1])

            try:
                diphon = [ersatz[1], ersatz[2]]
            except IndexError:
                return False
            nr = ersatz[0]
        timest = find_timestamps(
            "\\IPATS_emuDB\\0000_ses\\0001" + nr + "_bndl\\0001" + nr + "_annot.json", diphon)
        di_array.append([nr, timest[0], timest[1], timest[2]])

        i += 1

    return di_array
