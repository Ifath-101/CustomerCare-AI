export default function Navbar() {
  const logout = () => {
    localStorage.removeItem("token");
    window.location.href = "/";
  };

  return (
    <div className="navbar">
      <h2>Email Replier Dashboard</h2>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
