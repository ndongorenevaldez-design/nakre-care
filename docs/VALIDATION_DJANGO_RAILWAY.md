# Rapport de validation — Django complet sur Railway

1 novembre 2026. Rapport de conception pour décision du propriétaire. Aucun développement fonctionnel, service Railway, souscription ou déploiement effectué. La validation demandée à la fin de ce rapport porte sur le passage à la préparation applicative ; elle ne vaut pas autorisation de production.

## 1. État réel et portée de la revue

| Élément | Preuve / résultat |
| --- | --- |
| `main` distant | `ba669260a8d21fc84c313f48d42fe58f8e159a8a` au contrôle Git. Site statique conservé. |
| Première branche documentaire | `docs/audit-architecture-nakre-care`, `dde57ebf62d796f32e15ee5f41d5b8024baf5e50`. Proposition Supabase/Vercel historique, désormais remplacée. |
| Nouvelle branche documentaire | `docs/django-railway-fullstack-20261101`, `a2f760b97c7c8a0cec28c38c5389a0da9edd49e5`, récupérée et lue. |
| PR #1 | `refs/pull/1/head` pointe sur ce même `a2f760b…`. La présence d’une référence de merge est un résultat Git synthétique, pas la preuve d’une fusion. `main` ne contient pas ces documents. |
| Métadonnées GitHub | `gh pr view 1` refusé par le proxy (`Forbidden` sur api.github.com/graphql). État ouvert/fermé, base déclarée, discussions, checks et revues non vérifiés. |
| Fichiers relus | ARCHITECTURE_CIBLE, CAHIER_DES_CHARGES, SECURITE_ET_DONNEES, PLAN_IMPLEMENTATION, PROMPT_CODEX_DJANGO_RAILWAY. Aucun AGENTS.md trouvé. |
| Code applicatif | Le diff de la nouvelle branche par rapport à main contient uniquement ces cinq documents. Ni backend ni migration de site déjà réalisés. |
| Branche du rapport | `docs/validation-django-railway-20261101`, dérivée de `a2f760b…`, pour préserver le travail existant et main. |

Les cinq documents sont cohérents avec **Django Templates + Django Forms + Django Auth + PostgreSQL, entièrement sur Railway**. Les mentions de Supabase/Vercel Functions servent à exclure l’ancienne cible ; elles ne demandent pas sa mise en œuvre. La mention « décision validée » valide le choix de technologie, pas l’implémentation, qui attend l’accord demandé dans la mission.

Ajustements ciblés : actualiser la ligne historique « aucune PR signalée », qualifier les crédits Railway non vérifiés sur le compte et renvoyer au présent complément. Les cinq documents ne sont pas réécrits. Les tarifs et l’état du compte Railway ne sont pas accessibles dans cette session ; aucun montant de crédit n’est acquis.

## 2. Architecture proposée pour validation

Monolithe Django **5.2 LTS**, dernier correctif de sécurité disponible à vérifier et verrouiller au début de l’implémentation ; Python 3.12 comme base compatible, à confirmer avec les dépendances. PostgreSQL 17 proposé, version réellement disponible et maintenue sur Railway à qualifier avant provisionnement. Django Templates/Forms, Gunicorn WSGI, Staticfiles/WhiteNoise ; aucune SPA et aucun SDK Supabase.

Apps : website (pages), intake (demandes), accounts (comptes/MFA/politiques), patients (dossiers/contacts/plans), interventions, notifications, audit. Les transactions et transitions passent par des services métier réutilisés dans les vues et Django Admin ; les formulaires restent responsables de la validation des entrées. Ne pas dupliquer les règles entre Admin et tableau de bord.

Le service web sert `/`, `/recrutement/`, `/prise-en-charge/`, sa confirmation, `/confidentialite/`, `/administration/` et le Django Admin protégé. Une seule origine Railway pour public et privé. Un processus séparé consomme l’outbox PostgreSQL : worker Railway ou exécution planifiée selon délai et coût validés. Pas de Redis/Celery au départ tant qu’un consommateur PostgreSQL suffit ; une outbox durable est nécessaire même si les transports sont désactivés. Aucun envoi dans la transaction de réception ou dans un thread non durable du serveur web.

