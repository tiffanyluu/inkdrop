import { useState, useEffect } from "react";
import type { SubscriptionItem } from "../types";

export default function Library() {
  const [subscriptions, setSubscriptions] = useState<SubscriptionItem[] | null>(
    null,
  );
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

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
          subscriptions?.filter(
            (s) => s.subscription_public_id !== subscriptionPublicId,
          ),
        );
      }
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
          <p>Status: {subscription.title_status}</p>
          <p>
            Read: {subscription.latest_read_chapter ?? "None"} / Latest:{" "}
            {subscription.latest_free_chapter ?? "None"}
          </p>
          {subscription.has_new_chapter && <p>New</p>}
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
