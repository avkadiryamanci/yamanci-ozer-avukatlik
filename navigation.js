(() => {
  const links = [...document.querySelectorAll('nav a')];
  function sync() {
    if (location.pathname !== '/' && location.pathname !== '/index.html') return;
    links.forEach(link => {
      const target = new URL(link.href, location.href);
      if (location.hash && target.hash === location.hash) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }
  window.addEventListener('hashchange', sync);
  sync();
})();