## 3. Migration minimale de l’existant

- Garder les fichiers statiques déployés sur Vercel pendant la construction. Transformer des copies contrôlées des deux pages en templates Django, avec base/en-tête/pied communs, balises static et URL nommées. Réutiliser médias, palette CSS et textes métier confirmés.
- Dans la version Django, remplacer le questionnaire WhatsApp par le parcours POST interne ; conserver les boutons WhatsApp génériques. Le risque GET et l’envoi de texte libre existants restent présents sur l’ancienne production tant qu’une correction Vercel distincte n’a pas été autorisée. Ne pas prétendre qu’ils sont déjà corrigés.
- Corriger sur la nouvelle version le menu de recrutement mobile, les dimensions déclarées des photographies et la logique IntersectionObserver identifiés par l’audit. Pas de refonte visuelle globale.
- Conserver ancres et chemins publics utiles. Les anciennes URL `/assets/...` peuvent continuer à être servies comme statiques sur Railway pour les liens conservés ; choisir un seul emplacement source afin d’éviter des copies divergentes. Aucun upload utilisateur ni service de médias patient.
- Conserver les métadonnées utiles ; les canonical, Open Graph, sitemap, robots et JSON-LD doivent utiliser l’origine réellement retenue lors de la bascule. Préproduction protégée et noindex ; origine publique centralisée et jamais déduite d’un Host arbitraire. Exclure administration/confirmation de l’index.
- Le domaine vercel.app ne peut être transféré. Communiquer la nouvelle adresse et préparer des redirections route par route sur Vercel uniquement sur autorisation distincte ; garder l’ancien service assez longtemps si l’on veut maintenir ces redirections. Aucun retrait automatique.

## 4. Référence visuelle et fiche officielle

L’image jointe au message a été examinée : logo N vert, fond ivoire, bandeaux verts avec pictogrammes, accent terre cuite pour les observations, deux colonnes et huit sections numérotées. Le fichier local `assets/logo-mark-nakre.png`, examiné, montre le monogramme N compatible avec cette référence. Le site utilise actuellement un autre fichier, `assets/logo-nakre-care.svg` ; déterminer le verrouillage logo complet/monogramme à partir des assets officiels, sans redessiner ni remplacer arbitrairement le logo.

**Disponibilité :** référence visible dans le chat, mais aucun fichier de cette fiche trouvé dans `/workspace/attachments` ou dans les assets du dépôt ; seul le texte de mission est téléchargeable ici. La référence n’est donc pas encore conservée comme asset reproductible dans le workspace. Pour l’intégration et la recette visuelles ultérieures, fournir le fichier image/PDF original dans le workspace (sans données de personne). Cela ne bloque pas le schéma ni cette revue. Ne pas reconstruire le logo à partir d’une capture et ne pas extraire des codes couleur d’une image compressée comme nouvelle palette.

| Section | Correspondance et arbitrage de collecte |
| --- | --- |
| 1 — Demandeur | Noms/prénoms, relation, téléphone, WhatsApp, ville, quartier/adresse ; e-mail facultatif ajouté par la mission, absent de la fiche papier. |
| 2 — Personne à accompagner | Identité, âge, lieu ; sexe seulement si nécessité confirmée. Situation domicile/hospitalisation/convalescence/autre, autonomie oui/non/partielle, mobilité seule/avec aide/alitée, alimentation/toilettes oui/non/avec aide. Prévoir « non renseigné » pour les informations inconnues ; ne pas confondre vide et « non ». |
| 3 — Santé/situation | La fiche demande problème principal, handicap, traitement/médicaments, besoin familial et urgence faible/modérée/urgente. Proposer de laisser traitements/médicaments désactivés tant que leur nécessité n’est pas approuvée. Conserver la rubrique et expliquer les adaptations validées ; ne pas recopier automatiquement une collecte clinique détaillée. L’urgence déclarée sert à organiser un rappel, sans promettre une réponse d’urgence médicale. |
| 4 — Accompagnement | Liste papier : domicile, hospitalier, hygiène, mobilité, garde jour/nuit, ponctuel/régulier, surveillance/présence rassurante, autre. Confronter ces choix aux prestations effectivement proposées ; ne pas publier un service non confirmé. Les déplacements utiles figurent dans la mission/site : ajout explicite à valider, pas omission silencieuse. |
| 5 — Disponibilité | Début souhaité, ponctuel/temporaire/régulier, horaires, jour/nuit/les deux, fréquence et durée si utile. Préférence ≠ rendez-vous confirmé. |
| 6 — Contact | Nom, lien, téléphone principal/secondaire. Contact proposé ≠ contact autorisé ; vérification préalable au partage de données. |
| 7 — Observations | Texte court facultatif, proposition 1000 caractères maximum ; exclure les détails médicaux inutiles et toute pièce jointe. |
| 8 — Interne | Réception, évaluateur, date, orientation, suite, état et historique. Formulaire et modèle de validation internes distincts ; aucun champ caché dans le POST public ne doit permettre de modifier ces valeurs. |

