# Cahier des charges — NAKRE CARE

Version de cadrage du 1 novembre 2026, à valider. Aucun développement fonctionnel engagé. Architecture et audit dans [ARCHITECTURE_CIBLE.md](ARCHITECTURE_CIBLE.md).

## 1. Objectifs et limites

Conserver la vitrine à Yaoundé, la marque, les médias, les contenus utiles et le SEO. Structurer la réception des demandes sans compte public, leur traitement par plusieurs administrateurs nominatifs et le suivi des prestations. Aucune facturation numérique, paiement, connexion client, pièce jointe ou téléversement de document médical. Ce service ne remplace pas les urgences ni une consultation médicale.

## 2. Parcours public

- Accueil/recrutement existants préservés. WhatsApp au +237674134365 maintenu pour contact générique ; avertir de ne pas transmettre de dossier médical par ce canal.
- `/demande/` accessible directement, partageable sur WhatsApp avec un lien générique sans identité, santé, adresse, GPS ou référence de patient dans l’URL. Pas de connexion, pas d’outil de suivi public de dossier.
- Expliquer le but, les champs requis, le délai de réponse indicatif validé par l’équipe et la distinction entre réception et acceptation. Ne pas promettre une prise en charge automatique.
- Formulaire en français, utilisable sur mobile et réseau lent, sans carte ni GPS obligatoire, sans pièce jointe. Ne pas persister le brouillon sensible dans le navigateur. Préserver les valeurs en mémoire lors d’une erreur de connexion, avec avertissement sur appareil partagé.

### Dictionnaire de collecte proposé

| Groupe | Champs | Obligation et limites proposées |
| --- | --- | --- |
| Demandeur | Nom usuel, téléphone, relation au bénéficiaire ; e-mail facultatif | Nom 2–120 caractères, téléphone normalisé selon pays ; e-mail ≤254. Pas de pièce d’identité. |
| Bénéficiaire | Nom usuel et téléphone si différent/utile ; tranche d’âge facultative | Nom requis si confirmé nécessaire ; pas de date de naissance exacte par défaut. Coordonnées non requises si personne injoignable directement. |
| Besoin | Domicile, milieu hospitalier, rendez-vous/déplacement, autre demande d’information | Valeur issue d’une liste autorisée ; pas de diagnostic obligatoire. |
| Situation | Court contexte d’accompagnement | Facultatif, ≤1000 caractères ; inviter à exclure diagnostic, ordonnance, numéro de dossier et détail médical. Réévaluer la nécessité juridique de ce champ. |
| Disponibilité | Date souhaitée, plages horaires, fréquence envisagée | Distinguer souhait et engagement ; validation cohérente des dates côté serveur. |
| Lieu | Ville/quartier requis ; indications pratiques limitées | Yaoundé et couverture à confirmer ; adresse précise uniquement si nécessaire à la visite. Longueurs bornées. |
| GPS | Latitude, longitude, précision et date du relevé | Entièrement facultatif, acquis après action explicite ; aucune géolocalisation à l’ouverture, aucun suivi continu. |
| Information et consentements | Notice versionnée, accord explicite adapté à la base juridique, déclaration de qualité du demandeur | Cases distinctes, non précochées ; autorité du tiers à vérifier avant divulgation ou prestation. Pas de consentement marketing groupé. |

Ces limites sont des propositions de contrat serveur à confirmer, pas des contrôles déjà implémentés. Le demandeur peut être le bénéficiaire ; éviter les doubles saisies. Aucun champ libre illimité ni fichier encodé dans du JSON.

### GPS, envoi et confirmation

Bouton « Ajouter ma position » distinct, explication de la finalité, permission navigateur, possibilité de retirer la position ; refus, timeout ou absence d’API ne bloquent jamais l’alternative manuelle. Demander confirmation que la position correspond au lieu d’intervention et pas seulement à celle du demandeur. HTTPS requis en production.

À la soumission : serveur valide, contrôle spam/quota et idempotence, puis stocke atomiquement. Afficher la référence aléatoire après succès confirmé, sans répéter les détails sensibles. Si indisponibilité, montrer une erreur honnête, pas une référence fictive ni une fausse réussite. Une notification échouée n’annule pas une demande enregistrée. Référence en réponse POST/session mémoire, pas une clé publique d’accès aux données. Confirmation marquée no-store/noindex, sans paramètres sensibles.

Accessibilité cible WCAG 2.2 AA sur parcours modifiés : labels/aides, résumé et erreurs liées aux champs, focus géré, messages annoncés, clavier, zoom et contrastes. Tester à 320 px et en paysage, avec permissions refusées, JavaScript indisponible et connexion interrompue. Aucun repli GET contenant les réponses.

## 3. Administration privée

Comptes nominatifs, invitation uniquement, pas d’inscription publique. Mot de passe + MFA TOTP obligatoire pour toute lecture/écriture métier. Le premier superadministrateur est provisionné par une procédure hors interface publique ; aucune route de bootstrap ouverte ni mot de passe par défaut. Réinitialiser le mot de passe ne dispense pas de MFA. Récupération de compte et perte de facteur avec vérification d’identité, révocation et journalisation.

