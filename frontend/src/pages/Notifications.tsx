import { useState, useEffect } from "react";
import type { NotificationItem } from "../types";

interface NotificationsProps {
  onSeen: () => void;
}

export default function Notifications({ onSeen }: NotificationsProps) {
  const [notifications, setNotifications] = useState<NotificationItem[] | null>(
    null,
  );
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadNotifications = async () => {
    try {
      const response = await fetch("/api/notifications");
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const data: NotificationItem[] = await response.json();
      setNotifications(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const handleMarkSeen = async (notificationPublicId: string) => {
    try {
      const response = await fetch(
        `/api/notifications/${notificationPublicId}`,
        { method: "PATCH" },
      );
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      await loadNotifications();
      onSeen();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    }
  };

  const handleMarkAllSeen = async () => {
    try {
      const response = await fetch("/api/notifications/seen-all", {
        method: "POST",
      });
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      await loadNotifications();
      onSeen();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    }
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  if (notifications === null || notifications.length === 0)
    return <p>No notifications yet</p>;
  return (
    <>
      <h2>Notifications</h2>
      <button onClick={handleMarkAllSeen}>Mark all seen</button>
      <ul>
        {notifications.map((notification) => (
          <li key={notification.notification_public_id}>
            {notification.cover_url && (
              <img
                src={
                  "/api/covers?url=" +
                  encodeURIComponent(notification.cover_url)
                }
                alt={notification.title_name}
                width={100}
              />
            )}
            <p>
              {notification.title_name}: Chapter {Number(notification.chapter)}
            </p>
            <p>{new Date(notification.create_datetime).toLocaleString()}</p>
            {notification.seen_datetime === null && (
              <>
                <p>New</p>
                <button
                  onClick={() =>
                    handleMarkSeen(notification.notification_public_id)
                  }
                >
                  Mark seen
                </button>
              </>
            )}
          </li>
        ))}
      </ul>
    </>
  );
}
