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
create table push_subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade not null,
  subscription jsonb not null,
  created_at timestamptz default now()
);

alter table push_subscriptions enable row level security;

create policy "Users manage their own push subscriptions"
  on push_subscriptions for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- Track which day we last notified each user, so the daily cron doesn't spam.
create table notification_log (
  user_id uuid references auth.users(id) on delete cascade primary key,
  last_notified_date date
);

alter table notification_log enable row level security;

create policy "Service role only"
  on notification_log for all
  using (false);
