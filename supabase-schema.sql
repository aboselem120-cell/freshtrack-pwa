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
-- `endpoint` is derived from the subscription payload and kept unique so that
-- re-subscribing the same browser/device (e.g. toggling notifications off and
-- back on) updates the existing row instead of inserting a duplicate.
create table push_subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade not null,
  subscription jsonb not null,
  endpoint text generated always as (subscription->>'endpoint') stored unique,
  created_at timestamptz default now()
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
-- Step 2 — remove duplicate rows that share the same endpoint, keeping only
-- the most recently created row for each one (run this BEFORE step 3; skip
-- it if you know there are no duplicates):
-- delete from push_subscriptions a
--   using push_subscriptions b
--   where a.endpoint = b.endpoint
--     and a.created_at < b.created_at;
--
-- Step 3 — now that endpoints are unique, add the constraint:
-- alter table push_subscriptions add constraint push_subscriptions_endpoint_key unique (endpoint);

-- Track which day we last notified each user, so the daily cron doesn't spam.
create table notification_log (
  user_id uuid references auth.users(id) on delete cascade primary key,
  last_notified_date date
);

alter table notification_log enable row level security;

create policy "Service role only"
  on notification_log for all
  using (false);
