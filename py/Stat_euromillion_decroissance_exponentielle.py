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
def calcul_scores_exponentielle(tirages, alpha=0.85):
    """
    Méthode 3 : fréquence avec décroissance exponentielle
    Les tirages récents ont plus de poids que les anciens,
    avec une décroissance exponentielle.
    """

    scores = {num: 0 for num in range(1, 51)}
    total_tirages = len(tirages)

    for i, tirage in enumerate(tirages):
        # i=0 => tirage le plus récent => poids maximal
        poids = alpha ** i

        for num in tirage:
            scores[num] += poids

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
    numeros_tries = calcul_scores_exponentielle(tirages)

    print("Tirages récupérés :", tirages)
    print("Top numéros :", numeros_tries[:10])
