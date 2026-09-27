-- Run this once in your Supabase project: SQL Editor → New Query → paste → Run

-- Items table: each row is one grocery item belonging to one signed-in user.
create table items (
  id text primary key,
  user_id uuid references auth.users(id) on delete cascade not null,
  name jsonb not null,               -- {"en":"Milk","ar":"حليب","es":"Leche"}
  category text not null,
  expiry_date timestamptz not null,
  from_label boolean default false,
  created_at timestamptz default now()
);

alter table items enable row level security;

create policy "Users manage their own items"
  on items for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- Push subscriptions: one row per device a user enabled notifications on.
-- `endpoint` is derived from the subscription payload; (user_id, endpoint) is
-- kept unique so that re-subscribing the same browser/device (e.g. toggling
-- notifications off and back on) updates the existing row instead of
-- inserting a duplicate. Scoping the uniqueness to user_id too (rather than
-- endpoint alone) lets the same device be re-subscribed under a different
-- signed-in user without a conflict.
create table push_subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade not null,
  subscription jsonb not null,
  endpoint text generated always as (subscription->>'endpoint') stored,
  created_at timestamptz default now(),
  unique (user_id, endpoint)
);

alter table push_subscriptions enable row level security;

create policy "Users manage their own push subscriptions"
  on push_subscriptions for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- Migration for a database created before the `endpoint` column existed:
-- run this block instead of the `create table` above if push_subscriptions
-- already exists.
--
-- Step 1 — add the derived column (safe to run even with existing rows):
-- alter table push_subscriptions add column endpoint text generated always as (subscription->>'endpoint') stored;
--
-- Step 2 — remove duplicate rows that share the same (user_id, endpoint),
-- keeping only the most recently created row for each pair (run this BEFORE
-- step 3; skip it if you know there are no duplicates):
-- delete from push_subscriptions a
--   using push_subscriptions b
--   where a.user_id = b.user_id
--     and a.endpoint = b.endpoint
--     and a.created_at < b.created_at;
--
-- Step 3 — now that (user_id, endpoint) pairs are unique, add the constraint:
-- alter table push_subscriptions add constraint push_subscriptions_user_endpoint_key unique (user_id, endpoint);

-- Track which day we last notified each user, so the daily cron doesn't spam.
create table notification_log (
  user_id uuid references auth.users(id) on delete cascade primary key,
  last_notified_date date
);

alter table notification_log enable row level security;

create policy "Service role only"
  on notification_log for all
  using (false);

-- Anonymous usage events, to measure real usage (daily active devices,
-- retention, scans/day, AI failure rate). No names, images, emails or raw IPs.
--   * scan / recipe are written server-side only (api/_events.js, service role),
--     with a salted IP hash so per-user volume can inform rate limits.
--   * the rest are written by the app with the anon key; clients can insert
--     but never read, and can't forge server-only events or an ip_hash.
--   * is_owner marks the owner's own devices so they can be filtered out.
create table events (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  event text not null check (event in ('app_open','scan','recipe','item_added','item_resolved','sign_in','notif_enabled')),
  device_id uuid,
  user_id uuid references auth.users(id) on delete set null,
  ip_hash text check (char_length(ip_hash) <= 64),
  is_owner boolean not null default false,
  props jsonb not null default '{}'::jsonb check (pg_column_size(props) < 2000)
);

create index events_event_created_idx on events (event, created_at);
create index events_ip_hash_created_idx on events (ip_hash, created_at) where ip_hash is not null;

alter table events enable row level security;

create policy "Clients can log usage events"
  on events for insert to anon, authenticated
  with check (
    event in ('app_open','item_added','item_resolved','sign_in','notif_enabled')
    and ip_hash is null
    and (user_id is null or user_id = auth.uid())
  );
