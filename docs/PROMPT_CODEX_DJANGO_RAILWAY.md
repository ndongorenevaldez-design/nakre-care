# PROMPT CODEX CLOUD — NAKRE CARE : DJANGO COMPLET SUR RAILWAY

Tu es un ingénieur logiciel senior spécialiste de Python/Django, PostgreSQL, Railway, sécurité des données de santé et UX/UI.

## Contexte et sources

Dépôt : `ndongorenevaldez-design/nakre-care`.
Site existant à conserver pendant la transition : https://nakre-care.vercel.app/
Branche documentaire source : `docs/audit-architecture-nakre-care`.
Lire les quatre documents mis à jour sur `docs/django-railway-fullstack-20261101` : `docs/ARCHITECTURE_CIBLE.md`, `docs/CAHIER_DES_CHARGES.md`, `docs/SECURITE_ET_DONNEES.md`, `docs/PLAN_IMPLEMENTATION.md`.

NAKRE CARE propose l'assistance et l'accompagnement professionnel des personnes âgées, malades, dépendantes ou en perte d'autonomie à Yaoundé, Cameroun.

## Architecture définitive — non négociable

Le site complet, **frontend ET backend**, doit être migré vers **une application Django monolithique** (Django Templates, Django Forms, Django Auth, PostgreSQL), déployée **entièrement sur Railway** : pages publiques, formulaire patient, administration, dossiers et suivi des prestations. Railway doit héberger aussi PostgreSQL, accessible en privé ; worker séparé seulement si nécessaire.

**Vercel n'est pas une composante définitive de l'architecture.** Conserver le site statique existant sur Vercel tant que Django/Railway n'est pas validé. Ne pas modifier ou supprimer le déploiement Vercel ni fusionner dans `main` sans consentement explicite. Après validation fonctionnelle, sécurité, juridique, budget et stabilité, préparer une bascule maîtrisée puis un retrait ultérieur de Vercel sur instruction séparée.

