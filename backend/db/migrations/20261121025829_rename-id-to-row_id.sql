-- migrate:up
alter table subscriptions rename column id to row_id;
alter table title_sources rename column id to row_id;
alter table titles rename column id to row_id;
alter table user_sessions rename column id to row_id;
alter table users rename column id to row_id;

-- migrate:down
alter table users rename row_id to id;
alter table user_sessions rename row_id to id;
alter table titles rename row_id to id;
alter table title_sources rename row_id to id;
alter table subscriptions rename row_id to id;
