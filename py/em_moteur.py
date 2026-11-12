"""
em_moteur.py - moteur de generation des grilles, SANS interface.

C'est la logique de "EM_Dashboard - V2.py" (C:/Python), sortie de tkinter pour
pouvoir tourner dans un navigateur (Pyodide) comme sur le PC. Les fonctions
sont reprises a l'identique ; seules changent les entrees/sorties :

  - le CSV arrive sous forme de texte (plus de chemin C:/Python/...)
  - l'historique des sessions est passe en parametre et rendu en resultat
    (c'est la page web qui le stocke)
  - les scripts de methodes sont cherches dans le dossier de ce fichier

Les 11 methodes Stat_euromillion_*.py et em_plausibilite.py sont utilisees
telles quelles, sans modification.

REGLE HERITEE DU DASHBOARD : tirages[0] = tirage le plus RECENT. Ne jamais
inverser la liste.
"""

import csv
import importlib.util
import io
import math
import os
import random
from collections import Counter
from datetime import datetime

import em_plausibilite

# -----------------------------
# CONFIG (memes valeurs que le dashboard)
# -----------------------------
FENETRE               = 50    # DOIT rester identique a FENETRE_HISTORIQUE du backtest
QUOTA_FACTEUR         = 2.0
MEMOIRE_SESSIONS      = 4
POIDS_MEMOIRE         = 0.5
SEUIL_REDONDANCE      = 0.70
PROFONDEUR_REDONDANCE = 10
FILTRE_PLAUSIBILITE   = True

_DOSSIER = os.path.dirname(os.path.abspath(__file__))


# =========================================================
# LECTURE DU CSV FDJ
# =========================================================
def lire_tirages(texte_csv: str) -> list[dict]:
    """
    Lit le CSV FDJ (texte) et renvoie TOUS les tirages, du plus recent au
    plus ancien, sous la forme {"date", "boules", "etoiles"}.
    La date est normalisee en AAAA-MM-JJ pour pouvoir etre comparee.
    """
    if texte_csv.startswith("\ufeff"):
        texte_csv = texte_csv[1:]
    tirages = []
    for row in csv.DictReader(io.StringIO(texte_csv), delimiter=";"):
        try:
            boules  = [int(row[f"boule_{i}"]) for i in range(1, 6)]
            etoiles = [int(row[f"etoile_{i}"]) for i in range(1, 3)]
            j, m, a = row["date_de_tirage"].strip().split("/")
            date = f"{int(a):04d}-{int(m):02d}-{int(j):02d}"
        except Exception:
            continue
        tirages.append({"date": date, "boules": boules, "etoiles": etoiles})
    # Le fichier FDJ est deja trie du plus recent au plus ancien ; on le
    # garantit quand meme, car tout le reste en depend.
    tirages.sort(key=lambda t: t["date"], reverse=True)
    return tirages


# =========================================================
# CHARGEMENT DES METHODES
# =========================================================
_module_cache = {}


def charger_fonction(script: str, nom_fonction: str):
    """
    `script` vient de best_params.json ("C:/Python/Stat_...py"). On n'en
    garde que le nom de fichier, cherche a cote de ce module. Les espaces
    sont retires ("Stat_euromillion _cooccurrence.py") car le fichier est
    publie sans espace.
    """
    nom = script.replace("\\", "/").split("/")[-1]
    chemin = os.path.join(_DOSSIER, nom)
    if not os.path.exists(chemin):
        chemin = os.path.join(_DOSSIER, nom.replace(" ", ""))
    if chemin not in _module_cache:
        spec = importlib.util.spec_from_file_location("mod", chemin)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _module_cache[chemin] = mod
    return getattr(_module_cache[chemin], nom_fonction)


# =========================================================
# GENERATION D'UNE GRILLE (identique au dashboard)
# =========================================================
def variation_rebond(n: int, amp: int) -> int:
    for _ in range(100):
        v = n + random.randint(-amp, amp)
        if 1 <= v <= 50:
            return v
    return random.randint(1, 50)


def generer_grille(classement, nb_m, nb_a, amp, top_n) -> list[int]:
    pool   = classement[:max(top_n, nb_m)]
    grille = random.sample(pool, min(nb_m, len(pool)))
    taille = nb_m + nb_a

    if nb_a == 0 or amp == 0:
        for n in classement:
            if n not in grille:
                grille.append(n)
            if len(grille) >= taille:
                break
        return sorted(grille[:taille])

    for _ in range(1000):
        if len(grille) >= taille:
            break
        ref = random.choice(grille[:nb_m])
        v   = variation_rebond(ref, amp)
        if v not in grille:
            grille.append(v)
    else:
        for n in classement:
            if n not in grille:
                grille.append(n)
            if len(grille) >= taille:
                break

    return sorted(grille[:taille])


