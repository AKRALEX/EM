"""
maj_tirages.py - telecharge l'historique Euromillions depuis FDJ et met a jour
data/euromillions_202002.csv.

Lance automatiquement par GitHub Actions apres chaque tirage (voir
.github/workflows/maj-tirages.yml). Peut aussi etre lance a la main :

    python scripts/maj_tirages.py

Le fichier n'est remplace que s'il passe tous les controles ci-dessous. En cas
de doute (fichier vide, format change, tirage incoherent), le script s'arrete
en erreur et l'ancien CSV reste en place : l'appli continue de fonctionner
avec les donnees precedentes.
"""

import csv
import io
import sys
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path

# Lien "fevrier 2020 a aujourd'hui" de la page
# https://www.fdj.fr/jeux-de-tirage/euromillions-my-million/historique
# Si FDJ change ce lien, c'est la seule ligne a corriger.
URL_FDJ = ("https://www.sto.api.fdj.fr/anonymous/service-draw-info/v3/"
           "documentations/1a2b3c4d-9876-4562-b3fc-2c963f66afe6")

CIBLE = Path(__file__).resolve().parent.parent / "data" / "euromillions_202002.csv"
MIN_TIRAGES = 700          # le fichier en contenait 706 le 06/11/2026


def telecharger() -> bytes:
    requete = urllib.request.Request(URL_FDJ, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
        "Accept": "*/*",
    })
    with urllib.request.urlopen(requete, timeout=60) as reponse:
        return reponse.read()


def extraire_csv(archive: bytes) -> bytes:
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        noms = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(noms) != 1:
            raise ValueError(f"archive inattendue : {z.namelist()}")
        return z.read(noms[0])


def controler(contenu: bytes) -> tuple[int, str]:
    """Renvoie (nombre de tirages, date du plus recent). Leve ValueError sinon."""
    texte = contenu.decode("utf-8-sig")
    lignes = list(csv.DictReader(io.StringIO(texte), delimiter=";"))
    if len(lignes) < MIN_TIRAGES:
        raise ValueError(f"seulement {len(lignes)} tirages (attendu >= {MIN_TIRAGES})")

    dates = []
    for i, row in enumerate(lignes, start=2):
        try:
            boules = [int(row[f"boule_{k}"]) for k in range(1, 6)]
            etoiles = [int(row[f"etoile_{k}"]) for k in range(1, 3)]
            date = datetime.strptime(row["date_de_tirage"].strip(), "%d/%m/%Y")
        except Exception as e:
            raise ValueError(f"ligne {i} illisible : {e}")
        if len(set(boules)) != 5 or not all(1 <= b <= 50 for b in boules):
            raise ValueError(f"ligne {i} : boules invalides {boules}")
        if len(set(etoiles)) != 2 or not all(1 <= e <= 12 for e in etoiles):
            raise ValueError(f"ligne {i} : etoiles invalides {etoiles}")
        # Les boules doivent correspondre a la colonne "ordre croissant" :
        # c'est ce controle qui detecte une ligne modifiee par erreur.
        attendu = [int(x) for x in
                   row["boules_gagnantes_en_ordre_croissant"].strip("-").split("-")]
        if sorted(boules) != attendu:
            raise ValueError(f"ligne {i} ({row['date_de_tirage']}) : boules {sorted(boules)} "
                             f"differentes de l'ordre croissant {attendu}")
        dates.append(date)

    # L'appli suppose : premiere ligne = tirage le plus recent.
    if dates != sorted(dates, reverse=True):
        raise ValueError("le fichier n'est plus trie du plus recent au plus ancien")
    return len(lignes), dates[0].strftime("%d/%m/%Y")


def main() -> int:
    try:
        contenu = extraire_csv(telecharger())
        nb, plus_recent = controler(contenu)
    except Exception as e:
        print(f"ECHEC - CSV existant conserve : {e}")
        return 1

    if CIBLE.exists() and CIBLE.read_bytes() == contenu:
        print(f"Deja a jour : {nb} tirages, dernier le {plus_recent}.")
        return 0

    CIBLE.parent.mkdir(parents=True, exist_ok=True)
    CIBLE.write_bytes(contenu)
    print(f"Mis a jour : {nb} tirages, dernier le {plus_recent}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
