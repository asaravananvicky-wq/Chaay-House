// Chaay House — small progressive-enhancement JS.
// Forms still work without JS (full page reload); this just smooths the experience.

document.addEventListener('DOMContentLoaded', function () {
  // Auto-dismiss toast/alert messages after a few seconds
  document.querySelectorAll('.alert-dismissible').forEach(function (el) {
    setTimeout(function () {
      el.classList.add('fade');
      el.classList.remove('show');
      setTimeout(() => el.remove(), 400);
    }, 4000);
  });

  // Quantity stepper on product detail page
  const qtyInput = document.getElementById('qty-input');
  const incBtn = document.getElementById('qty-increase');
  const decBtn = document.getElementById('qty-decrease');
  if (qtyInput && incBtn && decBtn) {
    incBtn.addEventListener('click', function () {
      qtyInput.value = Math.min(99, parseInt(qtyInput.value || '1', 10) + 1);
    });
    decBtn.addEventListener('click', function () {
      qtyInput.value = Math.max(1, parseInt(qtyInput.value || '1', 10) - 1);
    });
  }

  // Confirmation dialogs for destructive actions
  document.querySelectorAll('[data-confirm]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      if (!confirm(form.getAttribute('data-confirm'))) {
        e.preventDefault();
      }
    });
  });
});
