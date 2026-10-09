// Vercel Serverless Function — suggests a quick recipe using items that are
// expiring soon. Text-only call to Gemini (no image), same free-tier key.

import { isRateLimited, clientIp } from './_rateLimit.js';
import { logEvent } from './_events.js';

const RATE_LIMIT = 20; // requests per IP per hour
const RATE_WINDOW_MS = 60 * 60 * 1000;

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  // Every outcome below is recorded as one `recipe` usage event (see _events.js).
  const startedAt = Date.now();
  const send = async (status, payload) => {
    await logEvent(req, 'recipe', {
      ok: status === 200,
      status,
      code: payload.code || null,
      ms: Date.now() - startedAt,
    });
    res.status(status).json(payload);
  };

  const ip = clientIp(req);
  if (isRateLimited(ip, RATE_LIMIT, RATE_WINDOW_MS)) {
    console.warn(`[recipe] rate limit hit for ${ip}`);
    await send(429, { error: 'Too many requests. Please try again later.', code: 'rate_limited' });
    return;
  }

  if (!process.env.GEMINI_API_KEY) {
    await send(500, {
      error: 'Server is missing GEMINI_API_KEY. Add it in your Vercel project settings under Environment Variables, then redeploy.'
    });
    return;
  }

  const { items, language } = req.body || {};
  if (!Array.isArray(items) || items.length === 0) {
    await send(400, { error: 'Missing "items" (array of item names)' });
    return;
  }

  // Bound the prompt: at most 30 short item names (the client sends names of
  // items expiring within 3 days; anything beyond this is not a real fridge).
  const names = items.filter((n) => typeof n === 'string').slice(0, 30).map((n) => n.slice(0, 60));
  if (names.length === 0) {
    await send(400, { error: 'Missing "items" (array of item names)' });
    return;
  }

  const langName = { en: 'English', ar: 'Arabic', es: 'Spanish' }[language] || 'English';

  const prompt = `These grocery items are about to expire: ${names.join(', ')}.
Suggest ONE simple, quick recipe that uses as many of them as possible (extra common pantry staples like salt, oil, water are fine to assume).
Respond in ${langName}.
Respond with ONLY valid JSON, no markdown fences, no commentary, in exactly this shape:
{"title":"...","steps":["...","...","..."]}
Keep it to 4-6 short steps.`;

  try {
    // Gemini often answers 503 ("model overloaded") or hangs; with no retry
    // every recipe request failed during those spells. Retry once, then fall
    // back to Groq (text-only, so any of its chat models will do).
    const gemini = await recipeWithGemini(prompt);
    if (gemini.text) {
      await send(200, { text: gemini.text });
      return;
    }

    if (gemini.retryable && process.env.GROQ_API_KEY) {
      console.warn(`[recipe] Gemini failed (${gemini.status || 'timeout'}); trying Groq fallback`);
      const groqText = await recipeWithGroq(prompt).catch((err) => {
        console.error('[recipe] Groq fallback failed', err);
        return null;
      });
      if (groqText) {
        await send(200, { text: groqText });
        return;
      }
    }

    if (gemini.retryable) {
      await send(gemini.status || 504, { error: 'The recipe service is busy. Please try again in a minute.', code: 'busy' });
      return;
    }
    await send(gemini.status || 502, { error: `Gemini API error: ${gemini.error}`, code: 'gemini_error' });
  } catch (err) {
    await send(500, { error: String(err), code: 'server_error' });
  }
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function fetchWithTimeout(url, options, ms) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), ms);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(timeoutId);
  }
}

// Returns { text } on success, otherwise { status, error, retryable }.
async function recipeWithGemini(prompt) {
  const model = 'gemini-3.6-flash';
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${process.env.GEMINI_API_KEY}`;
  const body = JSON.stringify({
    contents: [{ role: 'user', parts: [{ text: prompt }] }],
    generationConfig: { response_mime_type: 'application/json' },
  });

  const MAX_ATTEMPTS = 2;
  let last = { status: null, error: 'no response', retryable: true };
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    let response;
    try {
      response = await fetchWithTimeout(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body }, 15000);
    } catch (err) {
      if (err.name !== 'AbortError') throw err;
      last = { status: null, error: 'timeout', retryable: true };
      if (attempt < MAX_ATTEMPTS) await sleep(1000);
      continue;
    }

    if (response.ok) {
      const data = await response.json();
      const text = data?.candidates?.[0]?.content?.parts?.[0]?.text || '';
      if (text) return { text };
      return { status: 502, error: 'empty response', retryable: true };
    }

    const errText = await response.text();
    // 429 is a per-minute quota: retrying Gemini right away won't help.
    last = { status: response.status, error: errText, retryable: response.status === 503 || response.status === 429 };
    if (response.status !== 503) break;
    if (attempt < MAX_ATTEMPTS) await sleep(1000);
  }
  return last;
}

const GROQ_TEXT_MODEL_PREFERENCE = ['openai/gpt-oss-120b', 'openai/gpt-oss-20b', 'qwen/qwen3.8-27b'];

async function recipeWithGroq(prompt) {
  const headers = { 'Content-Type': 'application/json', Authorization: `Bearer ${process.env.GROQ_API_KEY}` };

  const modelsRes = await fetchWithTimeout('https://api.groq.com/openai/v1/models', { headers }, 8000);
  if (!modelsRes.ok) return null;
  const available = new Set(((await modelsRes.json()).data || []).filter((m) => m.active !== false).map((m) => m.id));
  const model = GROQ_TEXT_MODEL_PREFERENCE.find((id) => available.has(id));
  if (!model) return null;

  const res = await fetchWithTimeout('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers,
    body: JSON.stringify({
      model,
      messages: [{ role: 'user', content: prompt }],
      response_format: { type: 'json_object' },
    }),
  }, 20000);
  if (!res.ok) throw new Error(`Groq API error ${res.status}: ${await res.text()}`);
  const data = await res.json();
  return data?.choices?.[0]?.message?.content || null;
}
