import { useEffect, useState } from "react";
import { fetchStats, getUnreadCount } from "../api/api";
import Navbar from "../components/Navbar";
import StatsCard from "../components/StatsCard";
import "../styles/dashboard.css";
import "../styles/components.css";

export default function Dashboard() {
  const [stats, setStats] = useState({
    total: 0,
    inquiries: 0,
    complaints: 0,
    replied: 0,
  });

  const [unread, setUnread] = useState(0);
  const [filter, setFilter] = useState("today");
  const [loading, setLoading] = useState(true);

  const loadStats = async () => {
    setLoading(true);
    try {
      const data = await fetchStats(filter);
      setStats(data);
    } catch (e) {
      console.error("Stats fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  const loadUnread = async () => {
    try {
      const data = await getUnreadCount();
      setUnread(data.unread);
    } catch (e) {
      console.error("Unread fetch error:", e);
    }
  };

  useEffect(() => {
    loadStats();
  }, [filter]);

  useEffect(() => {
    loadUnread();
  }, []);

  return (
    <>
      <Navbar />

      <div className="container">
        {/* Header Section */}
        <div className="header-section">
          <h2 className="page-title">Dashboard Overview</h2>
          <p className="page-subtitle">Monitor your email metrics and performance</p>
        </div>

        {/* Filter Bar */}
        <div className="filter-card">
          <div className="filter-header">
            <div className="filter-label">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
              <span>Time Period:</span>
            </div>
            <div className="filter-buttons">
              {["today", "3days", "week"].map((f) => (
                <button
                  key={f}
                  className={`filter-btn ${filter === f ? "active" : ""}`}
                  onClick={() => setFilter(f)}
                >
                  {f === "today" ? "Today" : f === "3days" ? "Last 3 Days" : "Last Week"}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        {loading ? (
          <div className="stats-grid">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="stats-card loading-skeleton">
                <div className="skeleton-icon"></div>
                <div className="skeleton-text"></div>
                <div className="skeleton-value"></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="stats-grid">
            <StatsCard 
              title="Total Emails" 
              value={stats.total} 
              icon="mail"
              color="blue"
              trend="+12%"
            />
            <StatsCard 
              title="Inquiries" 
              value={stats.inquiries} 
              icon="message"
              color="cyan"
              trend="+8%"
            />
            <StatsCard 
              title="Complaints" 
              value={stats.complaints} 
              icon="alert"
              color="red"
              trend="-3%"
            />
            <StatsCard 
              title="Replied" 
              value={stats.replied} 
              icon="check"
              color="green"
              trend="+15%"
            />
            <StatsCard 
              title="Unread Emails" 
              value={unread} 
              icon="inbox"
              color="purple"
            />
          </div>
        )}

        {/* Quick Actions Banner */}
        <div className="action-banner">
          <div className="action-content">
            <h3>Need Help?</h3>
            <p>View documentation or contact support</p>
          </div>
          <button className="action-btn">Get Support</button>
        </div>
      </div>
    </>
  );
}