Affichage responsive : deux colonnes sur écran large, une sur mobile, fieldsets/legends, labels, erreurs liées aux champs, résumé d’erreurs et focus. GPS ajouté par action explicite, coordonnées supprimables, adresse manuelle suffisante et confirmation du lieu réel d’intervention. Le refus GPS n’est pas une erreur bloquante. Les choix papier ne sont pas tous indépendants : listes exclusives pour autonomie, mobilité et jour/nuit ; choix multiples seulement pour services/situations compatibles.

## 5. Schéma relationnel PostgreSQL proposé

Conception seulement : aucune migration générée. UUID internes pour les objets métier, timestamps UTC, dates/heures métier affichées en `Africa/Douala`. Champs sensibles structurés et bornés, pas de grand JSON permettant d’enregistrer tout le POST.

| Modèle | Relations et contraintes clés |
| --- | --- |
| `User` dans accounts | Modèle personnalisé dès migration initiale, basé sur AbstractUser avec connexion par e-mail, unicité insensible à la casse en DB (normalisation explicite), pas de signup public. Groupes/permissions Django, is_active, version de session pour révocation. Aucun compte créé ici. |
| `AdminRole` | Représenté initialement par Groups/Permissions Django plutôt qu’une seconde table de rôles concurrente. Deux profils : superadministrateur et administrateur opérationnel. Affectations objet séparées. |
| `CareRequest` | Référence aléatoire unique (au moins 128 bits d’entropie), statut, version, identité/contacts demandeur et bénéficiaire, relation, contexte minimal, disponibilité, lieu distinct, GPS facultatif, submitted_at. Âge entier optionnel 0–120, choix bornés, longueurs sur texte/téléphone. La référence n’authentifie personne. |
| `ServiceType` + lien demande/service | Catalogue métier stable de services approuvés, code unique, actif/inactif ; unicité de la paire. Types historiques conservés si désactivés. |
| `ConsentRecord` | FK demande, version notice et finalité, fondement/accord approprié, qualité déclarant, date. Corrections par événement, pas de réécriture de preuve ; permission GPS distincte. |
| `RequestAssignment` | FK demande + User, unicité de la paire, droit de traitement, dates ; nécessaire pour la file avant conversion en dossier. Permissions spéciales pour la file non affectée. |
| `RequestReview` | FK demande, évaluateur User, date, orientation/suite bornées et transition. Représente la section 8, créée exclusivement par service interne autorisé. |
| `PatientCase` | OneToOne vers demande source, statut actif/suspendu/clos, dates ; unicité DB contre double conversion. Pas de déduplication de personnes par nom ; pas de fusion automatique. |
| `CaseAssignment` | FK dossier + User, périmètre et dates/révocation, unicité d’une affectation active par paire. Le membre du personnel intervenant n’est pas automatiquement administrateur. |
| `AuthorizedContact` | FK dossier, coordonnées nécessaires, relation, périmètre autorisé, vérification par User/date, validité/révocation. Les contacts soumis restent dans la demande jusqu’à vérification ; pas de transfert automatique en autorisation. |
| `CarePlan` | FK dossier, version unique par dossier, dates, fréquence et services approuvés ; au plus un plan actif avec contrainte partielle. Mise à jour versionnée, historique conservé selon politique. |
| `StaffMember` | Référence d’intervenant, identité professionnelle minimale, actif ; User facultatif si la personne a réellement besoin de connexion. Pas d’espace intervenant inclus dans le premier périmètre. |
| `Intervention` | FK plan et intervenant, début/fin prévus, dates réelles optionnelles, prévue/effectuée/annulée, note factuelle limitée. CHECK fin ≥ début ; contrôle des chevauchements et de cohérence dossier/plan dans service métier. |
| `InterventionEvent` | FK intervention + acteur, date effective/date de saisie, transition/correction et note bornée. Pas d’écrasement silencieux d’une prestation passée. |
| `AuditEvent` | Acteur nullable pour événement système, action, cible UUID/type, date/résultat ; aucune copie de santé/contact dans le journal. Rôles applicatifs sans modification/suppression arbitraire de l’audit. Pas de garantie d’inaltérabilité contre DBA sans dispositif supplémentaire. |
| `NotificationOutbox` | Type d’événement, cible technique, canal/destinataire habilité, état, scheduled_at, lease_until et clé de déduplication unique. Aucun corps de formulaire. |
| `NotificationAttempt` | FK outbox, numéro de tentative unique par job, réponse fournisseur nettoyée, identifiant externe, statut et dates. État accepté ≠ livré. |
| `SubmissionToken` | Jeton aléatoire à durée limitée lié à session anonyme serveur, unicité ; référence interne à demande créée. Réutilisation ne crée pas une deuxième demande. Jamais un mécanisme de lecture publique. |

