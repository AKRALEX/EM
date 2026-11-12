"""
em_plausibilite.py - filtre de plausibilite des grilles Euromillions

Une grille peut etre "bien scoree" par une methode et rester une grille que le
tirage n'a jamais produite. Ce module tranche cette question a partir des
tirages reels, pas d'une intuition.

CALIBRAGE (mesure sur les 685 tirages du CSV, 02/2020 -> 08/2026) :

    numeros dans une meme dizaine   moyenne 2.21
                                    4 ou plus : 1.8 % des tirages
                                    5         : 0.00 % (jamais observe)
    somme de la grille              moyenne 129   5e-95e centile : 78 - 176
    etendue (max - min)             moyenne 33.7  5e centile : 19
    tout pair / tout impair         ~3 % des tirages

Les seuils ci-dessous laissent donc passer l'immense majorite des tirages
reels et n'ecartent que les configurations qui n'arrivent pratiquement
jamais. Les regenerer, c'est reprendre une chance ; les garder, c'est jouer
une combinaison que six ans de tirages n'ont pas produite.

RECALIBRER : lancer  python em_plausibilite.py  pour reafficher les mesures
sur le CSV courant.
"""

# --- seuils stricts : le regime normal -----------------------------------
# Choisis pour ne rejeter que ce qui n'arrive pratiquement jamais : ces trois
# regles laissent passer 94.3 % des 685 tirages reels.
MAX_PAR_DIZAINE = 3      # 4 dans une dizaine : 1.75 % des tirages, 5 : jamais
SOMME_MIN       = 65     # 2e centile
SOMME_MAX       = 190    # 98e centile
ETENDUE_MIN     = 15     # 2e centile

# Tout pair ou tout impair arrive dans 4.2 % des tirages reels : c'est une
# configuration parfaitement normale, seulement moins jolie a regarder.
# Desactive par defaut - l'activer, c'est refuser des grilles legitimes.
REFUSER_PARITE_UNIQUE = False

# --- seuils larges : dernier repli, on ne bloque plus que l'aberrant -----
MAX_PAR_DIZAINE_LARGE = 4
SOMME_MIN_LARGE       = 60
SOMME_MAX_LARGE       = 200
ETENDUE_MIN_LARGE     = 12


def diagnostic(grille):
    """Renvoie (max_par_dizaine, somme, etendue, nb_pairs) - utile pour tracer."""
    dizaines = {}
    for n in grille:
        d = (n - 1) // 10
        dizaines[d] = dizaines.get(d, 0) + 1
    return (max(dizaines.values()), sum(grille),
            max(grille) - min(grille), sum(1 for n in grille if n % 2 == 0))


def est_plausible(grille, strict=True):
    """
    True si la grille ressemble a un tirage reel.
    strict=False applique les seuils larges (dernier repli).
    """
    if len(set(grille)) != 5:
        return False

    if strict:
        max_diz, s_min, s_max, e_min = (MAX_PAR_DIZAINE, SOMME_MIN,
                                        SOMME_MAX, ETENDUE_MIN)
    else:
        max_diz, s_min, s_max, e_min = (MAX_PAR_DIZAINE_LARGE, SOMME_MIN_LARGE,
                                        SOMME_MAX_LARGE, ETENDUE_MIN_LARGE)

    concentration, somme, etendue, nb_pairs = diagnostic(grille)

    if concentration > max_diz:      return False
    if not (s_min <= somme <= s_max): return False
    if etendue < e_min:              return False
    if strict and REFUSER_PARITE_UNIQUE and nb_pairs in (0, 5):
        return False
    return True


def raison_du_rejet(grille, strict=True):
    """Message court expliquant pourquoi la grille est rejetee (ou None)."""
    concentration, somme, etendue, nb_pairs = diagnostic(grille)
    if strict:
        max_diz, s_min, s_max, e_min = (MAX_PAR_DIZAINE, SOMME_MIN,
                                        SOMME_MAX, ETENDUE_MIN)
    else:
        max_diz, s_min, s_max, e_min = (MAX_PAR_DIZAINE_LARGE, SOMME_MIN_LARGE,
                                        SOMME_MAX_LARGE, ETENDUE_MIN_LARGE)
    if concentration > max_diz:
        return f"{concentration} numeros dans la meme dizaine"
    if somme < s_min or somme > s_max:
        return f"somme {somme} hors de [{s_min}, {s_max}]"
    if etendue < e_min:
        return f"etendue {etendue} < {e_min}"
    if strict and REFUSER_PARITE_UNIQUE and nb_pairs in (0, 5):
        return "tout pair" if nb_pairs == 5 else "tout impair"
    return None


# =========================================================================
# RECALIBRAGE : python em_plausibilite.py
# =========================================================================
if __name__ == "__main__":
    import csv, statistics, os

    chemin = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "Source", "euromillions_202002.csv")
    tirages = []
    with open(chemin, newline="", encoding="utf-8-sig") as f:
        for ligne in csv.DictReader(f, delimiter=";"):
            try:
                tirages.append(sorted(int(ligne[f"boule_{i}"]) for i in range(1, 6)))
            except Exception:
                continue

    diags = [diagnostic(g) for g in tirages]
    conc  = sorted(d[0] for d in diags)
    somme = sorted(d[1] for d in diags)
    etend = sorted(d[2] for d in diags)
    pair  = [d[3] for d in diags]
    n     = len(tirages)

    print(f"\n{n} tirages reels analyses\n" + "-" * 58)
    print(f"  max par dizaine   moyenne {statistics.mean(conc):.2f}")
    for k in (2, 3, 4, 5):
        print(f"       exactement {k}   {sum(1 for c in conc if c == k) / n:>7.2%}")
    print(f"  somme             moyenne {statistics.mean(somme):.0f}"
          f"   5e-95e centile : {somme[n // 20]} - {somme[n * 19 // 20]}")
    print(f"  etendue           moyenne {statistics.mean(etend):.1f}"
          f"   5e centile : {etend[n // 20]}")
    print(f"  tout pair/impair  {sum(1 for p in pair if p in (0, 5)) / n:.2%}")

    passent = sum(1 for g in tirages if est_plausible(g))
    print("-" * 58)
    print(f"  Avec les seuils actuels, {passent}/{n} tirages reels "
          f"({passent / n:.1%}) passeraient le filtre.")
    print()
