# Lot 2 : modèles PostgreSQL, intégrité et politiques d’accès

Le socle Django ne disposait pas encore de données métier ni d’autorisation par dossier. Ce lot ajoute les demandes, consentements, évaluations, dossiers, contacts vérifiés, plans et interventions, ainsi qu’un journal minimal et une outbox strictement bloquée. Les services transactionnels et les politiques par permission/affectation seront réutilisables par les futures vues et Django Admin.

Une acceptation et son dossier sont liés par transaction, unicité et contraintes PostgreSQL différées. Les écritures concurrentes utilisent verrous et versions ; les historiques sont protégés contre UPDATE/DELETE. Aucun accès privé, formulaire public, MFA fonctionnel, transport de notification ou déploiement n’est activé dans ce lot.

Validation : 35 tests sur PostgreSQL réel, dont les neuf non-régressions Lot 1, trois scénarios à connexions concurrentes et un aller/retour des migrations. Aucun compte applicatif ni demande conservés en développement ; trois services confirmés seulement dans le catalogue. Rapport et diagramme : docs/LOT2_EXECUTION.md.

Base proposée : feat/django-foundation-lot1. À garder en brouillon pour revue, sans fusion automatique. Les avertissements HSTS préexistants restent documentés ; sécurité de session/MFA, collecte et exploitation Railway restent soumis aux lots et validations ultérieurs.