Index : demande `(status, submitted_at)`, affectations `(user, active)`, dossier/statut, interventions `(plan, scheduled_start)` et `(staff, scheduled_start)`, outbox `(status, scheduled_at)` et audit `(target_id, created_at)`. Vérifier les plans de requête sur jeux synthétiques avant ajout d’index supplémentaires. Ne pas indexer tout le texte sensible par défaut.

Conversion : `transaction.atomic`, verrou `select_for_update` sur demande, autorisation courante, transition attendue et contrainte OneToOne ; créer dossier, trace et outbox dans la même transaction. Deux validations concurrentes retournent le résultat existant ou un conflit clair. Les autres mutations utilisent une version attendue et refusent une écriture périmée. Validation ORM seule insuffisante : contraintes DB et tests PostgreSQL concurrents.

Suppression : FKs PROTECT pour références métier à conserver, CASCADE uniquement pour dépendances dont la purge est décidée ; audit minimal avec identifiant technique sans dépendance exigeant de conserver indéfiniment le patient. Politique de purge explicite pour demande/dossier/contact/notifications/preuves/sauvegardes avant activation réelle.

## 6. Authentification et permissions proposées

Choix proposé : `django-two-factor-auth` avec `django-otp` pour TOTP, versions compatibles Django 5.2 à vérifier/verrouiller lors de la préparation. Bibliothèque éprouvée plutôt que MFA maison. Session Django côté serveur (DB), cookie Secure/HttpOnly/SameSite, pas de session signée contenant des réponses patient ni de tokens en localStorage. Protection anti-bruteforce durable (par exemple django-axes, compatibilité à qualifier) et quotas de soumission PostgreSQL atomiques ; ne pas utiliser un cache local au processus comme limite distribuée.

Invitation par responsable : jeton à expiration, usage unique, adresse vérifiée, inscription MFA avant tout accès aux données. Provisionnement initial du superadministrateur via commande contrôlée, jamais route publique ni mot de passe dans une migration. Aucun « contournement d’urgence » web sans MFA. Récupération par codes à usage unique si le package les protège correctement, sinon procédure d’identité contrôlée ; révocation de toutes les sessions après perte/réinitialisation de facteur. Secrets TOTP sauvegardés avec les mêmes restrictions que la base, jamais dans les logs/QR enregistrés.

MFA imposé par politique centrale sur toutes les vues privées et par AdminSite adapté au package. Le backend password seul ne suffit pas : utilisateur actif, session vérifiée OTP et permission sont requis sur chaque requête, superadministrateurs inclus. Tester `/admin/login/`, routes alternatives, actions groupées, popups relationnels, autocomplete, historique et changements de compte. Enrôlement/récupération n’exposent aucun dossier. Revalidation de is_active et version de session à chaque accès pour révocation immédiate.

