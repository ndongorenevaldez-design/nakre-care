# Plan d’implémentation et dossier de validation

1 novembre 2026. La présente PR est exclusivement documentaire. Aucun code fonctionnel, base, compte, secret, abonnement ou déploiement n’est créé. Aucune donnée réelle de patient utilisée. La branche principale n’est pas modifiée.

Documents : [architecture et audit](ARCHITECTURE_CIBLE.md), [spécifications](CAHIER_DES_CHARGES.md), [sécurité et données](SECURITE_ET_DONNEES.md).

## 1. Évidence de l’audit

Base auditée : `ba669260a8d21fc84c313f48d42fe58f8e159a8a`, vérifiée identique à `main` distant via Git. Inspection du HTML, JavaScript, CSS, documentation et SEO, inventaire des médias et dimensions/types, vérification de l’absence de scripts dans les SVG. Dépôt initial propre ; absence de dépendances et configuration serveur suivies. Aucun framework requis pour le workflow actuel.

| Contrôle | Résultat / limite |
| --- | --- |
| Syntaxe `node --check assets/site.js` | Réussi. |
| Serveur statique local Python + HTTP | Deux pages accessibles ; 49 occurrences de ressources/liens internes contrôlées HTTP 200 lors de la préparation de cet environnement. Aucun endpoint de production testé. |
| Chromium/Playwright, contrôle de préparation | Accueil et recrutement à 375 et 1440 px ; images chargées après attente lazy, un H1, pas de débordement global ; menu/Escape et validation des champs obligatoires passent, URL WhatsApp interceptée sans envoi. Zéro erreur JavaScript observée. |
| Réaudit de cette mission | Réussi sur les deux pages à 320, 375, 768, 980, 1024, 1440 px : HTTP 200, un H1 et aucun débordement global. Menu/Escape, champs requis, génération WhatsApp interceptée et absence d’erreur JS confirmés. Les mesures de largeur globale ne certifient pas l’absence de contenu rogné ni WCAG. |
| Téléphone | Lecture du code et contrôle navigateur : type tel sans pattern/validation métier. |
| Repli sans JS | Confirmé dans Chromium sans JS : champs fictifs soumis dans la query string GET. Un premier essai a expiré sur le contrôle de stabilité du bouton ; nouvel essai sans animations réussi. |
| Git distant | Lecture de main réussie ; aucun push main. |
| Site public et API GitHub | Refus du proxy réseau (403). Headers de production, intégration Vercel, droits API et paramètres de déploiement non vérifiés. |
| Conformité, sécurité backend, notifications | Non exécutables à ce stade : backend absent, textes officiels/contrats et fournisseurs non vérifiés. Pas de fausse réussite. |

L’ancien AUDIT.md reste inchangé comme document historique. Aucun test additionnel de développement ne sera ajouté dans cette tâche documentaire. Les scénarios ci-dessous sont des exigences futures, pas des résultats déjà obtenus.

## 2. Séquence et portes de validation

| Étape | Livrables / modification minimale | Validation de sortie |
| --- | --- | --- |
| 0 — cette mission | Audit, cible, exigences, risques, coûts et plan sur branche documentaire | Validation explicite de la direction technique ; aucune fonctionnalité commencée. |
| 1 — décisions et juridique | Relevé Vercel réel, régions/flux/sous-traitants, avis loi 2024/017, politique de données, budget, responsables, fournisseur notification et conditions WhatsApp | Décisions écrites et formalités identifiées ; pas de collecte sensible. |
| 2 — socle de test isolé | Projet Supabase de développement synthétique, migrations versionnées, runtime serveur minimal/lockfile, API validation/erreurs, secrets hors Git, environnement preview protégé | Build/runtime vérifiés, aucune liaison production, tests SQL RLS et secrets/bundles. |
| 3 — accès administratif | Invitations, superadmin initial hors API publique, sessions, MFA, permissions et révocation, journal d’audit | Tests négatifs AAL1/anon/rôle/périmètre/compte désactivé ; récupération MFA contrôlée. |
| 4 — demande publique | Page HTML dédiée et notice, endpoint POST restreint, anti-abus durable, consentement, GPS facultatif, référence et idempotence | Recette avec données fictives, refus GPS et panne réseau, pas de GET sensible, aucun accès public aux demandes. Collecte réelle toujours désactivée. |
| 5 — opérations métier | Liste/filtres, transitions, conversion transactionnelle, contacts autorisés, timeline et affectations | Tests concurrence/conversion/droits et audit, aucune fusion silencieuse de personnes. |
| 6 — notifications | Outbox, ordonnanceur, adaptateurs officiels e-mail/WhatsApp, webhooks, tentatives et alertes | Boîte de capture en test, échecs et retries vérifiés ; test réel uniquement avec destinataires internes autorisés et sans données de patient. |
| 7 — préproduction et exploitation | Tests E2E/sécurité, accessibilité, restauration, purge, monitoring, procédures et formation | Avis juridique/technique clos, restauration prouvée, absence de secrets et données sensibles dans logs/notifications/URLs, revue indépendante. |
| 8 — activation contrôlée | Plan de migration, collecte activable explicitement côté serveur, mise en production autorisée | Accord du responsable NAKRE CARE et validation de déploiement distincte ; contrôles post-déploiement, surveillance et retour arrière. |

