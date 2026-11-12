# Grilles Euromillions sur téléphone

Version mobile du dashboard `C:\Python\EM_Dashboard - V2.py`. La page fait tourner
les scripts Python du PC dans le navigateur (Pyodide) : rien n'a été réécrit.

## Contenu du dossier

| Fichier | Rôle |
|---|---|
| `index.html` | L'appli (interface + chargement du moteur) |
| `py/em_moteur.py` | La logique du dashboard, sans tkinter |
| `py/em_plausibilite.py`, `py/Stat_euromillion_*.py` | **Copies** des fichiers de `C:\Python` |
| `data/euromillions_202002.csv` | Tirages FDJ (mis à jour automatiquement une fois sur GitHub) |
| `data/best_params.json` | Résultat du dernier backtest lancé sur le PC |
| `data/historique_initial.json` | Sessions du PC au 09/11/2026, point de départ du quota |
| `scripts/maj_tirages.py` + `workflow-github/maj-tirages.yml` | Téléchargement automatique des tirages |
| `manifest.webmanifest`, `sw.js`, `icons/` | Installation sur l'écran d'accueil et mode hors ligne |

## Mise en ligne (gratuit, une seule fois)

1. Créer un compte sur github.com, puis un dépôt **public** nommé par exemple `grilles-em`.
   (GitHub Pages est gratuit uniquement pour un dépôt public : le code et les grilles
   de `historique_initial.json` seront visibles par qui connaît l'adresse.)
2. Envoyer **tout le contenu de ce dossier** dans le dépôt. Puis, dans le dépôt, créer le fichier
   `.github/workflows/maj-tirages.yml` (bouton *Add file → Create new file*, taper ce chemin complet)
   et y coller le contenu de `workflow-github/maj-tirages.yml`. Sans ce fichier à cet endroit précis,
   les tirages ne se mettent pas à jour.
3. Dans le dépôt : *Settings → Pages → Source : Deploy from a branch → main / (root)*.
4. Dans *Settings → Actions → General → Workflow permissions*, choisir *Read and write permissions*.
5. Dans l'onglet *Actions*, ouvrir « Mise a jour des tirages » et cliquer *Run workflow*
   pour vérifier que le téléchargement FDJ fonctionne.
6. Sur le téléphone, ouvrir `https://<votre-compte>.github.io/grilles-em/` dans Chrome,
   puis menu ⋮ → *Ajouter à l'écran d'accueil*.

## À ne pas faire

- **Ne pas modifier une méthode seulement dans `C:\Python`** : ce dossier en contient des
  copies. Après un correctif sur le PC, recopier le fichier dans `py/` et le renvoyer sur GitHub.
- **Ne pas ouvrir `index.html` par double-clic** : la page a besoin d'un serveur web
  (GitHub Pages, ou `python -m http.server` dans ce dossier pour un essai sur le PC).
- **Ne pas renommer `data/euromillions_202002.csv`** : la page et le script de mise à jour
  utilisent ce nom.
- **Ne pas changer `FENETRE` dans `em_moteur.py` sans changer `FENETRE_HISTORIQUE` du backtest.**

## Limites connues

- Le téléchargement automatique n'a pas pu être testé depuis GitHub : si FDJ bloque les
  serveurs de GitHub ou change son lien, l'étape 5 échouera et l'ancien CSV restera en place.
  Le lien se corrige en une ligne dans `scripts/maj_tirages.py` ; en attendant, la page permet
  de saisir un tirage à la main.
- Le backtest ne tourne pas sur le téléphone. Pour rafraîchir `best_params.json`, lancer
  `Lance-EM.cmd -BacktestSeul` sur le PC et recopier le fichier dans `data/`.
- L'historique des sessions du téléphone et celui du PC sont séparés. Le bouton
  « Copier l'historique » / « Importer » permet de passer de l'un à l'autre.
- Premier lancement : environ 10 Mo à télécharger (moteur Python), puis l'appli fonctionne hors ligne.
