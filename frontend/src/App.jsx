import React, { useEffect, useState } from "react";
import LoginPage from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import { checkLogin } from "./api/api";

export default function App() {
  const [loggedIn, setLoggedIn] = useState(null); // null = loading

  useEffect(() => {
    async function checkStatus() {
      try {
        const data = await checkLogin();
        setLoggedIn(data);
      } catch (e) {
        console.error("Failed to check login status:", e);
        setLoggedIn(false);
      }
    }
    checkStatus();
  }, []);

  if (loggedIn === null) {
    return <div>Loading...</div>;
  }

  return loggedIn ? <Dashboard /> : <LoginPage />;
}


