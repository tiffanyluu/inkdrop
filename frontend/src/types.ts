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
