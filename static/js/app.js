const menuButton = document.querySelector('[data-menu-toggle]');
const menu = document.querySelector('[data-menu]');

if (menuButton && menu) {
  menuButton.addEventListener('click', () => {
    const open = menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.setAttribute('aria-expanded', String(!open));
    menu.classList.toggle('is-open', !open);
    document.body.classList.toggle('menu-open', !open);
  });

  menu.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      menuButton.setAttribute('aria-expanded', 'false');
      menu.classList.remove('is-open');
      document.body.classList.remove('menu-open');
    });
  });
}

document.querySelectorAll('.upload-box input[type="file"]').forEach((input) => {
  input.addEventListener('change', () => {
    const box = input.closest('.upload-box');
    const label = box?.querySelector('strong');
    if (!box || !label) return;
    box.classList.toggle('has-file', input.files.length > 0);
    label.textContent = input.files[0]?.name || `照片 ${input.name.slice(-1)}`;
  });
});

const header = document.querySelector('[data-header]');
if (header) {
  const updateHeader = () => header.classList.toggle('is-sticky', window.scrollY > 120);
  window.addEventListener('scroll', updateHeader, { passive: true });
  updateHeader();
}
