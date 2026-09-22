# Audit UX/UI et technique — NAKRE Care

## Architecture identifiée

Le projet existant est un site statique sans framework :

- HTML : `index.html`
- CSS global : `assets/styles.css`
- JavaScript léger : `assets/site.js`
- Assets locaux PNG/SVG
- Déploiement compatible Vercel sans étape de build

Cette architecture a été conservée afin d’éviter une migration technologique inutile.

## Principaux constats avant refonte

### UX / direction artistique

- Hero trop chargé : badges, quatre mini-cartes, plusieurs visuels et plusieurs niveaux de CTA en concurrence.
- Usage excessif de cartes, bordures arrondies, fonds alternés et ombres.
- Affiches sociales utilisées comme éléments de structure web, ce qui donnait un effet “catalogue de posts Facebook”.
- Recrutement mélangé à la présentation des services.
- Galerie “Visuels de la marque” sans utilité pour le parcours client.
- Répétitions éditoriales entre le hero, les services, les blocs de confiance et les CTA.
- Texte technique visible dans l’interface (“le site est statique…”, explications sur l’intégration des visuels).

### Navigation / CTA

- Header surchargé avec des entrées qui ne sont pas nécessaires au parcours principal.
- Trop de sollicitations WhatsApp à différents endroits.
- Bouton WhatsApp flottant visible en permanence avec un z-index élevé et sans logique d’évitement du contact/footer.

### Responsive

- Les grilles basculaient correctement sur mobile, mais la densité et l’empilement créaient une page très longue.
- Le bouton flottant n’avait pas de gestion `safe-area`.
- Le menu mobile fonctionnait par simple affichage/masquage, sans gestion Escape, fermeture au redimensionnement ou blocage du scroll.

### Accessibilité

- Pas de lien d’évitement vers le contenu.
- Focus clavier non explicitement stylé.
- Le bouton de menu ne mettait pas à jour `aria-expanded`.
- Hiérarchie générale exploitable, mais plusieurs éléments décoratifs étaient exposés comme contenu.
- Les zones tactiles et états focus n’étaient pas systématiquement définis.

### SEO

- Title, description et Open Graph présents mais incomplets.
- Pas de canonical.
- Pas de `robots.txt` ni de sitemap.
- Pas de données structurées.
- Image Open Graph référencée avec une URL relative.

### Performance

- Plusieurs affiches PNG pèsent environ 2,6–2,8 Mo chacune.
- Certaines images étaient répétées dans plusieurs sections.
- Les visuels sociaux étaient chargés comme contenu principal alors qu’ils ne sont pas adaptés au web.

## Corrections réalisées

### Homepage

- Hero simplifié : un message, une description, un CTA principal, un lien secondaire discret et une photographie principale.
- Ligne de contexte concise : domicile, milieu hospitalier, rendez-vous, Yaoundé.
- Nouvelle section “À qui s’adresse NAKRE Care ?”.
- Services limités aux prestations confirmées : domicile, milieu hospitalier, rendez-vous/déplacements utiles.
- Section de confiance réorganisée autour de six engagements défendables.
- Processus conservé en quatre étapes mais transformé en timeline éditoriale.
- Suppression totale de la galerie de visuels de la homepage.
- Recrutement séparé du parcours client et déplacé en fin de page.
- Création d’une page `/recrutement/`.
- Contact réorganisé avec priorité WhatsApp → téléphone → formulaire.
- Microcopy du formulaire réécrite sans commentaire technique.

### Design system

- Palette réduite autour du vert profond, blanc, ivoire, gris neutres et un accent limité.
- Suppression des gradients décoratifs, ombres omniprésentes et grands rayons de cartes.
- Typographie ramenée à une seule famille système moderne et lisible.
- Échelle d’espacement unifiée et container de 1160 px.
- H1 réduit à une taille éditoriale plus crédible.

### Images

- Les affiches originales sont conservées dans les assets, mais ne structurent plus la homepage.
- Création de crops photo optimisés en WebP pour le web : environ 59–77 Ko au lieu de plusieurs Mo.
- Chaque photographie principale est utilisée une seule fois.
- Lazy-loading appliqué aux images non critiques.

### WhatsApp flottant

- Taille : 54 px.
- `right: 16–18px` selon viewport.
- `bottom` compatible avec `env(safe-area-inset-bottom)`.
- z-index inférieur au header/menu.
- Apparition seulement après un léger scroll.
- Masquage automatique lorsque la section Contact ou le footer est visible.
- `aria-label` explicite.

### Accessibilité

- Ajout d’un skip-link.
- États `:focus-visible` explicites.
- Menu avec `aria-controls`, `aria-expanded` et fermeture Escape.
- Labels explicites pour tous les champs.
- Zones tactiles d’au moins 44–48 px sur les principaux contrôles.
- Support `prefers-reduced-motion`.
- HTML sémantique et un seul H1 sur la homepage.

### SEO

- Canonical.
- Open Graph avec URL absolue et image 1200×630.
- Twitter card.
- `robots.txt`.
- `sitemap.xml`.
- Données structurées `Organization` limitées aux informations réellement connues.

## Contrôle final

Tests responsive automatisés effectués aux largeurs :

- 320 px
- 360 px
- 375 px
- 390 px
- 414 px
- 768 px
- 1024 px
- 1280 px
- 1440 px

Résultats :

- aucun overflow horizontal détecté ;
- aucune erreur JavaScript/console détectée dans la passe de rendu ;
- menu mobile fonctionnel ;
- bouton WhatsApp positionné hors du header et sous le z-index du menu ;
- formulaire valide avant ouverture de WhatsApp ;
- liens internes et assets locaux vérifiés ;
- un seul H1 sur la homepage ;
- aucun ID dupliqué.
