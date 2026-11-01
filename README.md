# NAKRE Care — site vitrine

Refonte UX/UI du site vitrine existant, en conservant l’architecture statique HTML/CSS/JS et le fonctionnement WhatsApp.

## Architecture

- `index.html` — homepage
- `recrutement/index.html` — parcours de recrutement séparé
- `assets/styles.css` — design system et responsive
- `assets/site.js` — menu mobile, bouton WhatsApp flottant et formulaire WhatsApp
- `robots.txt` / `sitemap.xml` — SEO

## Déploiement Vercel

Aucun build n’est nécessaire. Déployer le dossier `nakre-care-site` tel quel.

## Points conservés

- Numéro : +237 674 134 365
- WhatsApp
- Facebook : NAKRE CARE
- Zone : Yaoundé, Cameroun
- Services confirmés : domicile, milieu hospitalier, rendez-vous/déplacements utiles
- Processus : prise de contact, évaluation, organisation, suivi

## Développement Django — Lot 1

Le socle Django réutilise les médias et styles du site statique. Les fichiers HTML
historiques restent la référence de comparaison ; ils ne sont pas utilisés par Django.

```sh
uv sync --frozen
python scripts/dev.py init
python scripts/dev.py up
python scripts/dev.py manage migrate --noinput
python scripts/dev.py manage test
python scripts/dev.py manage runserver 127.0.0.1:8000 --noreload
```

Python 3.12, uv et Docker Compose sont requis. Aucun compte administrateur n’est créé.
Consulter [les instructions complètes et le bilan du Lot 1](docs/LOT1_EXECUTION.md).
Les routes privées et la collecte médicale sont désactivées ; aucun déploiement Railway.
