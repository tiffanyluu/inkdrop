export interface User {
  user_public_id: string;
  email: string;
  first_name: string;
  last_name: string;
}

export type SourceType = "MANGADEX" | "ATHREA";

export interface TitleSource {
  source_id: string;
  source_type: SourceType;
}

export interface TitleResult {
  name: string;
  cover_url: string | null;
  sources: TitleSource[];
}

export type TitleStatus = "ONGOING" | "COMPLETED" | "HIATUS" | "CANCELED";

export interface SubscriptionItem {
  title_public_id: string;
  title_name: string;
  cover_url: string | null;
  title_status: TitleStatus;
  latest_read_chapter: string | null;
  latest_free_chapter: string | null;
  read_url: string | null;
  subscription_public_id: string;
  has_new_chapter: boolean;
}

export interface NotificationItem {
  notification_public_id: string;
  title_name: string;
  cover_url: string | null;
  chapter: string;
  seen_datetime: string | null;
  create_datetime: string;
}

export interface UnseenCount {
  count: number;
}
