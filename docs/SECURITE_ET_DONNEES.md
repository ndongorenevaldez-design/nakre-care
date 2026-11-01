# Sécurité, données et conditions d’activation

Cadrage du 1 novembre 2026. Ce document distingue exigences proposées, risques observés et vérifications à obtenir ; il ne constitue ni un avis juridique ni une attestation de conformité. La mission actuelle produit seulement de la documentation.

## 1. Risques et priorités

| Priorité | Risque | Réponse minimale avant activation |
| --- | --- | --- |
| Critique | Lecture/écriture de données patient par anon, compte sans MFA ou rôle inadapté | Contrôles serveur + RLS testés en accès direct ; aucun écran ou secret côté navigateur utilisé comme protection. |
| Haute, existante | Texte libre de situation et coordonnées transportés dans `wa.me?text=` | Conserver le contact générique, retirer ultérieurement le contenu sensible de l’URL et proposer un parcours sécurisé après validation. Informer dès le cadrage de ce flux externe. |
| Haute, existante | Formulaire sans method/action : repli GET sans JavaScript | Ne pas soumettre les réponses dans l’URL ; future soumission POST serveur ou repli explicite non collectant. |
| Haute | Hébergement/transferts et santé non qualifiés juridiquement | Autorisation juridique et technique écrite avant collecte réelle, y compris test utilisateur avec personnes réelles. |
| Haute | Clé service Supabase ou secret notification exposé | Secrets uniquement dans environnement serveur ; rotation, séparation des projets et examen des bundles/logs. Clé service contourne RLS. |
| Haute | Abus d’API publique et saturation des notifications | Quotas atomiques durables, challenge serveur si nécessaire, limites de taille/coût et file plafonnée ; pas de compteur en mémoire de Function. |
| Haute | Fuite par cache, logs, erreurs, monitoring et sauvegardes | no-store, redaction, logs sans corps de requête, accès sauvegardes restreint et rétention documentée. |
| Haute | Compte admin compromis ou oublié | MFA AAL2, comptes individuels, scopes, révocation, récupération contrôlée, durée de session bornée et audit. |
| Moyenne | Notification prétendue livrée ou doublonnée | Outbox transactionnelle et états fournisseur honnêtes, idempotence, retries plafonnés, déduplication webhooks. |
| Moyenne, existante | Menu absent sur recrutement mobile ; flottant mal synchronisé | Correction séparée avec tests de non-régression. |

L’absence de backend actuel réduit la surface serveur mais n’annule pas le risque des informations déjà saisies et transmises à WhatsApp. Les données de santé peuvent être déduites du contexte d’accompagnement, même sans diagnostic explicite.

## 2. Modèle d’accès et MFA

- Inscriptions publiques désactivées ; invitations administratives nominatives, validation de l’adresse et de la personne. Bootstrap du superadministrateur hors interface publique avec procédure documentée. Aucune identité de test partagée en production.
- Toutes les opérations métier exigent un JWT vérifié (signature via mécanisme officiel/JWKS, issuer, audience, expiration), AAL2, membership active et permission actuelle. Ne pas se contenter de décoder le token ou d’un garde frontend. Ne pas croire un rôle envoyé par le client ou modifiable dans user_metadata.
- MFA : inscription/challenge TOTP, écran d’enrôlement isolé ne donnant aucun accès métier en AAL1. Ne pas journaliser secret TOTP/QR/code. Perte de facteur : procédure contrôlée, preuve d’identité, révocation des sessions, audit et notification minimale. Réauthentification pour rôles, export et récupération.
- Cookies Secure/HttpOnly/SameSite, rotation et logout révoquant côté serveur ; durée d’inactivité et durée absolue à valider. Origine vérifiée, protection CSRF pour mutations authentifiées, CORS limité aux origines connues ; pas de CORS universel avec credentials.
- Chaque table exposable a RLS activée et politiques explicites. Tester SELECT/INSERT/UPDATE/DELETE, WITH CHECK, champs immuables et chemins RPC. anon n’a aucune lecture des tables métier. L’ingestion serveur utilise un chemin restreint sans permettre de statut, rôle, auteur ou identifiant choisis par le client.
- Les requêtes admin utilisent l’identité utilisateur ; membership/affectation et AAL2 sont contrôlés en DB aussi. Permissions de gestion des membres non autoattribuables. Fonctions SECURITY DEFINER rares, search_path fixé, EXECUTE limité, validations explicites ; audit des risques de bypass de RLS par propriétaire/service_role/vues.
- L’audit est append-only pour les rôles applicatifs. Une garantie contre un administrateur de base requiert un stockage séparé/inaltérable et des contrôles d’exploitation ; ne pas présenter une simple table comme inviolable.

