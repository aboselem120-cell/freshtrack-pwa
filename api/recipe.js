// Vercel Serverless Function — suggests a quick recipe using items that are
// expiring soon. Text-only call to Gemini (no image), same free-tier key.

import { isRateLimited, clientIp } from './_rateLimit.js';

const RATE_LIMIT = 20; // requests per IP per hour
const RATE_WINDOW_MS = 60 * 60 * 1000;

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const ip = clientIp(req);
  if (isRateLimited(ip, RATE_LIMIT, RATE_WINDOW_MS)) {
    console.warn(`[recipe] rate limit hit for ${ip}`);
    res.status(429).json({ error: 'Too many requests. Please try again later.', code: 'rate_limited' });
    return;
  }

  if (!process.env.GEMINI_API_KEY) {
    res.status(500).json({
      error: 'Server is missing GEMINI_API_KEY. Add it in your Vercel project settings under Environment Variables, then redeploy.'
    });
    return;
  }

  const { items, language } = req.body || {};
  if (!Array.isArray(items) || items.length === 0) {
    res.status(400).json({ error: 'Missing "items" (array of item names)' });
    return;
  }

  const langName = { en: 'English', ar: 'Arabic', es: 'Spanish' }[language] || 'English';

  const prompt = `These grocery items are about to expire: ${items.join(', ')}.
Suggest ONE simple, quick recipe that uses as many of them as possible (extra common pantry staples like salt, oil, water are fine to assume).
Respond in ${langName}.
Respond with ONLY valid JSON, no markdown fences, no commentary, in exactly this shape:
{"title":"...","steps":["...","...","..."]}
Keep it to 4-6 short steps.`;

  try {
    const model = 'gemini-3.6-flash';
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${process.env.GEMINI_API_KEY}`;

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ role: 'user', parts: [{ text: prompt }] }],
        generationConfig: { response_mime_type: 'application/json' },
      }),
    });

    if (!response.ok) {
      const errText = await response.text();
      res.status(response.status).json({ error: `Gemini API error: ${errText}` });
      return;
    }

    const data = await response.json();
    const text = data?.candidates?.[0]?.content?.parts?.[0]?.text || '';
    res.status(200).json({ text });
  } catch (err) {
    res.status(500).json({ error: String(err) });
  }
}
