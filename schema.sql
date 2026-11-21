-- WorshipKeys community schema for Supabase PostgreSQL.
create extension if not exists pgcrypto;

create table if not exists public.songs (
  id uuid primary key default gen_random_uuid(),
  title text not null check (char_length(title) between 1 and 200),
  song_key text,
  transpose integer not null default 0 check (transpose between -12 and 12),
  tempo_feel text not null default 'Medium' check (tempo_feel in ('Low / Slow','Medium','High / Fast','Custom')),
  bpm integer check (bpm is null or bpm between 30 and 300),
  beat text,
  style text,
  category text,
  lyrics text not null,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.ideas (
  id uuid primary key default gen_random_uuid(),
  body text not null check (char_length(body) between 1 and 3000),
  user_id uuid not null references auth.users(id) on delete cascade,
  user_email text not null,
  user_name text,
  created_at timestamptz not null default now()
);

create table if not exists public.idea_comments (
  id uuid primary key default gen_random_uuid(),
  idea_id uuid not null references public.ideas(id) on delete cascade,
  body text not null check (char_length(body) between 1 and 1000),
  user_id uuid not null references auth.users(id) on delete cascade,
  user_email text not null,
  user_name text,
  created_at timestamptz not null default now()
);

create table if not exists public.idea_likes (
  idea_id uuid not null references public.ideas(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (idea_id, user_id)
);

create index if not exists ideas_created_at_idx on public.ideas(created_at desc);
create index if not exists ideas_user_id_idx on public.ideas(user_id);
create index if not exists idea_comments_idea_id_idx on public.idea_comments(idea_id, created_at);
create index if not exists idea_comments_user_id_idx on public.idea_comments(user_id);
create index if not exists idea_likes_idea_id_idx on public.idea_likes(idea_id);
create index if not exists idea_likes_user_id_idx on public.idea_likes(user_id);

alter table public.songs enable row level security;
alter table public.ideas enable row level security;
alter table public.idea_comments enable row level security;
alter table public.idea_likes enable row level security;

-- Admin song permissions are checked in Postgres, not only in the UI.
drop policy if exists "Signed-in users can read songs" on public.songs;
drop policy if exists "Only WorshipKeys admin can insert songs" on public.songs;
drop policy if exists "Only WorshipKeys admin can update songs" on public.songs;
drop policy if exists "Only WorshipKeys admin can delete songs" on public.songs;
create policy "Signed-in users can read songs" on public.songs for select to authenticated using (true);
create policy "Only WorshipKeys admin can insert songs" on public.songs for insert to authenticated
  with check (lower(coalesce((select auth.jwt())->>'email','')) = 'happyjordanpaul777@gmail.com');
create policy "Only WorshipKeys admin can update songs" on public.songs for update to authenticated
  using (lower(coalesce((select auth.jwt())->>'email','')) = 'happyjordanpaul777@gmail.com')
  with check (lower(coalesce((select auth.jwt())->>'email','')) = 'happyjordanpaul777@gmail.com');
create policy "Only WorshipKeys admin can delete songs" on public.songs for delete to authenticated
  using (lower(coalesce((select auth.jwt())->>'email','')) = 'happyjordanpaul777@gmail.com');

-- Signed-in members can read ideas and comment threads; inserts must be their own identity.
drop policy if exists "Signed-in users can read ideas" on public.ideas;
drop policy if exists "Members can post ideas as themselves" on public.ideas;
create policy "Signed-in users can read ideas" on public.ideas for select to authenticated using (true);
create policy "Members can post ideas as themselves" on public.ideas for insert to authenticated
  with check (user_id = (select auth.uid()) and lower(user_email) = lower(coalesce((select auth.jwt())->>'email','')));

drop policy if exists "Signed-in users can read comments" on public.idea_comments;
drop policy if exists "Members can comment as themselves" on public.idea_comments;
create policy "Signed-in users can read comments" on public.idea_comments for select to authenticated using (true);
create policy "Members can comment as themselves" on public.idea_comments for insert to authenticated
  with check (user_id = (select auth.uid()) and lower(user_email) = lower(coalesce((select auth.jwt())->>'email','')));

drop policy if exists "Members can read idea likes" on public.idea_likes;
drop policy if exists "Members can like once" on public.idea_likes;
drop policy if exists "Members can unlike own like" on public.idea_likes;
create policy "Members can read idea likes" on public.idea_likes for select to authenticated using (true);
create policy "Members can like once" on public.idea_likes for insert to authenticated with check (user_id = (select auth.uid()));
create policy "Members can unlike own like" on public.idea_likes for delete to authenticated using (user_id = (select auth.uid()));

-- Counts are computed from per-user likes; one member can like each idea only once.
create or replace view public.ideas_with_counts with (security_invoker = true) as
select i.id, i.body, i.user_id, i.user_email, i.user_name, i.created_at,
       count(l.user_id)::integer as like_count
from public.ideas i left join public.idea_likes l on l.idea_id = i.id
group by i.id;

grant usage on schema public to authenticated;
grant select, insert, update, delete on public.songs to authenticated;
grant select, insert on public.ideas to authenticated;
grant select, insert on public.idea_comments to authenticated;
grant select, insert, delete on public.idea_likes to authenticated;
grant select on public.ideas_with_counts to authenticated;

-- The Dashboard's automatic-RLS option may install this event-trigger function.
-- It is not part of the app API and must not be callable by browser roles.
revoke all on function public.rls_auto_enable() from public;
revoke all on function public.rls_auto_enable() from anon;
revoke all on function public.rls_auto_enable() from authenticated;