## 3. Validation et anti-abus

Validation indépendante côté serveur : types, listes autorisées, longueurs, téléphone, e-mail, dates, coordonnées GPS dans les plages valides et cohérence du lieu. Corps JSON limité (proposition 16 Kio), refus de multipart/base64/fichiers, rejet des champs inattendus. Requêtes SQL paramétrées ; affichage texte échappé, jamais innerHTML de contenu libre. Erreurs publiques génériques avec identifiant technique sans contenu patient. Limiter aussi les réponses, filtres, pagination et tris admin.

Rate limiting distribué/atomique par clés minimisées (par exemple IP pseudonymisée et fenêtre temporelle), plafond global et protections login/récupération. Tenir compte des réseaux partagés : seuils à tester, pas de blocage fondé uniquement sur l’IP. Challenge anti-robot vérifié serveur, honeypot accessible correctement, quotas d’envoi et idempotence bornée. Ces prestataires ajoutent des flux de données à analyser. Une vérification Origin seule ne protège pas une API anonyme contre un bot.

## 4. Inventaire et minimisation

| Données | Usage / accès | Mesure de réduction |
| --- | --- | --- |
| Coordonnées demandeur/bénéficiaire | Traitement de la demande, équipe habilitée | Seulement contacts utiles ; aucun identifiant national ni date de naissance complète par défaut. |
| Besoin et contexte | Organisation de l’aide, admins affectés | Catégories et texte court optionnel, pas de dossier clinique, ordonnance ou document. |
| Adresse/GPS | Intervention | Position facultative et révocable ; ne pas inclure dans notifications, cartes tierces ou logs. |
| Contacts autorisés | Communication limitée | Vérifier identité, relation, finalités, dates et périmètre ; ne pas déduire l’autorisation d’un lien familial déclaré. |
| Prestations | Continuité et responsabilité | Compte rendu factuel minimal, auteurs et corrections traçables, pas de notes médicales extensibles. |
| Auth/audit/anti-abus | Accès et sécurité | Sans mots de passe, codes MFA, corps des demandes ou copie des notes. IP brute évitée ou rétention courte justifiée. |
| Notifications | Alerte opérationnelle | Texte générique et destinataire autorisé, pas de nom patient, santé, lieu ou lien public de dossier. |

Registre des finalités, responsables, bases légales, destinataires/sous-traitants, régions, durées et moyens d’exercice des droits à produire avant lancement. Référence aléatoire ne suffit pas à anonymiser les données. Aucun analytics, replay de session, stockage local persistant ou outil d’IA appliqué aux formulaires/dossiers sans analyse et autorisation séparées.

## 5. Loi camerounaise n° 2024/017 : analyse préalable requise

La loi n° 2024/017 du 23 décembre 2024 relative à la protection des données à caractère personnel constitue le texte de référence à faire vérifier pour ce service camerounais. Le texte officiel consolidé, les textes d’application, l’autorité compétente, les formalités et le régime transitoire applicables au lancement n’ont pas pu être vérifiés en ligne dans cette session. Aucun numéro d’article, délai légal, exemption ou autorisation acquise n’est affirmé ici.

La présence de données de personnes vulnérables, potentiellement de santé, et de positions précises exige une qualification renforcée. Le consentement du demandeur ne prouve pas celui du patient ; il faut déterminer les conditions de représentation, d’information du bénéficiaire, de capacité et, le cas échéant, le cas des mineurs. Un consentement générique n’autorise pas toutes les finalités et tous les transferts.

| Question à faire trancher par conseil compétent au Cameroun | Livrable attendu / conséquence |
| --- | --- |
| Qualification des données et bases légales par finalité | Matrice signée : demandes, dossiers, suivi, contacts, sécurité, notifications ; nécessité/proportionnalité et régime spécifique santé. |
| Identité et responsabilités | Responsable du traitement NAKRE CARE, contacts, sous-traitants, obligations contractuelles, responsable interne et éventuel délégué selon critères applicables. |
| Formalités préalables | Vérification des déclarations/autorisations requises pour données sensibles, géolocalisation et transferts ; obtenir les actes nécessaires avant activation. |
| Hébergement hors Cameroun | Cartographier Vercel, région Supabase, Auth, sauvegardes, logs, support, e-mail, Meta/BSP et anti-spam ; bases/mécanismes et éventuelles autorisations de transfert. Choisir une région européenne n’établit pas à elle seule la conformité au droit camerounais. |
| Information, consentement et droits | Notice française accessible, preuves versionnées, gestion des tiers, accès/rectification/opposition/retrait/effacement selon règles applicables, exceptions et délais validés. |
| Conservation et obligations sectorielles | Calendrier justifié, obligations de preuve/prestation et éventuelles restrictions santé ; suppression sélective et sauvegardes incluses. |
| Analyse d’impact, incidents et gouvernance | Déterminer les obligations applicables, documenter risques résiduels, destinataires et délais de notification des violations ; procédure de crise et validation. |
| Entrée en vigueur et transition | Date de pleine applicabilité et mesures requises confirmées à la date de mise en service, sans supposer une période de grâce. |

