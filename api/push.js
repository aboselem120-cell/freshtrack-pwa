// Push subscription upkeep for the signed-in user, called from the app.
//   action "claim": this device's endpoint now belongs to this account only —
//     removes copies stored under other accounts (one phone signed into two
//     accounts got every reminder twice).
//   action "test": claim, then send a test push to all of the user's devices
//     and return what the push service answered for each one.

import { createClient } from '@supabase/supabase-js';
import { isRateLimited, clientIp } from './_rateLimit.js';
import { configurePush, sendToUser } from './_push.js';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }
  if (isRateLimited(clientIp(req), 30, 60 * 60 * 1000)) {
    res.status(429).json({ error: 'Too many requests' });
    return;
  }
  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_ROLE_KEY) {
    res.status(500).json({ error: 'Missing SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY' });
    return;
  }

  const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY, {
    auth: { persistSession: false },
  });
  const token = (req.headers.authorization || '').replace(/^Bearer /, '');
  const { data: userData, error: authError } = await supabase.auth.getUser(token);
  if (authError || !userData?.user) {
    res.status(401).json({ error: 'Not signed in' });
    return;
  }
  const userId = userData.user.id;

  const { action, endpoint } = req.body || {};
  if (typeof endpoint === 'string' && endpoint.startsWith('https://')) {
    await supabase.from('push_subscriptions').delete().eq('endpoint', endpoint).neq('user_id', userId);
  }

  if (action !== 'test') {
    res.status(200).json({ ok: true });
    return;
  }
  if (!configurePush()) {
    res.status(500).json({ error: 'Missing VAPID_PUBLIC_KEY / VAPID_PRIVATE_KEY' });
    return;
  }
  try {
    const results = await sendToUser(supabase, userId, JSON.stringify({ title: 'FreshTrack', test: true }));
    console.log('[push test]', userId, JSON.stringify(results));
    res.status(200).json({ results });
  } catch (err) {
    res.status(500).json({ error: String(err.message || err) });
  }
}
