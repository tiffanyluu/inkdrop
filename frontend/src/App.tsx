import { useState, useEffect } from "react";
import Signup from "./components/Signup";
import Login from "./components/Login";
import Search from "./pages/Search";
import Library from "./pages/Library";
import Notifications from "./pages/Notifications";
import { Routes, Route, Link } from "react-router";
import type { UnseenCount, User } from "./types";

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showSignup, setShowSignup] = useState<boolean>(false);
  const [unseenCount, setUnseenCount] = useState<number>(0);

  const fetchUser = async () => {
    try {
      const response = await fetch("/api/auth/me");
      if (response.status === 401) {
        return;
      }
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const data: User = await response.json();
      setUser(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (email: string, password: string) => {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });
    if (response.status === 401) {
      throw new Error("Invalid email or password");
    }
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    await fetchUser();
  };

  const handleLogout = async () => {
    try {
      const response = await fetch("/api/auth/logout", { method: "POST" });
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      setUser(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    }
  };

  const fetchUnseenCount = async () => {
    const response = await fetch("/api/notifications/unseen-count");
    if (!response.ok) {
      return;
    }
    const data: UnseenCount = await response.json();
    setUnseenCount(data.count);
  };

  useEffect(() => {
    fetchUser();
  }, []);

  useEffect(() => {
    if (user !== null) {
      fetchUnseenCount();
    }
  }, [user]);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!user) {
    if (showSignup) {
      return (
        <>
          <Signup onSignup={handleLogin} />
          <button onClick={() => setShowSignup(false)}>
            Have an account? Log in
          </button>
        </>
      );
    }
    return (
      <>
        <Login onLogin={handleLogin} />
        <button onClick={() => setShowSignup(true)}>Create account</button>
      </>
    );
  }
  return (
    <>
      <h1>Hi {user.first_name}</h1>
      <nav>
        <Link to="/">Library</Link>
        <Link to="/search">Search</Link>
        <Link to="/notifications">
          Notifications {unseenCount > 0 && `(${unseenCount})`}
        </Link>
      </nav>
      <Routes>
        <Route path="/" element={<Library />} />
        <Route path="/search" element={<Search />} />
        <Route
          path="/notifications"
          element={<Notifications onSeen={fetchUnseenCount} />}
        />
        <Route path="*" element={<p>Page not found</p>} />
      </Routes>
      <button onClick={handleLogout}>Logout</button>
    </>
  );
}
