// Vercel Cron Function — runs daily (see vercel.json), checks every signed-in
// user's items for anything expiring within 3 days, and sends a real push
// notification via their stored subscription(s). This runs entirely on the
// server, so it works even if every user's phone has the app fully closed.

import { createClient } from '@supabase/supabase-js';
import webPush from 'web-push';

export default async function handler(req, res) {
  if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_ROLE_KEY) {
    res.status(500).json({ error: 'Missing SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY' });
    return;
  }
  if (!process.env.VAPID_PUBLIC_KEY || !process.env.VAPID_PRIVATE_KEY) {
    res.status(500).json({ error: 'Missing VAPID_PUBLIC_KEY / VAPID_PRIVATE_KEY' });
    return;
  }

  const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY);

  webPush.setVapidDetails(
    process.env.VAPID_SUBJECT || 'mailto:admin@example.com',
    process.env.VAPID_PUBLIC_KEY,
    process.env.VAPID_PRIVATE_KEY
  );

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

  for (const userId of Object.keys(byUser)) {
    const { data: log } = await supabase
      .from('notification_log')
      .select('last_notified_date')
      .eq('user_id', userId)
      .maybeSingle();

    if (log && log.last_notified_date === todayStr) continue;

    const { data: subs } = await supabase
      .from('push_subscriptions')
      .select('id, subscription')
      .eq('user_id', userId);

    if (!subs || subs.length === 0) continue;

    const count = byUser[userId].length;
    const payload = JSON.stringify({
      title: 'FreshTrack',
      body: `${count} item${count > 1 ? 's' : ''} expiring soon — check FreshTrack`,
    });

    for (const s of subs) {
      try {
        await webPush.sendNotification(s.subscription, payload);
        sent++;
      } catch (err) {
        if (err.statusCode === 410 || err.statusCode === 404) {
          await supabase.from('push_subscriptions').delete().eq('id', s.id);
        }
      }
    }

    await supabase
      .from('notification_log')
      .upsert({ user_id: userId, last_notified_date: todayStr });
  }

  res.status(200).json({ usersChecked: Object.keys(byUser).length, notificationsSent: sent });
}
