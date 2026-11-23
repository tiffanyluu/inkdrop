-- migrate:up
alter table notifications add column emailed_datetime timestamptz;

-- migrate:down
alter table notifications drop column emailed_datetime;

