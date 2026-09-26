const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status,
  headers: {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
  },
});

const clean = (value) => typeof value === 'string' ? value.trim() : '';

const allowedOrigins = new Set([
  'https://yamanciozerhukuk.com',
  'https://www.yamanciozerhukuk.com',
]);

async function verifyTurnstile(token, secret, ip) {
  const form = new FormData();
  form.append('secret', secret);
  form.append('response', token);
  if (ip) form.append('remoteip', ip);
  form.append('idempotency_key', crypto.randomUUID());

  const response = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
    method: 'POST',
    body: form,
  });
  if (!response.ok) return false;
  const result = await response.json();
  return result.success === true;
}

async function sendContactEmail(data, env) {
  const lines = [
    'Web sitesinden yeni iletişim talebi',
    '',
    `Ad soyad: ${data.name}`,
    `Telefon: ${data.phone}`,
    `E-posta: ${data.email || 'Belirtilmedi'}`,
    '',
    'Mesaj:',
    data.message,
  ];

  const payload = {
    from: env.CONTACT_FROM_EMAIL,
    to: [env.CONTACT_TO_EMAIL],
    subject: `Web sitesi iletişim formu — ${data.name}`,
    text: lines.join('\n'),
  };
  if (data.email) payload.reply_to = data.email;

  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  return response.ok;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname !== '/api/contact') return env.ASSETS.fetch(request);
    if (request.method !== 'POST') return json({ message: 'Bu yöntem desteklenmiyor.' }, 405);

    const origin = request.headers.get('Origin');
    if (origin && !allowedOrigins.has(origin)) return json({ message: 'Geçersiz istek.' }, 403);
    if (!request.headers.get('Content-Type')?.toLowerCase().startsWith('application/json')) {
      return json({ message: 'Geçersiz istek biçimi.' }, 415);
    }
    if (!env.RESEND_API_KEY || !env.TURNSTILE_SECRET_KEY) {
      return json({ message: 'İletişim formu henüz kullanıma hazır değil.' }, 503);
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return json({ message: 'Form bilgileri okunamadı.' }, 400);
    }

    const data = {
      name: clean(body.name),
      phone: clean(body.phone),
      email: clean(body.email),
      message: clean(body.message),
      website: clean(body.website),
      consent: body.consent === true,
      turnstileToken: clean(body.turnstileToken),
    };
    const phoneDigits = data.phone.replace(/\D/g, '');
    const emailValid = !data.email || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email);

    if (data.website) return json({ message: 'Mesajınız alınamadı.' }, 400);
    if (data.name.length < 2 || data.name.length > 100) return json({ message: 'Lütfen ad soyad bilginizi kontrol edin.' }, 400);
    if (phoneDigits.length < 10 || phoneDigits.length > 15) return json({ message: 'Lütfen geçerli bir telefon numarası girin.' }, 400);
    if (!emailValid || data.email.length > 254) return json({ message: 'Lütfen e-posta adresinizi kontrol edin.' }, 400);
    if (data.message.length < 10 || data.message.length > 3000) return json({ message: 'Mesajınız 10–3000 karakter arasında olmalıdır.' }, 400);
    if (!data.consent) return json({ message: 'Devam etmek için bilgi işleme onayını vermelisiniz.' }, 400);
    if (!data.turnstileToken) return json({ message: 'Lütfen güvenlik doğrulamasını tamamlayın.' }, 400);

    const verified = await verifyTurnstile(
      data.turnstileToken,
      env.TURNSTILE_SECRET_KEY,
      request.headers.get('CF-Connecting-IP'),
    );
    if (!verified) return json({ message: 'Güvenlik doğrulaması başarısız oldu. Lütfen tekrar deneyin.' }, 400);

    const sent = await sendContactEmail(data, env);
    if (!sent) return json({ message: 'Mesaj şu anda gönderilemedi. Lütfen telefon veya e-posta ile bize ulaşın.' }, 502);
    return json({ ok: true });
  },
};
