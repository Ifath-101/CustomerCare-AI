export default function Navbar() {
  const logout = () => {
    localStorage.removeItem("token");
    window.location.href = "/";
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <div className="brand-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="5" width="18" height="14" rx="2" ry="2"></rect>
              <polyline points="3 7 12 13 21 7"></polyline>
            </svg>
          </div>
          <div className="brand-text">
            <h1>Email Replier</h1>
            <p>Dashboard Analytics</p>
          </div>
        </div>
        <button className="logout-btn" onClick={logout}>Logout</button>
      </div>
    </nav>
  );
}