def distribuer(methodes: list[dict], nb_grilles: int) -> list[tuple[dict, int]]:
    n = len(methodes)
    if n == 0:
        return []
    base, reste = divmod(nb_grilles, n)
    return [(m, base + (1 if i < reste else 0)) for i, m in enumerate(methodes)]


# =========================================================
# MEMOIRE INTER-SESSIONS
# =========================================================
def charger_memoire(sessions: list) -> Counter:
    """
    Compteur pondere des numeros deja proposes lors des dernieres sessions.
    sessions[-1] = la plus recente => poids le plus fort.
    """
    freq = Counter()
    for i, sess in enumerate(reversed(sessions[-MEMOIRE_SESSIONS:])):
        poids = POIDS_MEMOIRE ** (i + 1)
        for grille in sess.get("grilles", []):
            for num in grille:
                freq[num] += poids
    return freq


def ajouter_session(sessions: list, grilles: list, etoiles: list = None) -> list:
    """Renvoie l'historique avec la session courante ajoutee (et tronque)."""
    if not grilles:
        return sessions
    sess = {
        "date":    datetime.now().isoformat(timespec="seconds"),
        "grilles": [list(g) for g in grilles],
    }
    if etoiles:
        # Champ en plus par rapport au PC : sans effet sur la memoire, il
        # sert seulement a reafficher la session complete sur le telephone.
        sess["etoiles"] = [list(e) for e in etoiles]
    return (list(sessions) + [sess])[-MEMOIRE_SESSIONS * 3:]


# =========================================================
# DEDUPLICATION DES METHODES
# =========================================================
def dedupliquer_methodes(methodes: list, classements: dict):
    tops = {
        m["nom"]: set(classements[m["nom"]][:PROFONDEUR_REDONDANCE])
        for m in methodes if m["nom"] in classements
    }

    actives, doublons = [], []
    for m in methodes:                      # deja triees par rang croissant
        nom = m["nom"]
        if nom not in tops:
            continue
        jumelle = None
        for garde in actives:
            recouvrement = (
                len(tops[nom] & tops[garde["nom"]]) / PROFONDEUR_REDONDANCE
            )
            if recouvrement >= SEUIL_REDONDANCE:
                jumelle = garde["nom"]
                break
        if jumelle:
            doublons.append((nom, jumelle))
        else:
            actives.append(m)
    return actives, doublons


# =========================================================
# GENERATION ANTI-DOUBLON (identique au dashboard)
# =========================================================
def _trop_proche(g: list[int], grilles_vues: set) -> bool:
    fg = frozenset(g)
    return any(len(fg & vue) >= 4 for vue in grilles_vues)


def _implausible(g: list[int], strict: bool = True) -> bool:
    if not FILTRE_PLAUSIBILITE:
        return False
    return not em_plausibilite.est_plausible(g, strict=strict)


def _quota_depasse(g: list[int], freq: Counter, plafond: float) -> bool:
    return any(freq.get(num, 0) >= plafond for num in g)


def generer_unique(classement, methode, grilles_vues,
                   freq: Counter = None, quota: int = None):
    nb_m = methode["nb_methode"]
    nb_a = methode["nb_aleatoires"]
    amp  = methode["amplitude"]
    top  = methode["top_n"]

    if nb_a == 0 or amp == 0:
        nb_m = min(nb_m, 4)
        nb_a = 5 - nb_m
        amp  = max(amp, 15)

    tentatives_params = [(nb_m, nb_a, amp)]
    for extra_amp in [10, 20, 30, 35]:
        tentatives_params.append((nb_m, nb_a, max(amp, extra_amp)))
    for nm in range(max(1, nb_m - 1), 0, -1):
        tentatives_params.append((nm, 5 - nm, max(amp, 15)))
    tentatives_params.append((1, 4, 35))

    for niveau in (0, 1, 2):
        if freq is None or quota is None or niveau == 2:
            plafond = None
        else:
            plafond = quota + 2 * niveau

        for nm, na, a in tentatives_params:
            for _ in range(40):
                g = generer_grille(classement, nm, na, a, top)
                if _trop_proche(g, grilles_vues):
                    continue
                if _implausible(g, strict=True):
                    continue
                if plafond is not None and _quota_depasse(g, freq, plafond):
                    continue
                return g, {"nb_methode": nm, "nb_aleatoires": na,
                           "amplitude": a, "quota_relache": niveau}

    for nm, na, a in tentatives_params:
        for _ in range(40):
            g = generer_grille(classement, nm, na, a, top)
            if _trop_proche(g, grilles_vues):
                continue
            if _implausible(g, strict=False):
                continue
            return g, {"nb_methode": nm, "nb_aleatoires": na,
                       "amplitude": a, "quota_relache": 2}

    for tentative in range(1, 501):
        g = sorted(random.sample(range(1, 51), 5))
        fin = (tentative >= 500)
        if fin or (not _trop_proche(g, grilles_vues)
                   and not _implausible(g, strict=True)):
            return g, {"nb_methode": 0, "nb_aleatoires": 5, "amplitude": 99,
                       "quota_relache": 2}


