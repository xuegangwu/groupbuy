/* Solaripple Mobile JS: hamburger + PWA install */

(function() {
  var navbar = document.querySelector('.navbar');
  if (!navbar) return;

  /* --- Hamburger --- */
  var hamburger = document.createElement('button');
  hamburger.className = 'hamburger';
  hamburger.setAttribute('aria-label', 'Menu');
  hamburger.innerHTML = '<span></span><span></span><span></span>';

  var mobileNav = document.createElement('div');
  mobileNav.className = 'mobile-nav';

  var links = navbar.querySelector('.navbar-links');
  if (links) {
    var clone = links.cloneNode(true);
    Array.from(clone.querySelectorAll('a')).forEach(function(a) {
      a.style.display = 'block';
      a.style.padding = '13px 4px';
      a.style.fontSize = '16px';
    });
    mobileNav.appendChild(clone);
  }

  var langSwitch = document.createElement('div');
  langSwitch.className = 'lang-switch-mobile';
  ['langZh', 'langEn', 'langJa'].forEach(function(id) {
    var orig = document.getElementById(id);
    if (orig) {
      var btn = orig.cloneNode(true);
      btn.className = 'lang-btn' + (orig.classList.contains('active') ? ' active' : '');
      btn.addEventListener('click', function() {
        orig.click();
        document.querySelectorAll('.lang-btn').forEach(function(b) { b.classList.remove('active'); });
        btn.classList.add('active');
      });
      langSwitch.appendChild(btn);
    }
  });
  mobileNav.appendChild(langSwitch);

  navbar.appendChild(hamburger);
  document.body.appendChild(mobileNav);

  hamburger.addEventListener('click', function() {
    hamburger.classList.toggle('active');
    mobileNav.classList.toggle('open');
    document.body.style.overflow = mobileNav.classList.contains('open') ? 'hidden' : '';
  });

  mobileNav.querySelectorAll('a').forEach(function(a) {
    a.addEventListener('click', function() {
      hamburger.classList.remove('active');
      mobileNav.classList.remove('open');
      document.body.style.overflow = '';
    });
  });

  /* --- PWA Install Banner --- */
  var deferredPrompt = null;
  window.addEventListener('beforeinstallprompt', function(e) {
    e.preventDefault();
    deferredPrompt = e;
    var banner = document.querySelector('.pwa-install-banner');
    if (banner) banner.classList.add('show');
  });

  document.addEventListener('click', function(e) {
    if (e.target.closest('.pwa-install-btn')) {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then(function() { deferredPrompt = null; });
        var banner = document.querySelector('.pwa-install-banner');
        if (banner) banner.classList.remove('show');
      }
    }
    if (e.target.closest('.pwa-install-close')) {
      var banner = document.querySelector('.pwa-install-banner');
      if (banner) banner.classList.remove('show');
    }
  });

  /* --- Register Service Worker --- */
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(function() {});
  }
})();
