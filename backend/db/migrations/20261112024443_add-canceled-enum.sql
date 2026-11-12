-- migrate:up
alter type title_status_enum add value if not exists 'CANCELED';

-- migrate:down
