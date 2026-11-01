# NAKRE CARE — Cahier des charges fonctionnel Django

Version du 1 novembre 2026. Se référer à [l'architecture cible](ARCHITECTURE_CIBLE.md). Le produit final sera un **site et une application Django uniques sur Railway**. Vercel est conservé seulement pendant la transition.

## 1. Périmètre

La nouvelle application sert toutes les pages : accueil, services, approche NAKRE CARE, FAQ, recrutement, contact, fiche officielle de renseignements, espace administrateur et suivi des prestations. Les visiteurs **ne créent pas de compte**. Plusieurs administrateurs disposent de comptes individuels, d'un mot de passe, d'une authentification multifacteur et de permissions différenciées.

Exclus : factures en ligne, paiements, espace personnel des familles, pièces jointes, dossiers médicaux hospitaliers, téléversements de photos. Les factures restent sur papier.

Conserver le logo NAKRE CARE authentique, les fichiers visuels déjà présents, le texte confirmé et les tokens CSS du site. Ne pas remplacer l'identité de marque ni réaliser un design générique. Contrôler l'image source « FICHE DE RENSEIGNEMENTS CLIENT » fournie par le propriétaire : **ne pas improviser ses libellés ou sa structure**. Cette image doit être disponible pour Codex avant la recette visuelle ; si elle n'est pas dans le dépôt, demander un transfert autorisé de l'asset, sans bloquer la documentation technique.

## 2. Fiche publique officielle

URL cible sur la **même origine Railway** : `/prise-en-charge/`, et non un formulaire WhatsApp. Mise en page 2 colonnes pour grand écran, une seule sur smartphone, bandeaux de rubrique et typographies respectant la charte. Gérer contrôles accessibles (clavier, zoom, messages d'erreur, focus) et connexions mobiles lentes.

| Section image officielle | Contenu / traitement |
| --- | --- |
| 1. Demandeur | Nom/prénom, lien avec le patient, téléphone, WhatsApp, adresse/quartier, ville ; e-mail facultatif. |
| 2. Personne à accompagner | Nom, sexe si nécessaire, âge, lieu de résidence, situation à domicile / hospitalisée / convalescence / autre, autonomie, mobilité, aide pour alimentation et toilettes. |
| 3. État de santé / situation | Difficultés ou problème principal, handicap particulier, médicaments ou traitements pertinents uniquement si justifiés, besoin spécifique, urgence déclarée ; ne pas transformer en diagnostic ni exiger d'informations superflues. |
| 4. Accompagnement recherché | Présence domicile/hôpital, hygiène, mobilité, garde jour/nuit, ponctuel/régulier, surveillance ou présence rassurante, autre. |
| 5. Période | Date de début souhaitée, ponctuel/temporaire/régulier, horaires, jour/nuit, fréquence. |
| 6. Contact | Nom, lien, téléphone principal et secondaire d'une personne à joindre ; autorisation de contact à vérifier. |
| 7. Observations | Informations nécessaires, texte court borné ; avertir d'éviter les détails médicaux inutiles. |
| 8. Validation/suivi interne | **Jamais dans l'interface familiale :** réception, évaluation, date, orientation, suite à donner, statut et historique réservés à l'administration. |

Ajouter une adresse du lieu **d'intervention** distincte du domicile du demandeur ou de la position actuelle du navigateur. GPS facultatif : bouton explicite, permission, possibilité de retirer ou corriger la position, saisie manuelle toujours utilisable ; pas de suivi permanent, de carte tierce ni de géolocalisation à l'ouverture.

Séparer information, base juridique/consentements applicables, qualité du répondant, contact d'urgence, et permission GPS. La signature d'un demandeur ne suffit pas automatiquement à autoriser le traitement de la santé d'un tiers. Ne lancer la collecte de santé réelle qu'après validation juridique camerounaise.

Soumission **POST Django** avec CSRF, validation serveur, anti-spam, limite de taille, idempotence et transaction, puis confirmation fiable avec référence unique non utilisable pour lire le dossier. Pas de GET, d'URL ou de messages WhatsApp portant les réponses. Pas de stockage persistant de brouillon dans localStorage. Si l'enregistrement échoue, afficher une erreur honnête et ne pas annoncer de succès.

## 3. Administration

Accès par invitation uniquement, comptes individuels, sessions sécurisées et MFA obligatoire sur les vues métier **et Django Admin**. Superadministrateur (comptes et droits), administrateurs (demandes et dossiers selon affectation) et coordinateur optionnel. Vérification effective côté serveur ; audit des changements de statut et actions sensibles.

Parcours : demande nouvelle → en évaluation → acceptée ou refusée/annulée → dossier activé et prestations suivies → clôture. L'acceptation crée au plus un dossier par demande, avec transaction/contrôle de concurrence. Permettre consultation, recherche, filtres, contact famille via lien WhatsApp **sans détail de santé prérempli**, planification et comptes rendus factuels minimaux. Statuts d'intervention : prévue, effectuée, annulée.

Modèles proposés : CareRequest, ConsentRecord, PatientCase, AuthorizedContact, CarePlan, Intervention, AdminRole/CaseAssignment, AuditEvent, NotificationOutbox. Prévoir des droits d'accès aux dossiers par rôle et affectation, des protections contre l'accès direct par identifiant, pagination et restrictions sur les exports. Aucun dossier consultable par une URL publique.

## 4. Notifications et contact

Numéro WhatsApp : **+237674134365** ; e-mail transitoire **ndongorenevaldez@gmail.com**, configurable sans changer les templates. Le lien WhatsApp de la vitrine sert au contact générique ; l'envoi automatique d'alertes administratives dépend d'une intégration WhatsApp Business Platform autorisée, à budgéter. Prévoir e-mail transactionnel. Notifications sobres : « Nouvelle demande NAKRE CARE — connectez-vous à l'administration », sans nom, diagnostic, adresse, GPS ou détails de prise en charge.

Prévoir stockage fiable des événements, retries contrôlés, traces minimales et affichage réel du statut de distribution ; un lien wa.me n'est pas une notification envoyée.

## 5. Critères d'acceptation

- Les pages existantes sont reproduites sans perte de contenus ni de cohérence graphique, sur mobile et desktop.
- Les sept sections publiques reflètent la fiche papier ; la huitième est inaccessible au public.
- Aucune donnée sensible ne figure dans URL, WhatsApp, logs, analytics, notifications ou pages mises en cache.
- Sans compte public, le demandeur reçoit une référence après persistance confirmée ; un visiteur ne peut lire aucune demande.
- Les administrateurs ne peuvent agir qu'avec session, MFA et permission serveur ; les comptes désactivés sont révoqués.
- L'application Django complète fonctionne sur un domaine Railway `*.up.railway.app` réellement généré, sans domaine payant.
- Vercel continue de servir l'ancien site pendant les travaux ; retrait soumis à validation explicite après contrôle et plan de communication.
- Données de test fictives uniquement jusqu'aux validations sécurité, conformité et exploitation.

## 6. Hors périmètre de cette branche

Documentation uniquement : aucune application Django, base Railway, clé, facture, compte, déploiement ni formulaire patient réel n'est créé ici.
