import React, { useState } from "react";

type SourceType = "MANGADEX" | "ATHREA";

interface TitleSource {
  source_id: string;
  source_type: SourceType;
}

interface TitleResult {
  name: string;
  cover_url: string | null;
  sources: TitleSource[];
}

export default function Search() {
  const [query, setQuery] = useState<string>("");
  const [titles, setTitles] = useState<TitleResult[] | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [subscribedNames, setSubscribedNames] = useState<string[]>([]);

  const handleSubmit = async (event: React.SubmitEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const encodedQuery: string = encodeURIComponent(query);
      const response = await fetch(`/api/titles/search?query=${encodedQuery}`);
      if (response.status === 502) {
        throw new Error("Search is unavailable. Please try again later");
      }
      if (!response.ok) {
        throw new Error(`HTTP Error! Status: ${response.status}`);
      }
      const data: TitleResult[] = await response.json();
      setTitles(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (title: TitleResult) => {
    setError(null);

    try {
      const response = await fetch("/api/subscriptions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          sources: title.sources,
        }),
      });
      if (!response.ok) {
        throw new Error(`HTTP Error! Status: ${response.status}`);
      }
      setSubscribedNames([...subscribedNames, title.sources[0].source_id]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    }
  };
  return (
    <>
      <form onSubmit={handleSubmit}>
        <h2>Search</h2>

        {error && <p style={{ color: "red" }}>{error}</p>}

        <div>
          <label htmlFor="search">Search For a Title</label>
          <input
            id="search"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            required
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>
      {titles !== null && titles.length === 0 && <p>No results</p>}
      {titles !== null && (
        <ul>
          {titles.map((title) => (
            <li key={title.name}>
              {title.cover_url && (
                <img
                  src={"/api/covers?url=" + encodeURIComponent(title.cover_url)}
                  alt={title.name}
                  width={100}
                />
              )}
              {title.name}
              {subscribedNames.includes(title.sources[0].source_id) ? (
                <button disabled>Subscribed ✓</button>
              ) : (
                <button onClick={() => handleSubscribe(title)}>
                  Subscribe
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
