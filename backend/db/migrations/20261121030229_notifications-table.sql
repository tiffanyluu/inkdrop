-- migrate:up
create table if not exists notifications (
    row_id bigint generated always as identity primary key,
    notification_public_id uuid default gen_random_uuid() not null unique,
    chapter numeric not null,
    user_row_id bigint references users(row_id) on delete cascade not null,
    title_row_id bigint references titles(row_id) on delete cascade not null,
    create_datetime timestamptz default now() not null,
    seen_datetime timestamptz,
    unique (user_row_id, title_row_id, chapter)
);

-- migrate:down
drop table if exists notifications;
