# NAKRE CARE — Sécurité et données sensibles (Django / Railway)

Version de cadrage du 1 novembre 2026. Ce plan **ne constitue ni preuve de conformité ni sécurité déjà implémentée**. Voir [architecture](ARCHITECTURE_CIBLE.md) et [cahier des charges](CAHIER_DES_CHARGES.md).

## 1. Responsabilités et hébergement

Railway fournit l'infrastructure de déploiement Django et PostgreSQL privé ; NAKRE CARE reste responsable des accès, paramètres Django, droits métier, sauvegardes et restauration, conservation, incidents et obligations légales. Domaine de service `*.up.railway.app` fourni sans achat de domaine, mais service web et base consomment des ressources facturables selon le plan/crédit ; aucune disponibilité 24/7 gratuite n'est présumée.

Les données de santé potentielles, la dépendance et la géolocalisation requièrent minimisation et analyse des risques renforcée. Vérifier juridiquement la loi camerounaise **n° 2024/017 du 23 décembre 2024**, ses formalités, transferts éventuels hors Cameroun, sous-traitants, consentement/autorité du déclarant et droits du patient avant d'activer le formulaire en production. Ne pas présenter un simple checkbox comme justification juridique universelle. Valider régions Railway et éventuels services tiers (e-mail, WhatsApp, anti-spam, monitoring) avec un professionnel local compétent.

## 2. Contrôles Django indispensables

- Django maintenu à jour (branche LTS compatible), `DEBUG=False`, `SECRET_KEY` hors Git, `ALLOWED_HOSTS` strict pour le domaine Railway réellement attribué ; `CSRF_TRUSTED_ORIGINS` seulement pour origines nécessaires.
- HTTPS effectivement actif, cookies de session et CSRF correctement sécurisés, `HttpOnly` pour session, SameSite, HSTS après qualification, politique proxy et en-têtes vérifiés derrière Railway.
- CSRF pour les formulaires authentifiés et anonymes, protection XSS via échappement des templates, pas de `mark_safe` pour texte libre ; SQL via ORM/paramètres.
- Protection de force brute / verrouillage contrôlé, limitation de débit distribuée pour envoi et connexion, validation serveur exhaustive, cap de taille, anti-bot proportionné et vérifié serveur.
- Comptes administrateurs **nominatifs sur invitation**, sans signup public, mot de passe robuste + MFA. L'accès Django Admin natif ne prouve pas le MFA : intégrer et tester explicitement le second facteur sur toutes les routes administratives ; prévoir récupération sécurisée et révocation immédiate.
- Autorisation par rôle **et** par dossier/affectation côté serveur, y compris liste, détails, transitions et exports. Les noms de route et menus masqués ne sont pas une protection.
- Éviter de mettre données sensibles dans la session, URL, cache, notifications, logs, systèmes d'erreurs ou historiques JS. Réponses privées avec Cache-Control no-store et protections contre indexation, sans confondre noindex et contrôle d'accès.
- Séparer production et développement/test avec données synthétiques ; secrets par environnement, rotation et revues de dépendances ; CI pour tests de permissions et scans de secrets.

## 3. Fiche publique et GPS

POST Django uniquement, jeton CSRF, protection anti-automatisation, idempotence, transaction, validation des longueurs/types/échelles et messages d'erreur minimaux. Aucun GET contenant une réponse de santé. Aucun téléversement de document. La géolocalisation n'est sollicitée qu'après un geste explicite : consentement navigateur, possibilité de refuser et de supprimer ; confirmer qu'il s'agit du lieu **d'intervention**, qui peut différer de la position actuelle du demandeur.

Une personne remplissant la fiche pour un proche doit indiquer son lien et la légitimité de la transmission ; vérifier la capacité/autorité et les modalités de contact avant partage. Ne pas collecter automatiquement davantage de données que nécessaire au triage.

## 4. Conception des données

CareRequest → PatientCase uniquement après acceptation ; contacts réellement autorisés distingués des contacts proposés. Traces des consentements et notices versionnées. Transactions et contraintes d'unicité contre conversion en double. Historique d'intervention factuel avec corrections tracées. Références publiques non prédictibles et jamais utilisées seules pour authentifier un lecteur.

Journal d'audit minimal : auteur, action, ID interne, horodatage, résultat ; aucune copie du nom, diagnostic, téléphone, GPS, note libre. Notifications : destinataires habilités et texte générique seulement ; secret des webhooks, vérification signature et anti-rejeu selon fournisseur.

## 5. Conservation, sauvegardes, incidents

Établir avec conseil compétent un registre des traitements : finalité, base juridique, responsables, droits d'accès, destinataires, régions, sous-traitants, durée de conservation, effacement et transferts. Hypothèses de travail seulement (pas délais légaux affirmés) : purger rapidement les demandes refusées/abandonnées après durée justifiée ; GPS dès qu'inutile ; éviter conservation indéfinie des logs, notifications et dossiers. Respecter les exceptions légales et la traçabilité.

Planifier des **sauvegardes PostgreSQL** chiffrées, rétention, contrôle des accès, restauration testée et suppression propagée aux copies selon politique. Ne pas considérer la simple présence de PostgreSQL Railway comme une sauvegarde complète ; vérifier les capacités et conditions du plan. Définir objectifs RPO/RTO en fonction du budget et des risques, puis effectuer au moins un exercice de restauration synthétique avant ouverture.

Prévoir contrôles de santé de Django, alertes pour erreurs 5xx/DB indisponible, limites de crédit/coût, sécurité MFA, saturation des jobs. Procédure d'incident : isoler application si nécessaire, limiter accès, préserver preuves minimisées, évaluer impact, informer les responsables et respecter obligations confirmées. Aucun envoi de données de patients vers des services de télémétrie non approuvés.

## 6. Déploiement Railway

Service Django avec build/install dépendances verrouillées, migrations contrôlées avant activation et collectstatic ; Gunicorn ou serveur équivalent conforme ; port `$PORT` ; healthcheck documenté. PostgreSQL attaché sur réseau privé, accès internet désactivé sauf raison documentée. `DATABASE_URL`, secrets et tokens dans variables Railway (jamais Git). Domaine Railway généré depuis le tableau de bord et exact hôte ajouté à Django. Paramétrer HTTPS/proxy uniquement après vérification du comportement réel.

Prévoir mise en veille / épuisement du crédit : le domaine gratuit ne garantit pas le calcul gratuit. Préproduction et production distinctes si ressources suffisantes ; aucune donnée réelle en preview. Ne pas fermer Vercel tant que Railway n'est pas validé et financé durablement.

## 7. Vérifications bloquantes avant collecte réelle

MFA réellement imposé partout ; matrice de permissions et tentatives d'accès non autorisées ; CSRF et validation ; journalisation saine ; tests mobile et refus GPS ; test de sauvegarde/restauration ; budget et monitoring ; documentation du traitement des données et décision juridique. Tout échec bloque l'activation du formulaire sensible.

Références officielles : https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/ ; https://docs.railway.com/networking/domains/working-with-domains ; https://docs.railway.com/pricing/plans .