**Django ne fournit pas automatiquement des permissions par objet.** Groups/Permissions décrivent les capacités globales, RequestAssignment/CaseAssignment le périmètre. Politique de refus par défaut utilisée pour queryset, détail, écriture, FK/choices, actions et exports ; filtrer la liste ne protège pas les URL directes. Aucun accès direct navigateur à PostgreSQL. RLS PostgreSQL facultative en défense supplémentaire après conception dédiée, pas un héritage automatique de l’ancienne architecture Supabase.

| Opération | Superadministrateur | Administrateur |
| --- | --- | --- |
| Comptes/rôles/récupération | MFA et réauthentification, journal | Interdit ; ne peut modifier is_staff/is_superuser/groupes |
| File non affectée | Autorisé | Permission `triage_unassigned` explicite ; sinon aucune visibilité |
| Demande affectée/décision | Autorisé | Affectation active + capacité requise |
| Dossier, contacts, plan/intervention | Autorisé | Affectation dossier + capacité pour l’action |
| Affecter d’autres personnes | Autorisé | Permission de coordination explicite ; pas d’auto-extension de droits |
| Export massif/purge | Procédure séparée et audit, désactivé par défaut | Interdit |
| Audit/notification | Vue autorisée minimisée | Accès limité au périmètre et au besoin |

Recherches de noms/téléphones via POST interne, afin de ne pas placer ces données dans la query string de Django Admin ou des logs. Configurer/restrictre le search Admin natif en conséquence. CSRF sur chaque mutation, sortie HTML échappée, messages/sérialisation/__str__ sans santé, no-store sur réponses privées et confirmations.

## 7. Réception et notifications fiables

POST Forms avec liste explicite de champs publics (jamais ModelForm fields=all), CSRF, limites, validation, anti-spam et contrôle de concurrence. Pas de champ interne accepté même si injecté dans le POST. Recevoir en une transaction demande, consentement et outbox ; confirmation seulement après commit, via redirect vers page sans paramètres sensibles. Session serveur anonyme à durée limitée contenant seulement la référence technique de confirmation ; aucune page permettant de lire la demande avec cette référence. En cas de perte de session, ne pas exposer la demande pour « aider » à retrouver la référence.

Contact WhatsApp générique centralisé à +237674134365 ; adresse administrative provisoire `ndongorenevaldez@gmail.com` configurable côté serveur. Cette adresse est un destinataire proposé, pas un expéditeur SMTP authentifié ni une autorisation d’envoi pendant la revue. Sans domaine acheté, qualifier un fournisseur permettant un expéditeur vérifié ou une authentification Google appropriée ; ne pas annoncer que la délivrabilité est résolue.

Consommateur outbox avec verrouillage, bail expirant et reprise après crash, backoff et plafond ; état blocked/unconfigured si transport absent, jamais envoyé. Déduplication applicative et clé fournisseur lorsqu’elle existe. Un timeout après envoi peut laisser la livraison inconnue : ne pas promettre exactement un envoi. Webhooks signés, anti-rejeu et événement unique, mise à jour monotone. E-mail accepté par SMTP ≠ livré, WhatsApp accepté ≠ livré. Contenu limité à « nouvelle demande, connectez-vous » ; aucun nom patient, GPS ou note. Adaptateur de test/boîte de capture clairement identifiés, sans émission réelle.

## 8. Configuration Railway à réaliser après accord

