-- migrate:up
alter table titles add column description text;

-- migrate:down
alter table titles drop column description;