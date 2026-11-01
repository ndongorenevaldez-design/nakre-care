# NAKRE CARE — Plan d'implémentation Django complet sur Railway

Décision : **Railway héberge frontend Django Templates + backend Django + PostgreSQL ; Vercel ne sert que temporairement l'ancienne vitrine**. Pas d'achat de domaine imposé. Document du 1 novembre 2026.

## 1. Phases, livrables et validations

| Phase | Travaux | Critère de sortie |
| --- | --- | --- |
| 0. Documentation (cette PR) | Relire audit et fiche officielle ; actualiser architecture, cahier des charges, sécurité, plan et prompt Codex. | Une PR documentaire ; aucune modification de `main` ou du déploiement. |
| 1. Préparation Django | Branche applicative dédiée ; configuration Django, apps, templates du site existant, statiques, dépendances verrouillées, tests de base et environnement local. | Accueil et recrutement reproduits fidèlement ; aucun changement de site Vercel. |
| 2. Base métier | PostgreSQL local/test, modèles versionnés, migrations, contraintes, jeux de données fictifs et droits. | Tests de modèles, transactions, migrations et droits réussis. |
| 3. Authentification | Invitations, comptes séparés, MFA obligatoire y compris Django Admin, récupération, sessions et rôles. | Tests négatifs et désactivation/révocation validés. |
| 4. Fiche officielle | Sections publiques 1–7, section 8 privée, Django Forms, GPS facultatif, confidentialité, validation et confirmation fiable. | Tests sans JS, mobile, champs, CSRF, échecs réseau, zéro fuite en URL/WhatsApp. |
| 5. Opérations | Tableau de bord, filtres, statuts, conversion de demande en patient, contacts autorisés, suivi des interventions, audit. | Permissions par dossier et concurrence contrôlées. |
| 6. Notifications | E-mail et WhatsApp Business Platform si autorisée et abordable ; outbox/worker selon besoin ; échecs et retries. | Tests avec boîte de capture et destinataires internes, sans dossier réel. |
| 7. Railway de test | Service Django + PostgreSQL privé, URL `*.up.railway.app` générée, variables d'env, collectstatic, migrations contrôlées, healthcheck, logs minimisés. | Application entière accessible en test sur Railway, restauration démontrée. |
| 8. Validation finale | Recette design/mobile, sécurité, conformité camerounaise, disponibilité, coût, monitoring et procédure de retour arrière. | Accord explicite avant toute collecte réelle. |
| 9. Bascule | Publier le site Django Railway, communiquer la nouvelle URL, surveiller et corriger les liens ; désactiver Vercel **seulement après accord distinct** et plan de redirection/communication. | Railway seul héberge finalement toute la plateforme ; GitHub reste source. |

Un push sur une branche peut déclencher une preview Vercel suivant l'intégration : vérifier les paramètres et isoler les nouvelles fonctionnalités/données avant tout push ; ne jamais brancher la production de test à des dossiers patients réels.

## 2. Migration progressive, sans rupture

- **Origine :** `https://nakre-care.vercel.app/` ne change pas pendant la construction. Son domaine ne peut pas être transféré à Railway.
- **Cible provisoire :** domaine de service Railway `*.up.railway.app`, généré dans Railway, pas de nom fixé à l'avance ni achat de domaine.
- **Cible finale tant qu'il n'y a pas de budget domaine :** la même URL Railway devient officielle une fois validée.
- **Option future :** domaine personnel acheté seulement lorsque les moyens le permettront.
- **Retrait Vercel :** fermeture non automatique ; analyser la perte possible de liens/indexation sur l'adresse `.vercel.app`, préparer communication et redirections si réalisables avant suppression.

## 3. Structure cible proposée

```text
config/                 # settings, urls, wsgi/asgi
apps/
  website/              # vitrine et recrutement
  intake/               # formulaire de renseignements
  accounts/             # comptes, MFA et rôles
  patients/             # dossiers
  interventions/        # prestations
  notifications/        # messages et reprises
  audit/                # journal
templates/              # Django Templates
static/                 # logo, photos, CSS, JS existants
tests/                  # tests de sécurité et E2E
manage.py
pyproject.toml           # versionnage des dépendances
```

Décider tôt du modèle User, du mécanisme MFA et de la séparation des permissions. Pas de migration aveugle de la structure HTML ; conserver et réutiliser les médias locaux et SEO. Les références visuelles papier fournies dans le chat devront être transférées légalement dans le contexte Codex avant recette visuelle ; l'image n'est pas automatiquement dans GitHub.

## 4. Coûts et conditions d'ouverture

Le nom de service Railway fourni (`*.up.railway.app`) évite **l'achat d'un domaine** ; il n'annule pas le coût du calcul du service web ni de PostgreSQL. Les plans Railway sont basés sur l'utilisation/crédits ; vérifier solde, éligibilité et capacité réelle du compte. À confirmer dans le tableau de bord : ressources mémoire, stockage DB, backups, jobs, limites et politique de facturation. Ajouter e-mail, WhatsApp API et monitoring le cas échéant. Aucun abonnement ni création de projet n'est inclus dans cette mission documentaire.

Ne pas activer la collecte de données médicales si : hébergement non pérenne, stockage/restauration non prouvés, permissions/MFA incomplets, formalités légales non satisfaites ou journaux non sécurisés. Conserver l'ancienne vitrine sans collecte jusqu'à résolution.

## 5. Tests prioritaires

Django `check --deploy`, tests de validation serveur, CSRF, accès au Django Admin sans second facteur, tests multi-admin et affectations, anti-bruteforce, XSS, données dans URL, localisation refusée, droits de tiers, double validation concurrente, migration réversible/corrective, sauvegarde/restauration isolée, mobile 320–1440 px et navigation clavier. Vérifier que l'URL Railway sert **la vitrine ET l'administration**, et non seulement une API.

## 6. Portes d'approbation

Cette PR : uniquement documentation. Toute création de projet Railway, variables sensibles, facture, mise en production ou migration du site existant exige une phase ultérieure explicitement acceptée. Ne jamais fusionner automatiquement sur `main`.

Documents : [Architecture](ARCHITECTURE_CIBLE.md), [Cahier des charges](CAHIER_DES_CHARGES.md), [Sécurité](SECURITE_ET_DONNEES.md).