def _badge(params: dict, methode: dict) -> dict:
    """Meme regle d'affichage que _draw_card du dashboard."""
    nb_m_change = params["nb_methode"] != methode["nb_methode"]
    amp_change  = params["amplitude"] != methode["amplitude"]
    if params["nb_methode"] == 0:
        repli = "aleatoire"
    elif nb_m_change or amp_change:
        repli = "anti-doublon"
    else:
        repli = ""
    return {"repli": repli, "quota_relache": params.get("quota_relache", 0)}


# =========================================================
# SESSION COMPLETE (equivalent de App._generer)
# =========================================================
def generer_session(tirages: list, methodes: list, nb_grilles: int,
                    sessions: list) -> dict:
    """
    tirages  : listes de 5 boules, tirages[0] = le plus recent. Seuls les
               FENETRE premiers sont utilises.
    methodes : contenu de best_params.json.
    sessions : historique des sessions precedentes (format de
               historique_grilles.json).
    Renvoie les grilles, les messages de statut et l'historique mis a jour.
    """
    tirages = [list(t) for t in tirages[:FENETRE]]

    # --- 1) Classement de chaque methode -----------------------------
    classements, erreurs = {}, []
    for methode in methodes:
        try:
            fn = charger_fonction(methode["script"], methode["fonction"])
            classements[methode["nom"]] = fn(tirages)
        except Exception as e:
            erreurs.append({"methode": methode["nom"], "erreur": str(e)})

    if not classements:
        return {"grilles": [], "erreurs": erreurs, "sessions": sessions,
                "doublons": [], "nb_actives": 0, "quota": 0, "penalises": []}

    # --- 2) Elimination des methodes redondantes ---------------------
    actives, doublons = dedupliquer_methodes(methodes, classements)

    # --- 3) Quota de frequence + memoire des sessions passees --------
    quota = max(2, math.ceil(QUOTA_FACTEUR * nb_grilles * 5 / 50))
    freq  = charger_memoire(sessions)
    penalises = [n for n, v in freq.most_common(8) if v >= 1]

    # --- 4) Generation -----------------------------------------------
    grilles_vues = set()
    session, session_etoiles, cartes = [], [], []
    num = 0
    for methode, nb in distribuer(actives, nb_grilles):
        if nb == 0:
            continue
        classement = classements[methode["nom"]]
        for _ in range(nb):
            num += 1
            grille, params = generer_unique(
                classement, methode, grilles_vues, freq, quota
            )
            grilles_vues.add(frozenset(grille))
            freq.update(grille)          # le quota se consomme au fil de l'eau
            session.append(grille)
            etoiles = sorted(random.sample(range(1, 13), 2))
            session_etoiles.append(etoiles)
            diag = em_plausibilite.diagnostic(grille)
            cartes.append({
                "num": num,
                "methode": methode["nom"],
                "rang": methode["rang"],
                "grille": grille,
                "etoiles": etoiles,
                "badge": _badge(params, methode),
                "somme": diag[1],
                "etendue": diag[2],
            })

    return {
        "grilles": cartes,
        "erreurs": erreurs,
        "doublons": [list(d) for d in doublons],
        "nb_actives": len(actives),
        "nb_methodes": len(methodes),
        "quota": quota,
        "penalises": penalises,
        "filtre": {
            "max_par_dizaine": em_plausibilite.MAX_PAR_DIZAINE,
            "somme_min": em_plausibilite.SOMME_MIN,
            "somme_max": em_plausibilite.SOMME_MAX,
            "etendue_min": em_plausibilite.ETENDUE_MIN,
        },
        "sessions": ajouter_session(sessions, session, session_etoiles),
    }
