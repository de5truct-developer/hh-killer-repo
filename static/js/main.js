// Flash message auto-hide
document.addEventListener('DOMContentLoaded', () => {
  const alerts = document.querySelectorAll('.alert[data-autohide]');
  alerts.forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity .4s ease, transform .4s ease';
      el.style.opacity = '0';
      el.style.transform = 'translateY(-8px)';
      setTimeout(() => el.remove(), 400);
    }, 4000);
  });

  // Skill chip toggle highlight
  document.querySelectorAll('.skills-grid input[type=checkbox]').forEach(cb => {
    const label = cb.closest('label');
    if (cb.checked) label.style.background = '#EEF2FF';
    cb.addEventListener('change', () => {
      label.style.background = cb.checked ? '#EEF2FF' : '';
    });
  });

  // Animate vacancy cards on scroll
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('fade-in');
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.vacancy-card, .card').forEach(el => observer.observe(el));

  // Confirm delete
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', e => {
      if (!confirm(el.dataset.confirm)) e.preventDefault();
    });
  });

  // Hero search redirect
  const heroForm = document.getElementById('hero-search-form');
  if (heroForm) {
    heroForm.addEventListener('submit', e => {
      e.preventDefault();
      const q = document.getElementById('hero-q').value.trim();
      if (q) window.location.href = `/vacancies/?q=${encodeURIComponent(q)}`;
      else window.location.href = '/vacancies/';
    });
  }
});
