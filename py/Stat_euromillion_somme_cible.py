import csv
import random

# -----------------------------
# 1. RÉCUPÉRATION DES TIRAGES (CSV)
# -----------------------------
def recuperer_tirages(nb_tirages=10):
    chemin = "C:/Python/Source/euromillions_202002.csv"
    tirages = []

    with open(chemin, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")

        print("Colonnes détectées :", reader.fieldnames)

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
                print("Erreur ligne :", row)
                print("Détail :", e)
                continue

    return tirages


# -----------------------------
# 2. MÉTHODE 9 : SOMME CIBLE
# -----------------------------
def calcul_scores_somme_cible(tirages):
    """
    Favorise les numeros qui apparaissent dans les tirages dont la SOMME est
    proche de la somme moyenne observee.

    CORRECTIF : l'ancienne version notait chaque numero par sa distance a
    somme_moyenne / 5, soit environ 26. Le classement etait donc toujours une
    bande contigue autour du centre (19..30), et les grilles produites
    faisaient 4.22 numeros dans la meme dizaine pour une etendue de 11, la
    ou les tirages reels donnent 2.21 et 33.7.

    L'erreur de fond : viser une somme totale ne veut pas dire choisir cinq
    numeros proches de la moyenne. 3-14-27-41-44 fait aussi 129 que
    25-26-27-28-29, et ressemble bien davantage a un vrai tirage. La
    contrainte de somme appartient a la grille entiere - elle est desormais
    appliquee par em_plausibilite.est_plausible().
    Ce qui reste ici est une vraie mesure : parmi les tirages passes dont la
    somme etait "normale", quels numeros revenaient le plus ?
    """
    if not tirages:
        return list(range(1, 51))

    sommes = [sum(tirage) for tirage in tirages]
    somme_moyenne = sum(sommes) / len(sommes)

    scores = {num: 0.0 for num in range(1, 51)}

    for tirage in tirages:
        ecart = abs(sum(tirage) - somme_moyenne)
        # Un tirage compte d'autant plus que sa somme etait proche de la
        # moyenne. Decroissance douce : a 40 d'ecart le poids vaut encore 0.5.
        poids = 1.0 / (1.0 + (ecart / 40.0) ** 2)
        for num in tirage:
            scores[num] += poids

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
    numeros_tries = calcul_scores_somme_cible(tirages)

    print("Tirages récupérés :", tirages)
    print("Top numéros :", numeros_tries[:10])