| Capacité | Superadministrateur | Administrateur opérationnel |
| --- | --- | --- |
| Gérer comptes/rôles, désactiver, récupération MFA | Oui, réauthentification forte | Non |
| Liste et détail de demandes | Oui | Selon permission et périmètre attribués |
| Statuts et conversion en dossier | Oui | Si droit de traitement sur la demande |
| Contacts autorisés et prestations | Oui | Seulement sur dossiers affectés et droit approprié |
| Journal d’audit et historique notifications | Oui | Vue limitée si droit explicite, sans secret |
| Export de masse, purge, paramétrage de conservation | Procédure contrôlée, pas par défaut | Non |

Refuser par défaut ; pas de rôle autoattribuable ni de droits dérivés d’un e-mail présent dans le frontend. Modifier/désactiver un compte doit prendre effet sur les opérations suivantes, même si son JWT n’est pas encore expiré. Définir explicitement qui voit la file des demandes non affectées, pour éviter à la fois l’exposition générale et une file inaccessible.

Écrans : connexion/MFA ; liste paginée avec statut, date, besoin et affectation ; détail limité au périmètre ; transition avec raison ; conversion ; dossier et contacts ; timeline ; historique des notifications et audit selon rôle. Aucun cache public ni données patient dans URL/titre de notification/outil d’analytics.

### Cycle métier

Demande : `nouvelle → en_examen → acceptee | refusee | annulee`. Autoriser `nouvelle → annulee` ; toute réouverture exceptionnelle exige un droit explicite et une raison. Définir la politique de doublons avant conversion. Acceptation et création du dossier dans une transaction unique ; un seul dossier par demande source, double clic et concurrence sans duplication. Conserver l’événement et l’acteur de chaque transition ; le motif peut être sensible et reste privé.

Dossier : `actif → suspendu | clos`, reprise contrôlée. Contacts autorisés ajoutés après vérification de leur qualité et du périmètre consenti, révocables. Une adresse/numéro renseigné ne donne aucun droit d’accès. Timeline : date de prestation et date de saisie distinctes, auteur, type, état (prévue/réalisée/annulée) et note factuelle limitée ; correction par événement traçable. Les statuts et dictionnaires définitifs doivent être approuvés avant migration.

## 4. Notifications

E-mail et WhatsApp via fournisseurs officiels, sous réserve d’activation, opt-in applicable et destinataires autorisés. Première alerte destinée à l’équipe habilitée ; accusé au demandeur uniquement au canal autorisé. Exemple : « Une nouvelle demande est disponible dans votre espace sécurisé. » Lien générique vers login admin pour l’équipe. Aucun diagnostic, nom patient, contexte, GPS, adresse ou identifiant donnant accès au dossier dans une notification.

États distincts : `queued`, `processing`, `provider_accepted`, `delivered`, `failed`, `dead_letter`, et éventuellement `delivery_unknown`. L’acceptation d’une API ne prouve pas la livraison. Un transport non configuré reste désactivé/bloqué, jamais marqué envoyé. Historique des tentatives, code d’erreur nettoyé, identifiant fournisseur, timestamps et prochaine tentative ; pas de payload sensible ni token dans les logs. Webhooks signés et dédupliqués. Relance manuelle contrôlée et retry avec backoff/plafond ; ne pas garantir exactement une livraison si le fournisseur ne fournit pas l’idempotence.

Un numéro WhatsApp utilisé par wa.me n’est pas automatiquement éligible à l’envoi Business Platform. Vérifier propriété, compte Meta, coexistence/migration éventuelle, modèles approuvés, consentement et tarification avant choix du prestataire. Tests avec boîte de capture et adaptateur de test explicitement nommé ; les succès de test ne doivent jamais apparaître comme des envois réels réussis.

## 5. Critères de recette bloquants

| Parcours | Preuve attendue |
| --- | --- |
| Vitrine | URL/canonical/contenu/médias conservés ; liens internes et WhatsApp générique fonctionnels ; pas de régression clavier/mobile. |
| Demande | Contrôle serveur indépendant du JS ; stockage réel de test, référence unique, consentement versionné, refus des données surdimensionnées et fichiers, retry sans doublon. |
| Localisation | Permission seulement après clic, retrait possible, refus et saisie manuelle testés. |
| Confidentialité | Anonyme ne peut lire ni modifier aucune demande ; référence ne permet aucune recherche publique ; logs/cache/URLs nettoyés. |
| Auth/RLS | Session absente, AAL1, compte désactivé, rôle insuffisant et accès au dossier d’un autre périmètre sont refusés via API ET accès DB direct. |
| Métier | Conversion concurrente sans double dossier ; contacts non autorisés exclus ; corrections et transitions auditées. |
| Notifications | Erreurs et indisponibilité visibles, signature/rejeu testés, pas de faux « livré », aucun contenu sensible ; aucune émission réelle pendant les tests. |
| Exploitation | Sauvegarde restaurée en environnement isolé, révocation testée, purge contrôlée, alerte de panne/quota, rollback sans perte de demandes. |

Données de recette entièrement synthétiques. Collecte réelle bloquée jusqu’aux validations décrites dans [SECURITE_ET_DONNEES.md](SECURITE_ET_DONNEES.md).
