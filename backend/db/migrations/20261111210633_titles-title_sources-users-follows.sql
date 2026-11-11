-- migrate:up
create or replace function set_modified_datetime()
returns trigger as $$
begin
    new.modified_datetime = now();
    return new;
end;
$$ language plpgsql;

create type sources_type_enum as enum ('MANGADEX', 'ATHREA_SCANS');
create type title_status_enum as enum ('ONGOING', 'COMPLETED', 'HIATUS');

-- titles table
create table if not exists titles (
    id bigint generated always as identity primary key,
    title_public_id uuid default gen_random_uuid() not null unique,
    title_name varchar(255) not null,
    image_url text,
    title_status title_status_enum not null,
    create_datetime timestamptz default now() not null,
    modified_datetime timestamptz
);

create trigger trigger_titles_modified_datetime
before update on titles
for each row
execute function set_modified_datetime();

-- title sources table
create table if not exists title_sources (
    id bigint generated always as identity primary key,
    source_id varchar(255) not null,
    title_row_id bigint references titles(id) on delete cascade not null,
    source_type sources_type_enum not null,
    latest_free_chapter numeric,
    latest_paid_chapter numeric,
    create_datetime timestamptz default now() not null,
    modified_datetime timestamptz,
    last_checked_datetime timestamptz,
    latest_free_chapter_datetime timestamptz,
    unique (source_type, source_id)
);

create index title_sources_title_idx on title_sources (title_row_id);

create trigger trigger_title_sources_modified_datetime
before update on title_sources
for each row
execute function set_modified_datetime();

-- users table
create table if not exists users (
    id bigint generated always as identity primary key,
    user_public_id uuid default gen_random_uuid() not null unique,
    first_name varchar(50) not null,
    last_name varchar(50) not null,
    email varchar(255) not null,
    password_hash varchar(255) not null,
    create_datetime timestamptz default now() not null,
    modified_datetime timestamptz
);

create unique index users_email_lower_idx ON users (lower(email));

create trigger trigger_users_modified_datetime
before update on users
for each row
execute function set_modified_datetime();

-- follows table
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

-- migrate:down
drop index if exists follows_title_idx;
drop table if exists follows;

drop table if exists users;

drop index if exists title_sources_title_idx;
drop table if exists title_sources;

drop table if exists titles;

drop type if exists title_status_enum;
drop type if exists sources_type_enum;

drop function if exists set_modified_datetime;