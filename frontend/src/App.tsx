import { useState, useEffect } from "react";
import Signup from "./Signup";
import Login from "./Login";
import Search from "./Search";

export interface User {
  user_public_id: string;
  email: string;
  first_name: string;
  last_name: string;
}

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showSignup, setShowSignup] = useState<boolean>(false);

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
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unknown error occurred");
      }
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
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unknown error occurred");
      }
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

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
      <Search />
      <button onClick={handleLogout}>Logout</button>
    </>
  );
}
