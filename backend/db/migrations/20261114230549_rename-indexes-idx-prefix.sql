-- migrate:up
alter index title_sources_title_idx rename to idx_title_sources_title;
alter index users_email_lower_idx rename to idx_users_email_lower;
alter index subscriptions_title_idx rename to idx_subscriptions_title;

-- migrate:down
alter index idx_subscriptions_title rename to subscriptions_title_idx;
alter index idx_users_email_lower rename to users_email_lower_idx;
alter index idx_title_sources_title rename to title_sources_title_idx;
