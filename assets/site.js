
const navToggle = document.querySelector('.nav-toggle');
const nav = document.querySelector('.nav');
navToggle?.addEventListener('click',()=>nav.classList.toggle('open'));
document.querySelectorAll('.nav a').forEach(link=>link.addEventListener('click',()=>nav.classList.remove('open')));
const form = document.getElementById('contactForm');
form?.addEventListener('submit', (e) => {
  e.preventDefault();
  const data = new FormData(form);
  const lines = [
    'Bonjour NAKRE Care,',
    '',
    'Je souhaite vous présenter mon besoin :',
    `Nom : ${data.get('name') || '-'}`,
    `Téléphone : ${data.get('phone') || '-'}`,
    `Type de besoin : ${data.get('need') || '-'}`,
    `Moment souhaité : ${data.get('timing') || '-'}`,
    `Message : ${data.get('message') || '-'}`,
  ];
  window.open('https://wa.me/237674134365?text=' + encodeURIComponent(lines.join('
')), '_blank', 'noopener');
});
document.getElementById('year').textContent = new Date().getFullYear();