Le site reste vitrine tant que ces points bloquants ne sont pas tranchés. Une future politique de confidentialité doit décrire le fonctionnement réellement retenu ; ne pas publier de promesse de conformité ou d’hébergement local non prouvée. Les données déjà échangées via WhatsApp doivent aussi entrer dans l’inventaire métier et les consignes internes.

## 6. Conservation, suppression et sauvegardes

Politique à valider juridiquement avant toute application automatique. Hypothèses de travail uniquement : demandes abandonnées/refusées 90 jours après clôture ; GPS effacé dès qu’il n’est plus utile à l’intervention ; historique notifications 90 jours ; logs techniques 30 jours ; audit de sécurité 12 mois. La durée des dossiers/prestations doit être fixée selon obligations métier et légales ; pas de conservation infinie « par défaut ». Ces durées ne sont pas des durées imposées par la loi citée.

Définir déclencheur, responsable, exceptions de litige, purge des relations/outbox et preuve minimale de suppression sans recopier les données supprimées. Une suppression de compte Auth ne supprime pas automatiquement un dossier. Vérifier l’identité lors des demandes de droits, y compris celles d’un tiers ; ne pas divulguer l’existence d’un dossier à une personne non autorisée. Prévoir registre des demandes et notification aux sous-traitants lorsque nécessaire.

Sauvegardes chiffrées, accès séparé, rétention et localisation documentées, restauration testée sur environnement isolé et nettoyé. Cibles proposées RPO ≤24 h et RTO ≤8 h à chiffrer/valider ; choisir PITR si nécessaire et financé. Prévoir comment rejouer les suppressions après restauration et l’expiration des copies. Ni réplication ni promesse commerciale de backup ne remplacent un essai de restauration. Ne jamais copier les données de production vers une preview.

## 7. Déploiement, secrets et exploitation

Secrets dans variables serveur par environnement : credentials DB/ingestion, credentials notification, signatures webhooks, secret d’ordonnanceur et anti-spam. Clé publique Supabase/Auth seulement si nécessaire au design retenu et sûre avec RLS ; aucune clé service dans un asset, HTML, variable exposée au build ou Git. Rotation et procédure d’urgence ; scans du diff, de l’historique et des bundles avant lancement. Ne pas collecter de secret pendant l’audit documentaire.

Configurer HTTPS, HSTS après vérification du domaine, nosniff, Referrer-Policy restrictive, CSP adaptée (JSON-LD et styles inline actuels à traiter par hashes/nonces ou externalisation ciblée, sans unsafe-inline généralisé), frame-ancestors et Permissions-Policy pour géolocalisation limitée à self. Vérifier les headers effectivement servis, pas seulement le fichier de configuration. no-store pour auth/API/admin/confirmation et absence de mise en cache CDN des données ; noindex admin sans croire que cela sécurise l’accès.

Projets et identités distincts pour dev/préproduction/production. Protections de branche main, PR, revue, migrations réversibles ou correctives documentées, approbation de production. Préviews protégées, données synthétiques, notifications de capture désactivées pour l’extérieur. Alertes sur 5xx, ingestion, file en retard, MFA/login anormaux, quota/coût et sauvegarde manquante. Ne pas envoyer de détails sensibles à l’outil de monitoring.

Incident : arrêter la collecte si nécessaire, limiter l’accès, révoquer/rotater, préserver des preuves minimisées, qualifier l’impact, informer les responsables et appliquer les délais légaux confirmés. Procédure et exercice avant lancement.

## 8. Sources à vérifier avant décision

Sources officielles de référence, non consultées en ligne dans cette session : portail de la Présidence du Cameroun <https://www.prc.cm/> (obtenir la loi n° 2024/017 et textes associés) ; Supabase RLS <https://supabase.com/docs/guides/database/postgres/row-level-security>, MFA <https://supabase.com/docs/guides/auth/auth-mfa>, sauvegardes <https://supabase.com/docs/guides/platform/backups> ; Vercel Functions <https://vercel.com/docs/functions>, pricing <https://vercel.com/pricing> ; Supabase pricing <https://supabase.com/pricing> ; WhatsApp Business Platform <https://developers.facebook.com/docs/whatsapp/>. Valider la version, les contrats et les capacités réelles du plan choisi. Ne pas utiliser ces liens comme preuve que les formalités ou fonctionnalités sont déjà satisfaites.
