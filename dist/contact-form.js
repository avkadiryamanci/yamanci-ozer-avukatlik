(() => {
  const form = document.querySelector('#contact-form');
  if (!form) return;

  const status = document.querySelector('#contact-form-status');
  const submitButton = form.querySelector('button[type="submit"]');
  const turnstileElement = form.querySelector('.cf-turnstile');
  const siteKey = turnstileElement?.dataset.sitekey;

  if (siteKey && !siteKey.includes('PLACEHOLDER')) {
    const script = document.createElement('script');
    script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js';
    script.async = true;
    script.defer = true;
    document.head.append(script);
  }

  const setStatus = (message, state = '') => {
    status.textContent = message;
    status.dataset.state = state;
  };

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    setStatus('');

    if (!form.reportValidity()) return;

    const formData = new FormData(form);
    const turnstileToken = formData.get('cf-turnstile-response');
    if (!turnstileToken) {
      setStatus('Lütfen güvenlik doğrulamasını tamamlayın.', 'error');
      return;
    }

    submitButton.disabled = true;
    submitButton.setAttribute('aria-busy', 'true');
    setStatus('Mesajınız gönderiliyor…');

    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.get('name'),
          phone: formData.get('phone'),
          email: formData.get('email'),
          message: formData.get('message'),
          website: formData.get('website'),
          consent: formData.get('consent') === 'on',
          turnstileToken,
        }),
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(result.message || 'Mesaj gönderilemedi.');

      form.reset();
      if (window.turnstile) window.turnstile.reset();
      setStatus('Mesajınız başarıyla iletildi. En kısa sürede size dönüş yapacağız.', 'success');
    } catch (error) {
      setStatus(error.message || 'Bir sorun oluştu. Lütfen telefon veya e-posta ile bize ulaşın.', 'error');
      if (window.turnstile) window.turnstile.reset();
    } finally {
      submitButton.disabled = false;
      submitButton.removeAttribute('aria-busy');
    }
  });
})();
