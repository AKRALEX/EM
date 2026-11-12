import csv
import random

# -----------------------------
# 1. RÉCUPÉRATION DES TIRAGES
# -----------------------------
def recuperer_tirages(nb_tirages=10):
    chemin = "C:/Python/Source/euromillions_202002.csv"
    tirages = []

    with open(chemin, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")

        for row in reader:
            try:
                numeros = [
                    int(row["boule_1"]),
                    int(row["boule_2"]),
                    int(row["boule_3"]),
                    int(row["boule_4"]),
                    int(row["boule_5"]),
                ]
                tirages.append(numeros)

                if len(tirages) >= nb_tirages:
                    break
            except Exception as e:
                print("Erreur lecture ligne :", row)
                print("Détail :", e)

    return tirages


# -----------------------------
# 2. MÉTHODE 7 : RÉPARTITION PAR CLASSES
# -----------------------------
def calcul_scores_classes(tirages):
    """
    Favorise les numeros appartenant aux classes (dizaines) les plus
    frequentes, MAIS en tenant compte aussi du numero lui-meme.

    CORRECTIF : l'ancienne version donnait a chaque numero le score de sa
    dizaine, et rien d'autre. Sur 50 numeros il n'existait donc que 5 scores
    distincts : tous les numeros d'une dizaine etaient ex-aequo, et le top-N
    etait TOUJOURS un bloc de 10 numeros consecutifs (41..50). Resultat
    mesure : 4.39 numeros par dizaine et une somme moyenne de 221, alors que
    les tirages reels donnent 2.21 et 129 - la methode produisait des grilles
    jamais observees en six ans.

    Le score combine desormais deux niveaux :
        poids de la dizaine  x  frequence propre du numero
    La dizaine oriente toujours le classement, mais les numeros d'une meme
    dizaine ne sont plus interchangeables, et un numero souvent sorti d'une
    dizaine moyenne peut depasser un numero jamais sorti de la dizaine forte.
    """
    classes = {
        1: range(1, 11),
        2: range(11, 21),
        3: range(21, 31),
        4: range(31, 41),
        5: range(41, 51),
    }

    scores_classes = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    frequences     = {num: 0 for num in range(1, 51)}

    for tirage in tirages:
        for num in tirage:
            frequences[num] += 1
            for classe_id, intervalle in classes.items():
                if num in intervalle:
                    scores_classes[classe_id] += 1
                    break

    total = sum(scores_classes.values()) or 1

    scores = {}
    for num in range(1, 51):
        for classe_id, intervalle in classes.items():
            if num in intervalle:
                # poids relatif de la dizaine, jamais nul (lissage +1)
                poids_dizaine = (scores_classes[classe_id] + 1) / (total + 5)
                # frequence propre du numero, lissee elle aussi
                poids_numero  = frequences[num] + 1
                scores[num] = poids_dizaine * poids_numero
                break

    import random as _rnd_tie
    numeros_tries = sorted(
        scores, key=lambda _n: (scores[_n], _rnd_tie.random()), reverse=True
    )
    return numeros_tries

# -----------------------------
# 3. TEST LOCAL OPTIONNEL
# -----------------------------
if __name__ == "__main__":
    tirages = recuperer_tirages(10)
    numeros_tries = calcul_scores_classes(tirages)

    print("Tirages récupérés :", tirages)
    print("Top numéros :", numeros_tries[:10])
