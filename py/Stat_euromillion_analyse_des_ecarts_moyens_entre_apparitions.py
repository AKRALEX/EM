import csv
import random
from collections import Counter
import math
from datetime import datetime

# -----------------------------
# 1. RÉCUPÉRATION DES TIRAGES (CSV)
# -----------------------------
def recuperer_tirages(nb_tirages=10):
    import csv

    chemin = "C:/Python/Source/euromillions_202002.csv"
    tirages = []

    with open(chemin, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')

        print("Colonnes détectées :", reader.fieldnames)

        for i, row in enumerate(reader):
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
                print("Erreur ligne:", row)
                continue

    return tirages

# -----------------------------
# 2. CALCUL SCORE HYBRIDE
# -----------------------------
def calcul_scores_ecarts(tirages):
    """
    Méthode 5 : analyse des écarts moyens entre apparitions
    Plus un numéro apparaît avec des écarts courts et répétés,
    plus son score est élevé.
    """

    positions = {num: [] for num in range(1, 51)}

    # On enregistre les positions d'apparition
    # i = 0 => tirage le plus récent
    for i, tirage in enumerate(tirages):
        for num in tirage:
            positions[num].append(i)

    scores = {}

    for num in range(1, 51):
        pos = positions[num]

        if len(pos) >= 2:
            ecarts = []
            for j in range(len(pos) - 1):
                ecart = pos[j + 1] - pos[j]
                ecarts.append(ecart)

            ecart_moyen = sum(ecarts) / len(ecarts)

            # Plus l'écart moyen est petit, meilleur est le score
            scores[num] = 1 / ecart_moyen

        elif len(pos) == 1:
            # Une seule apparition : score faible
            scores[num] = 0.1

        else:
            # Jamais apparu
            scores[num] = 0

    # --- CORRECTIF ex-aequo -------------------------------------------
    # sorted() est STABLE : a score egal il conserve l'ordre d'insertion
    # (1, 2, 3, ...). Avec peu de tirages les scores sont massivement
    # ex-aequo => le "classement" devenait un bloc de petits numeros.
    # On departage donc les egalites au hasard.
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
    numeros_tries = calcul_scores_ecarts(tirages)

    print("Tirages récupérés :", tirages)
    print("Top numéros :", numeros_tries[:10])
