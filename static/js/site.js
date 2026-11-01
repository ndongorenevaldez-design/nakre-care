(() => {
  const menuToggle = document.querySelector('[data-menu-toggle]');
  const mobileMenu = document.querySelector('[data-mobile-menu]');
  const whatsappFloat = document.querySelector('[data-whatsapp-float]');
  const footer = document.querySelector('[data-footer]');
  const contactSection = document.getElementById('contact');

  const setMenu = (open) => {
    if (!menuToggle || !mobileMenu) return;
    menuToggle.setAttribute('aria-expanded', String(open));
    menuToggle.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
    mobileMenu.hidden = !open;
    document.body.classList.toggle('menu-open', open);
  };

  menuToggle?.addEventListener('click', () => {
    setMenu(menuToggle.getAttribute('aria-expanded') !== 'true');
  });

  mobileMenu?.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => setMenu(false));
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') setMenu(false);
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth > 980) setMenu(false);
  }, { passive: true });

  let blockedBySection = false;
  const intersecting = new Set();
  const updateFloat = () => {
    if (!whatsappFloat) return;
    const scrolledEnough = window.scrollY > 420;
    whatsappFloat.classList.toggle('is-visible', scrolledEnough && !blockedBySection);
  };

  window.addEventListener('scroll', updateFloat, { passive: true });
  updateFloat();

  if ('IntersectionObserver' in window && whatsappFloat) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => entry.isIntersecting ? intersecting.add(entry.target) : intersecting.delete(entry.target));
      blockedBySection = intersecting.size > 0;
      updateFloat();
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.05 });

    if (contactSection) observer.observe(contactSection);
    if (footer) observer.observe(footer);
  }

  const year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
})();
