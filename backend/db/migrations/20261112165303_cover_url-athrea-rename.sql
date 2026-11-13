-- migrate:up
alter type sources_type_enum rename value 'ATHREA_SCANS' to 'ATHREA';

alter table titles rename column image_url to cover_url;
-- migrate:down
alter table titles rename column cover_url to image_url;
alter type sources_type_enum rename value 'ATHREA' to 'ATHREA_SCANS';

