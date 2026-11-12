import csv
from collections import Counter
import math

# -----------------------------
# 1. RÉCUPÉRATION DES TIRAGES (CSV)
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
# 2. MÉTHODE POISSON
# -----------------------------
def calcul_scores_poisson(tirages):
    compteur = Counter()
    recence_score = Counter()

    total_tirages = len(tirages)

    for i, tirage in enumerate(tirages):
        for num in tirage:
            compteur[num] += 1
            recence_score[num] += (total_tirages - i)

    scores = {}

    lambda_ = sum(compteur.values()) / 50

    for num in range(1, 51):
        freq = compteur[num]
        poisson = 1 - math.exp(-lambda_)

        score = freq * 2 + recence_score[num] + poisson * 5
        scores[num] = score

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
    numeros_tries = calcul_scores_poisson(tirages)

    print("Tirages récupérés :", tirages)
    print("Top numéros :", numeros_tries[:10])
