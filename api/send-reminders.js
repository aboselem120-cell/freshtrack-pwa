// Vercel Cron Function — runs daily (see vercel.json), checks every signed-in
// user's items for anything expiring within 3 days, and sends a real push
// notification via their stored subscription(s). This runs entirely on the
// server, so it works even if every user's phone has the app fully closed.

import { createClient } from '@supabase/supabase-js';
import { configurePush, sendToUser } from './_push.js';

export default async function handler(req, res) {
  // Only Vercel Cron may trigger this: it sends "Authorization: Bearer <CRON_SECRET>"
  // automatically when that env var is set. Without this check anyone could hit
  // the URL and push notifications to every user (and burn the day's one reminder).
  if (!process.env.CRON_SECRET) {
    res.status(500).json({ error: 'Missing CRON_SECRET' });
    return;
  }
  if (req.headers.authorization !== `Bearer ${process.env.CRON_SECRET}`) {
    res.status(401).json({ error: 'Unauthorized' });
    return;
  }

  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_ROLE_KEY) {
    res.status(500).json({ error: 'Missing SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY' });
    return;
  }
  if (!configurePush()) {
    res.status(500).json({ error: 'Missing VAPID_PUBLIC_KEY / VAPID_PRIVATE_KEY' });
    return;
  }

  const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY);

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const cutoff = new Date(today);
  cutoff.setDate(cutoff.getDate() + 3);

  const { data: items, error: itemsError } = await supabase
    .from('items')
    .select('user_id, name, expiry_date')
    .lte('expiry_date', cutoff.toISOString());

  if (itemsError) {
    res.status(500).json({ error: itemsError.message });
    return;
  }

  const byUser = {};
  (items || []).forEach((it) => {
    if (!byUser[it.user_id]) byUser[it.user_id] = [];
    byUser[it.user_id].push(it);
  });

  const todayStr = today.toISOString().slice(0, 10);
  let sent = 0;
  const failures = [];

  for (const userId of Object.keys(byUser)) {
    const { data: log } = await supabase
      .from('notification_log')
      .select('last_notified_date')
      .eq('user_id', userId)
      .maybeSingle();

    if (log && log.last_notified_date === todayStr) continue;

    const count = byUser[userId].length;
    // `count` lets the service worker word the notification in the app's
    // language; `body` stays as the English fallback for older workers.
    const payload = JSON.stringify({
      title: 'FreshTrack',
      count,
      body: `${count} item${count > 1 ? 's' : ''} expiring soon — check FreshTrack`,
    });

    const results = await sendToUser(supabase, userId, payload);
    const ok = results.filter((r) => r.ok).length;
    sent += ok;
    results.filter((r) => !r.ok).forEach((r) => failures.push({ userId, ...r }));
    if (results.length) console.log('[send-reminders]', userId, JSON.stringify(results));

    // Only mark the day as done once a push actually got through — the log
    // used to be written even when every send failed, so a broken send looked
    // like a delivered one.
    if (ok > 0) {
      await supabase
        .from('notification_log')
        .upsert({ user_id: userId, last_notified_date: todayStr });
    }
  }

  res.status(200).json({ usersChecked: Object.keys(byUser).length, notificationsSent: sent, failures });
}
