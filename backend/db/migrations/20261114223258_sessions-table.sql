-- migrate:up
create table if not exists user_sessions (
    id bigint generated always as identity primary key,
    token_hash varchar(64) not null unique,
    user_row_id bigint not null references users(id) on delete cascade,
    create_datetime timestamptz not null default now(),
    expiration_datetime timestamptz not null
);

create index idx_user_sessions_user_row_id on user_sessions(user_row_id);
create index idx_user_sessions_expiration_datetime on user_sessions(expiration_datetime);

-- migrate:down
drop table if exists user_sessions;
