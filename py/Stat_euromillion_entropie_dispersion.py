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
def calcul_scores_dispersion(tirages):
    """
    Favorise les numeros anormalement eloignes des numeros recemment sortis.

    CORRECTIF : l'ancienne version notait chaque numero par sa distance
    moyenne aux numeros tires. Cette quantite est une courbe en V : elle est
    mathematiquement maximale aux extremites (1 et 50) et minimale au centre,
    QUELS QUE SOIENT les tirages. La methode classait donc toujours 1-2-3 et
    48-49-50 en tete sans rien lire des donnees.

    On retire maintenant la composante purement positionnelle : on compare la
    distance moyenne observee a celle qu'on obtiendrait si les numeros tires
    etaient repartis uniformement sur 1..50. Ce qui reste - le residu - est le
    seul signal reellement porte par les tirages.
    """
    tous_les_numeros = []
    for tirage in tirages:
        for num in tirage:
            tous_les_numeros.append(num)

    if not tous_les_numeros:
        return list(range(1, 51))

    scores = {}
    for num in range(1, 51):
        observe = sum(abs(num - autre) for autre in tous_les_numeros) / len(tous_les_numeros)
        # reference : distance moyenne de num a une repartition uniforme 1..50
        attendu = sum(abs(num - k) for k in range(1, 51)) / 50.0
        scores[num] = observe - attendu

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
    numeros_tries = calcul_scores_dispersion(tirages)

    print("Tirages récupérés :", tirages)
    print("Top numéros :", numeros_tries[:10])
