// Simple best-effort per-IP rate limiter for our Vercel serverless functions.
// This is an in-memory counter, so it only protects within a single warm
// function instance — it resets on cold start and isn't shared across
// concurrent instances/regions. That's an accepted tradeoff for a "just
// stop obvious abuse" limiter; a hard guarantee would need a shared store
// like Vercel KV or Upstash Redis.

const requestLog = new Map(); // ip -> array of request timestamps (ms)

export function isRateLimited(ip, limit, windowMs) {
  const now = Date.now();
  const timestamps = (requestLog.get(ip) || []).filter((t) => now - t < windowMs);
  timestamps.push(now);
  requestLog.set(ip, timestamps);
  return timestamps.length > limit;
}

export function clientIp(req) {
  const forwarded = req.headers['x-forwarded-for'];
  if (forwarded) return forwarded.split(',')[0].trim();
  return req.socket?.remoteAddress || 'unknown';
}