| Élément | Décision / vérification à effectuer |
| --- | --- |
| Services | Web Gunicorn + PostgreSQL privés entre eux ; consommateur outbox séparé/planifié. Aucun provisioning pendant cette revue. |
| Build | Dépendances verrouillées, environnement Python épinglé et collectstatic ; aucun accès DB requis par le build. Pas de migrations dans chaque démarrage de replica. |
| Release | Migration contrôlée une fois avec identité dédiée ; vérifier que le mécanisme choisi peut atteindre la DB privée Railway. À défaut, job interne contrôlé. Tests de migration et compatibilité ancienne/nouvelle version avant release. |
| Démarrage | Gunicorn sur `0.0.0.0:$PORT`, un petit nombre de workers dimensionné sur la RAM réelle ; pas de `runserver`. Timeouts et connexions DB bornés. |
| Domaine | Générer le domaine depuis Railway, enregistrer l’hôte réellement attribué, HTTPS et origine unique. Aucun nom précis réservé ou inventé. |
| Variables non secrètes | DEBUG false, hôtes exacts, origine publique, paramètres de contact, activation explicite de collecte et transports. Aucun wildcard `*.up.railway.app` pour autoriser tous les hôtes. |
| Secrets | SECRET_KEY, DATABASE_URL privée, credentials d’envoi/anti-abus et signatures uniquement dans variables serveur, distincts par environnement. Pas de valeurs dans docs/Git. |
| Proxy/CSRF | Vérifier quels headers Railway remplace et considérer fiables uniquement ceux-là ; éviter boucle HTTPS et spoofing X-Forwarded-Proto. CSRF same-origin par défaut, origines de confiance exactes uniquement si nécessaires, tests négatifs cross-origin. |
| DB | Utiliser la connexion privée référencée au service ; vérifier absence d’exposition TCP publique, TLS selon capacités/configuration réelles. Rôle runtime sans superuser/DDL, rôle de migration séparé. Réseau privé ne prouve pas à lui seul chiffrement ou sauvegarde. |
| Statics | WhiteNoise/collectstatic, cache long pour assets versionnés, aucune réponse privée dans ce cache. Filesystem de container éphémère : pas de DB SQLite ni de dossier patient sur disque web. |
| Santé | Liveness simple sans détail, readiness vérifiant DB avec délai borné ; surveiller aussi file outbox et sauvegardes. Pas de secrets ou noms de DB dans réponse healthcheck. |
| Environnements | Test protégé, données synthétiques, collecte réelle et transports externes désactivés. DB/secret de production distincts. Autosleep et expiration crédits incompatibles avec une disponibilité supposée sans contrôle. |
| Sauvegardes | Capacité du plan/volume à vérifier ; export chiffré séparé si nécessaire, rétention et régions approuvées, exercice de restauration. Cibles proposées RPO 24 h/RTO 8 h à confirmer et financer. |

Dépendances réseau futures : registres Python, GitHub, Railway, fournisseurs de notification et leurs webhooks ; accès cloud privés et publics à qualifier sans ouvrir plus que nécessaire. Aucun credential Railway n’est requis pour terminer cette documentation.

## 9. Coûts et risques opérationnels

Les chiffres d’essai/crédit dans la documentation source (5 USD/30 jours et 1 USD mensuel) ne sont pas validés pour le compte utilisateur. Ni offre active, ni solde, ni tarification unitaire actuelle n’ont été vérifiés ici. Ne pas financer le lancement sur leur seule mention. Les précédents 80–360+ USD du montage Vercel/Supabase ne constituent pas le budget du nouveau montage.

| Poste | Budget de cadrage, USD/mois, non contractuel |
| --- | --- |
| Achat de domaine | 0 avec adresse Railway fournie ; disponibilité du domaine ≠ hébergement gratuit |
| Web + PostgreSQL + petit stockage Railway | Provision indicative 15–60+, selon mémoire/CPU et temps d’activité |
| Worker ou jobs et sauvegarde séparée | 5–25+, selon fréquence/stockage et mécanisme retenu |
| E-mail/WhatsApp Business et supervision | 0–50+ à faible volume, dépend des fournisseurs et du nombre de messages |
| Total indicatif | 20–135+ hors taxes, maintenance humaine, conseil juridique et dépassements |

Ces enveloppes sont des hypothèses de planification, pas les tarifs Railway. Calcul réel : minimum/abonnement du plan selon conditions + usage mémoire/CPU/stockage/egress + services externes, en tenant compte des crédits réellement applicables sans les compter deux fois. Préproduction simultanée, plusieurs workers ou PITR peuvent augmenter fortement l’addition. Vérifier facture estimée dans Railway, fixer budget et alerte, mesurer une préproduction synthétique avant accord de fonctionnement continu. Aucune dépense ni souscription engagée.

