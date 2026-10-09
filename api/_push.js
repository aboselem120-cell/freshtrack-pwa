// Shared Web Push sending for the daily reminder cron and the in-app test
// button. Returns one result per subscription so failures are visible
// instead of being swallowed.

import webPush from 'web-push';

let configured = false;
export function configurePush() {
  if (!process.env.VAPID_PUBLIC_KEY || !process.env.VAPID_PRIVATE_KEY) return false;
  if (!configured) {
    webPush.setVapidDetails(
      process.env.VAPID_SUBJECT || 'mailto:admin@example.com',
      process.env.VAPID_PUBLIC_KEY,
      process.env.VAPID_PRIVATE_KEY
    );
    configured = true;
  }
  return true;
}

// Sends `payload` to every stored subscription of `userId`. Subscriptions the
// push service reports as gone (404/410) are deleted.
export async function sendToUser(supabase, userId, payload) {
  const { data: subs, error } = await supabase
    .from('push_subscriptions')
    .select('id, subscription')
    .eq('user_id', userId);
  if (error) throw error;

  const results = [];
  for (const s of subs || []) {
    const host = (() => { try { return new URL(s.subscription.endpoint).host; } catch { return '?'; } })();
    try {
      const r = await webPush.sendNotification(s.subscription, payload, { TTL: 24 * 60 * 60 });
      results.push({ id: s.id, host, ok: true, status: r.statusCode });
    } catch (err) {
      const status = err.statusCode || null;
      const gone = status === 404 || status === 410;
      if (gone) await supabase.from('push_subscriptions').delete().eq('id', s.id);
      results.push({ id: s.id, host, ok: false, status, removed: gone, error: String(err.body || err.message || err).slice(0, 200) });
    }
  }
  return results;
}