**Pas d'achat de domaine** : utiliser dans l'immédiat une adresse Railway `*.up.railway.app` fournie par la plateforme. Elle doit être générée dans Railway (ne jamais inventer l'adresse réelle). HTTPs et configuration ALLOWED_HOSTS/CSRF/proxy correctement appliqués. Distinguer absence de coût d'achat d'un domaine et **coût d'exécution** de Django/PostgreSQL selon les crédits Railway. Ne rien promettre de gratuit ni activer des services payants sans décision.

Ne pas retenir l'ancienne proposition Vercel Functions + Supabase ni un frontend Vercel couplé durablement à Django Railway. Ne pas ajouter React/Vue/SPA sans besoin justifié.

## Formulaire officiel : référence visuelle et fonctionnelle

Le propriétaire a fourni une image « FICHE DE RENSEIGNEMENTS CLIENT » aux couleurs NAKRE CARE. Vérifier qu'elle est accessible dans l'environnement de Codex ; si elle ne l'est pas, signaler explicitement que la **validation pixel/visuelle est bloquée** jusqu'au transfert de l'image. Ne pas prétendre avoir vu la référence si elle manque.

Reproduire en Django Forms et templates, avec deux colonnes desktop et une sur mobile, le logo, la palette officielle, les sept sections destinées aux familles :
1. Informations sur le demandeur (identité, lien, téléphone, WhatsApp, quartier, ville).
2. Informations sur la personne à accompagner (identité, âge, situation, autonomie, mobilité, alimentation, toilettes).
3. État de santé / situation (seulement informations indispensables, besoins, urgence).
4. Type d'accompagnement (domicile, hôpital, hygiène, mobilité, garde de jour/nuit, présence, ponctuel/régulier, autre).
5. Période et disponibilité (date souhaitée, horaires, fréquence, jour/nuit).
6. Personne à contacter en cas de besoin.
7. Observations complémentaires, bornées.

La **section 8 : Validation / suivi interne** est strictement réservée aux administrateurs et non visible dans le formulaire public.

Ajouter adresse d'intervention distincte du domicile du demandeur, GPS **facultatif**, sur action volontaire avec permission et alternative manuelle, ainsi qu'information/consentement adaptés. Pas de pièce jointe. Champs de santé minimisés et nécessité juridique évaluée avant collecte réelle.

Le formulaire est **un formulaire Django** : POST CSRF, validation serveur, anti-abus, idempotence, transaction PostgreSQL, référence unique et confirmation après sauvegarde. Il **ne doit jamais ouvrir WhatsApp pour soumettre les réponses**, ni inclure les réponses dans une URL, un e-mail d'alerte ou un message WhatsApp. Aucun compte demandé aux familles, aucun stockage sensible dans localStorage.

## Interface d'administration

Plusieurs comptes administrateurs individuels, par invitation, mot de passe et MFA obligatoire. Vérifier le MFA **sur toutes les routes métier et Django Admin** ; Django Admin natif seul ne constitue pas du MFA. Permissions serveur par rôle et si nécessaire dossier/affectation ; révocation, historique et audit.

Fonctions : liste/tri/recherche des demandes, statuts, évaluation, acceptation/refus, conversion transactionnelle en dossier patient, contacts autorisés, planning et suivi factuel des prestations, journal d'événements. Pas de facturation numérique, pas d'espace client, pas de documents médicaux joints.

## Contact et notifications

WhatsApp professionnel : +237674134365. E-mail provisoire : ndongorenevaldez@gmail.com, modifiable par configuration.

Conserver le bouton de contact WhatsApp public. Les notifications internes par e-mail et éventuellement WhatsApp Business Platform sont **distinctes** du formulaire : informer seulement qu'une nouvelle demande a été reçue et inviter les administrateurs à se connecter, sans nom, diagnostic, GPS, adresse ou autre donnée sensible. Journaliser échec, tentatives et état réel. Ne pas confondre lien wa.me et envoi automatisé ; différer les services payants ou non configurés.

## Conservation du site actuel

Auditer `index.html`, `recrutement/index.html`, `assets/styles.css`, `assets/site.js`, logo, images, métadonnées et responsive. Réutiliser les assets et la charte NAKRE CARE, les textes métier confirmés et URLs utiles dans les templates Django, sans interface générique.

Corriger notamment le risque historique du formulaire existant : en absence de JavaScript, une soumission GET peut placer des informations dans l'URL. Aucun texte de santé dans un formulaire de contact générique. Ne rien modifier sur Vercel pendant la préparation.

## Sécurité, conformité et exploitation

Loi camerounaise n° 2024/017 : traiter données de santé / géolocalisation comme sensibles, documenter bases juridiques, autorité du répondant, finalités, consentement ou autres fondements appropriés, régions Railway, transferts, sous-traitants, conservation, droits et formalités. Validation avec conseil compétent avant collecte réelle.

Django : DEBUG=False, secrets hors Git, HTTPS, cookies Secure/HttpOnly/SameSite, CSRF, XSS, validation serveur, rate-limits persistants, permissions testées, journaux minimisés, sauvegardes PostgreSQL et restauration réellement testée. Générer domaine Railway, servir port Railway, collectstatic, migrations contrôlées, healthcheck, monitoring, budget/alertes et procédure de rollback. Tests fictifs uniquement avant validation.

## Méthode et livrables immédiats

1. Examiner l'état exact des branches et de la documentation, sans écraser des travaux concurrents.
2. Utiliser les quatre documents déjà révisés comme base ; relever les contradictions résiduelles.
3. Présenter une proposition technique détaillée de migration Django/Railway, y compris modèle de données, structure apps, sécurisation MFA, test et coûts.
4. Vérifier la disponibilité de la fiche officielle dans le workspace, sinon marquer sa validation graphique en attente.
5. Créer une branche applicative distincte **seulement après validation** de l'architecture ; découper le code en petites Pull Requests, avec tests et preuves de sécurité.
6. Ne pas fusionner automatiquement `main`, ne pas déployer en production, ne pas supprimer Vercel, ne pas activer de collecte de données réelles et ne pas souscrire à un service payant sans accord.

**Objectif final : une seule application Django sur Railway, publique et privée, fidèle à NAKRE CARE, avec une fiche officielle de renseignements et un suivi patient confidentiel.**