Risques principaux : arrêt à épuisement de crédit, consommation mémoire DB/web, disque plein, perte du stockage éphémère, absence de backup vérifié, changement de domaine/SEO, transport WhatsApp non éligible et e-mail non authentifié, temps de récupération MFA, défaut de permissions objet, fuite de santé dans logs/recherche/notifications. Prévoir propriétaire et alerte pour chacun. Les protections Django ne dispensent pas de l’analyse loi n° 2024/017, de l’autorité du proche déclarant, du choix de région et de la validation des transferts/sous-traitants.

## 10. Lots et preuves attendues après validation

| Lot | Livrable et test de sortie |
| --- | --- |
| 1 — Socle/migration vitrine | Branche applicative créée après accord, User initial, Django LTS/lockfile, templates/statics ; comparaison visuelle accueil/recrutement, SEO/liens, mobile/clavier, check Django. Vercel inchangé. |
| 2 — Base et politiques | Migrations PostgreSQL, services transactionnels, permissions ; création DB vide, montée de version, contraintes et tests de concurrence réels PostgreSQL (SQLite insuffisant). |
| 3 — Auth/MFA | Invitation, TOTP, recovery/révocation ; tentative password-only sur chaque accès privé/Admin, compte désactivé, modification de rôle, sessions anciennes et accès croisé. |
| 4 — Fiche | Sections 1–7, revue privée 8, Forms/CSRF/GPS ; POST sans JS, champs injectés, fichiers refusés, quotas multiprocessus, double soumission, DB indisponible et confirmation après commit. |
| 5 — Opérations | Filtrage/scopes, conversion unique, contact vérifié, plan/prestations ; accès direct interdit, conflit de version et historique de correction. |
| 6 — Outbox | Consommateur/transports configurables ; panne avant/après acceptation, redémarrage, bail expiré, retry, webhook forgé/rejoué, aucune fausse livraison. Captures uniquement. |
| 7 — Railway test | URL réelle et services isolés après accord budget ; check --deploy, TLS/proxy/hôtes/CSRF, static, readiness, sauvegarde restaurée et purge/retrait des accès. |
| 8 — Recette et bascule | Accord juridique/technique/financier, validation visuelle avec source, plan de rollback et monitoring ; production sur accord distinct, retrait Vercel sur autre accord. |

Contrôles de cette revue : références Git, lecture des cinq docs, diff limité aux documents, inventaire local de la fiche et inspection du monogramme. Les tests Django, PostgreSQL, MFA et Railway ci-dessus **ne sont pas exécutés**, puisque l’application n’existe pas encore. Les tests Chromium de l’audit précédent ne prouvent pas le fonctionnement d’une future migration.

## 11. Décisions et dépendances avant la suite

**Avant préparation applicative :** accord sur cette conception détaillée (User e-mail initial, MFA TOTP proposé, permissions objet, schéma/transactions et maintien de la vitrine). Les versions exactes des packages seront vérifiées dans ce lot avant verrouillage ; une incompatibilité impose un ajustement documenté, pas un MFA affaibli.

**Avant implémentation de la fiche :** arbitrer nécessité sexe/âge/traitements, services effectivement offerts et champs requis ; rendre la fiche originale disponible comme fichier pour recette reproductible. La conception des modèles peut avancer sur champs approuvés en attendant la recette graphique.

**Avant préproduction Railway :** accès au projet, région/plan/solde réel, plafond budgétaire et autorisation de provisionnement. Choix de transport e-mail/WhatsApp nécessaire pour envois effectifs ; le socle peut être testé avec transports désactivés.

**Avant collecte réelle :** validation juridique locale (données de santé, proches, droits/conservation et transferts), MFA/permissions/anti-abus testés, procédures de reprise et restauration, budget durable, destinataires autorisés et feu vert explicite de production. Aucune obligation légale précise, dispense ou durée réglementaire n’est réputée acquise par ce rapport.

Références de qualification à consulter au début de la préparation : documentation Django 5.2, django-two-factor-auth/django-otp, Railway (plans, free trial, réseau privé, domaines, volumes/sauvegardes). Les montants et compatibilités non consultés en ligne pendant cette revue restent des vérifications ouvertes.