Ordre adaptable entre écrans sur socle synthétique ; les portes juridique/sécurité ne sont pas contournables. Toute PR ultérieure reste petite et vérifiable. Pas de reconstruction, changement d’identité ou framework implicite.

## 3. Plan de fichiers futur (indicatif, rien à créer maintenant)

- Conserver `index.html`, `recrutement/`, ressources officielles, robots et sitemap ; changements ciblés de liens/formulaire/menus seulement après accord.
- Ajouter `demande/`, `confidentialite/`, `admin/` avec scripts distincts. Éviter d’inclure auth, SDK admin ou données de dossiers dans la vitrine.
- Ajouter `api/` pour ingestion/auth/API privée/webhooks, bibliothèques serveur partagées et dépendances verrouillées. Choisir Node supporté par Vercel et préciser sa version.
- Ajouter migrations SQL et tests RLS dans un répertoire Supabase ; fixture uniquement synthétique. Pas de clés dans les migrations ni de signup public.
- Ajouter tests d’intégration/E2E et configuration CI après choix du runner ; paramétrage Vercel précis après lecture du projet réel. Aucun catch-all SPA écrasant les pages existantes.

## 4. Validation future par couche

DB : contraintes, transitions, transaction de conversion, migrations sur base vide et mise à niveau, rollback/forward recovery, matrice RLS par rôle et identité, appel direct REST/RPC hostile. API : validation sans navigateur, CSRF, contrôle JWT/MFA, injection, taille, quota distribué, idempotence, erreurs et indisponibilité DB. Interface : clavier, lecteur d’écran, focus, contraste, zoom 200/400 %, 320–1440 px, paysage, GPS refusé/timeout, absence JS et réseau lent. Notifications : timeout après acceptation fournisseur, retry/doublon, webhook falsifié/rejoué, échec définitif, historique honnête. Exploitation : restauration, suppression rejouée, révocation immédiate, incident, budget et alarmes.

Scénarios sensibles toujours en environnement synthétique distinct. Aucun scanner agressif du site public ni envoi WhatsApp réel inclus dans l’audit actuel. Aucun résultat futur ne doit être affiché comme un test passé.

## 5. Déploiement et retour arrière proposés

Avant push de code futur, vérifier l’automatisation Vercel : une branche peut générer une preview. Garder main protégée et interdire déploiement production sans accord. Préviews privées, données factices, collecte réelle et notifications externes désactivées. La PR documentaire ne change aucun fichier applicatif ou configuration de déploiement.

Migration additive compatible avec ancienne version, sauvegarde et test de restauration avant déploiement. Procédure d’arrêt de collecte côté serveur, désactivation du worker sans perdre l’outbox et retour au parcours de contact générique si nécessaire. Ne pas revenir à une ancienne version exposant des données, ni supprimer des demandes pour simplifier un rollback. Conserver les jobs et migrations avec piste d’audit.

## 6. Charge et coûts

Cadrage indicatif : 4–7 semaines de travail pour une personne expérimentée sur socle, parcours et sécurisation, plus revue indépendante, formation et délais externes juridiques/Meta ; pas un engagement de calendrier. Les décisions et validations peuvent prolonger cette durée. Prioriser sécurité/RLS avant enrichissement de l’interface.

Budget récurrent indicatif détaillé dans l’architecture : 80–360+ USD/mois selon fournisseurs/plans/usage, hors conseil, maintenance et dépassements. Pas de dépense engagée. Exiger devis réels, conditions commerciales, métriques de volume et alertes de coût avant activation.

## 7. Décisions à prendre avant développement

1. Accepter ou ajuster le maintien du frontend statique et l’ajout Vercel Functions/Supabase, conditionné aux régions et formalités légales.
2. Valider dictionnaire minimal, rôles/périmètres, cycle métier, contacts autorisés et durées de conservation.
3. Nommer les responsables juridique et technique ; obtenir texte officiel et analyse des transferts/santé.
4. Qualifier les comptes Vercel/Supabase et le numéro Business WhatsApp, sélectionner prestataires et budget.
5. Valider cibles de reprise, procédure de sauvegarde/restauration et critères d’ouverture à des demandes réelles.

L’autorisation de créer cette PR de documentation n’est pas une validation de ces choix ni un accord de développement ou de production.
