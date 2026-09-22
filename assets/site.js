(() => {
  const menuToggle = document.querySelector('[data-menu-toggle]');
  const mobileMenu = document.querySelector('[data-mobile-menu]');
  const whatsappFloat = document.querySelector('[data-whatsapp-float]');
  const footer = document.querySelector('[data-footer]');
  const contactSection = document.getElementById('contact');
  const form = document.getElementById('contactForm');
  const errorMessage = document.querySelector('[data-form-error]');

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
  const updateFloat = () => {
    if (!whatsappFloat) return;
    const scrolledEnough = window.scrollY > 420;
    whatsappFloat.classList.toggle('is-visible', scrolledEnough && !blockedBySection);
  };

  window.addEventListener('scroll', updateFloat, { passive: true });
  updateFloat();

  if ('IntersectionObserver' in window && whatsappFloat) {
    const observer = new IntersectionObserver((entries) => {
      blockedBySection = entries.some((entry) => entry.isIntersecting);
      updateFloat();
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.05 });

    if (contactSection) observer.observe(contactSection);
    if (footer) observer.observe(footer);
  }

  form?.addEventListener('submit', (event) => {
    event.preventDefault();

    if (!form.checkValidity()) {
      errorMessage.hidden = false;
      form.reportValidity();
      return;
    }

    errorMessage.hidden = true;
    const data = new FormData(form);
    const message = [
      'Bonjour NAKRE Care,',
      '',
      'Je souhaite vous présenter mon besoin.',
      `Nom : ${data.get('name')}`,
      `Téléphone : ${data.get('phone')}`,
      `Besoin : ${data.get('need')}`,
      `Situation : ${data.get('message')}`
    ].join('\n');

    const url = `https://wa.me/237674134365?text=${encodeURIComponent(message)}`;
    window.open(url, '_blank', 'noopener,noreferrer');
  });

  const year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
})();
