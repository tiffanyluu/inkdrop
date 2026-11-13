-- migrate:up
drop table if exists follows;

create table if not exists subscriptions (
    id bigint generated always as identity primary key,
    subscription_public_id uuid default gen_random_uuid() not null unique,
    user_row_id bigint references users(id) on delete cascade not null,
    title_row_id bigint references titles(id) on delete cascade not null,
    latest_read_chapter numeric,
    read_url text,
    latest_notified_chapter numeric,
    create_datetime timestamptz default now() not null,
    modified_datetime timestamptz,
    unique (user_row_id, title_row_id)
);

create index subscriptions_title_idx on subscriptions (title_row_id);

create trigger trigger_subscriptions_modified_datetime
before update on subscriptions
for each row
execute function set_modified_datetime();

-- migrate:down
drop table if exists subscriptions;

create table if not exists follows (
    id bigint generated always as identity primary key,
    follow_public_id uuid default gen_random_uuid() not null unique,
    user_row_id bigint references users(id) on delete cascade not null,
    title_row_id bigint references titles(id) on delete cascade not null,
    latest_read_chapter numeric,
    read_url text,
    latest_notified_chapter numeric,
    create_datetime timestamptz default now() not null,
    modified_datetime timestamptz,
    unique (user_row_id, title_row_id)
);

create index follows_title_idx on follows (title_row_id);

create trigger trigger_follows_modified_datetime
before update on follows
for each row
execute function set_modified_datetime();
