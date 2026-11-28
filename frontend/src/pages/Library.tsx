import { useState, useEffect } from "react";
import type { SubscriptionItem } from "../types";

export default function Library() {
  const [subscriptions, setSubscriptions] = useState<SubscriptionItem[] | null>(
    null,
  );
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [editingSubscriptionPublicId, setEditingSubscriptionPublicId] =
    useState<string | null>(null);
  const [editReadUrl, setEditReadUrl] = useState<string>("");

  const loadSubscriptions = async () => {
    try {
      const response = await fetch("/api/subscriptions");
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const data: SubscriptionItem[] = await response.json();
      setSubscriptions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSubscriptions();
  }, []);

  const handleUnsubscribe = async (subscriptionPublicId: string) => {
    try {
      const response = await fetch(
        `/api/subscriptions/${subscriptionPublicId}`,
        {
          method: "DELETE",
        },
      );
      if (!response.ok) {
        throw new Error(`HTTP Error! Status: ${response.status}`);
      }
      if (subscriptions !== null) {
        setSubscriptions(
          subscriptions.filter(
            (s) => s.subscription_public_id !== subscriptionPublicId,
          ),
        );
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    }
  };

  const handleEdit = (subscription: SubscriptionItem) => {
    setEditingSubscriptionPublicId(subscription.subscription_public_id);
    setEditReadUrl(subscription.read_url ?? "");
  };

  const handleSaveReadUrl = async (subscriptionPublicId: string) => {
    try {
      const response = await fetch(
        `/api/subscriptions/${subscriptionPublicId}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            read_url: editReadUrl === "" ? null : editReadUrl,
          }),
        },
      );
      if (!response.ok) {
        throw new Error(`HTTP Error! Status: ${response.status}`);
      }
      setEditingSubscriptionPublicId(null);
      await loadSubscriptions();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    }
  };

  const handleUpdateLatestReadChapter = async (
    subscriptionPublicId: string,
    latestReadChapter: number,
  ) => {
    try {
      const response = await fetch(
        `/api/subscriptions/${subscriptionPublicId}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            latest_read_chapter: latestReadChapter,
          }),
        },
      );
      if (!response.ok) {
        throw new Error(`HTTP Error! Status: ${response.status}`);
      }
      await loadSubscriptions();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    }
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  if (subscriptions === null || subscriptions.length === 0)
    return <p>No subscriptions yet</p>;
  return (
    <ul>
      {subscriptions.map((subscription) => (
        <li key={subscription.subscription_public_id}>
          {subscription.cover_url && (
            <img
              src={
                "/api/covers?url=" + encodeURIComponent(subscription.cover_url)
              }
              alt={subscription.title_name}
              width={100}
            />
          )}
          <p>{subscription.title_name}</p>
          {subscription.read_url && (
            <a
              href={subscription.read_url}
              target="_blank"
              rel="noopener noreferrer"
            >
              Read
            </a>
          )}
          <p>Status: {subscription.title_status}</p>
          <p>
            Read: {subscription.latest_read_chapter ?? "None"} / Latest:{" "}
            {subscription.latest_free_chapter ?? "None"}
          </p>
          {subscription.has_new_chapter && <p>New</p>}
          {subscription.latest_free_chapter !== null &&
            Number(subscription.latest_read_chapter ?? 0) <
              Number(subscription.latest_free_chapter) && (
              <button
                onClick={() =>
                  handleUpdateLatestReadChapter(
                    subscription.subscription_public_id,
                    Number(subscription.latest_free_chapter),
                  )
                }
              >
                Mark ch. {Number(subscription.latest_free_chapter)} read
              </button>
            )}
          {subscription.latest_free_chapter !== null &&
            Number(subscription.latest_read_chapter ?? 0) + 1 <
              Number(subscription.latest_free_chapter) && (
              <button
                onClick={() =>
                  handleUpdateLatestReadChapter(
                    subscription.subscription_public_id,
                    Number(subscription.latest_read_chapter ?? 0) + 1,
                  )
                }
              >
                Mark ch. {Number(subscription.latest_read_chapter ?? 0) + 1}{" "}
                read
              </button>
            )}
          {subscription.latest_read_chapter !== null &&
            Number(subscription.latest_read_chapter) >= 1 && (
              <button
                onClick={() =>
                  handleUpdateLatestReadChapter(
                    subscription.subscription_public_id,
                    Number(subscription.latest_read_chapter) - 1,
                  )
                }
              >
                Mark ch. {Number(subscription.latest_read_chapter)} unread
              </button>
            )}
          {editingSubscriptionPublicId ===
          subscription.subscription_public_id ? (
            <div>
              <label htmlFor="readUrl">Read URL</label>
              <input
                id="readUrl"
                type="url"
                value={editReadUrl}
                onChange={(e) => setEditReadUrl(e.target.value)}
              />
              <button
                onClick={() =>
                  handleSaveReadUrl(subscription.subscription_public_id)
                }
              >
                Save
              </button>
              <button onClick={() => setEditingSubscriptionPublicId(null)}>
                Cancel
              </button>
            </div>
          ) : (
            <button onClick={() => handleEdit(subscription)}>
              Edit read URL
            </button>
          )}
          <button
            onClick={() =>
              handleUnsubscribe(subscription.subscription_public_id)
            }
          >
            Unsubscribe
          </button>
        </li>
      ))}
    </ul>
  );
}
