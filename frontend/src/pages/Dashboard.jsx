import { useEffect, useState } from "react";
import API from "../api/api";
import Navbar from "../components/Navbar";
import StatsCard from "../components/StatsCard";
import "../styles/dashboard.css";

export default function Dashboard() {
  const [stats, setStats] = useState({
    total: 0,
    inquiries: 0,
    complaints: 0,
    replied: 0,
  });

  const [filter, setFilter] = useState("today");

  const loadStats = async () => {
    try {
      const res = await API.get(`/emails/stats?filter=${filter}`);
      setStats(res.data);
    } catch (e) {
      console.error("Stats fetch error:", e);
    }
  };

  useEffect(() => {
    loadStats();
  }, [filter]);

  return (
    <>
      <Navbar />

      <div className="container">

        <div className="filter-bar">
          {["today", "3days", "week"].map(f => (
            <button
              key={f}
              className={`filter-btn ${filter === f ? "active" : ""}`}
              onClick={() => setFilter(f)}
            >
              {f === "today" ? "Today" :
               f === "3days" ? "Last 3 Days" :
               "Last Week"}
            </button>
          ))}
        </div>

        <div className="stats-grid">
          <StatsCard title="Total Emails" value={stats.total} />
          <StatsCard title="Inquiries" value={stats.inquiries} />
          <StatsCard title="Complaints" value={stats.complaints} />
          <StatsCard title="Replied" value={stats.replied} />
        </div>

      </div>
    </>
  );
}
