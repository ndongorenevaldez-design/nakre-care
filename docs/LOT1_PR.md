# Brouillon de PR : socle Django et migration initiale de la vitrine

Le site statique ne dispose pas de socle serveur et son ancien formulaire transmet des réponses à WhatsApp. Ce lot prépare Django 5.2 LTS/PostgreSQL et migre accueil/recrutement en templates en réutilisant les ressources existantes. Dans Django, le formulaire est remplacé par un contact générique sans collecte.

User personnalisé par e-mail et première migration, configuration locale reproductible, paramètres de production stricts, statiques WhiteNoise, apps par domaine et tests. Aucune route administrative ou médicale exposée avant mise en place du MFA et des autorisations. Les fichiers de production statique et main ne sont pas modifiés ; aucun déploiement, donnée réelle ou service payant.

Validation : migrations et tests Django sur PostgreSQL, contraintes d’unicité, accès privés refusés, CSRF/POST, check et collectstatic, réponse statique hashée en configuration production. Comparaison Chromium des deux pages à 375/1440 px : accueil identique sur le premier écran, menu mobile ajouté au recrutement. Deux avertissements HSTS (includeSubDomains/preload) restent à qualifier pour le domaine réel. Détails et commandes : docs/LOT1_EXECUTION.md.

PR à créer en brouillon, base docs/validation-django-railway-20261101, sans merge automatique. Lot 2 et Railway attendent une autorisation distincte.
