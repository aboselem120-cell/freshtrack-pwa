// Best-effort usage-event logger for our serverless functions (see the
// `events` table in supabase-schema.sql). Writes with the service role key,
// so server-only events (scan, recipe) can't be forged from the browser.
//
// Logging must never break or noticeably slow the real request: every
// failure is swallowed, and the insert is capped by a short timeout.

import { createHash } from 'node:crypto';
import { createClient } from '@supabase/supabase-js';
import { clientIp } from './_rateLimit.js';

const LOG_TIMEOUT_MS = 1500;
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

let supabase = null;
function client() {
  if (!supabase && process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_ROLE_KEY) {
    supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY, {
      auth: { persistSession: false },
    });
  }
  return supabase;
}

// Salted so the stored value can't be matched back to an IP by hashing
// candidate addresses. Reuses the service role key as the salt (already a
// server-only secret) to avoid adding another env var.
function ipHash(req) {
  const salt = process.env.SUPABASE_SERVICE_ROLE_KEY || '';
  return createHash('sha256').update(salt + clientIp(req)).digest('hex').slice(0, 32);
}

export async function logEvent(req, event, props = {}) {
  try {
    const sb = client();
    if (!sb) return;
    const deviceId = req.headers['x-device-id'];
    const insert = sb.from('events').insert({
      event,
      device_id: UUID_RE.test(deviceId || '') ? deviceId : null,
      ip_hash: ipHash(req),
      is_owner: req.headers['x-owner'] === '1',
      props,
    });
    const timeout = new Promise((resolve) => setTimeout(resolve, LOG_TIMEOUT_MS));
    const result = await Promise.race([insert, timeout]);
    if (result && result.error) console.warn(`[events] insert failed: ${result.error.message}`);
  } catch (err) {
    console.warn('[events] insert failed', err);
  }
}
