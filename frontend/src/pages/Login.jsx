import "../styles/login.css";
import API from "../api/api";

export default function Login() {
  const handleLogin = async () => {
    window.location.href = "http://localhost:8000/auth/google-login";
  };

  return (
    <div className="login-wrapper">
      <div className="login-box">
        <h2>Login to Continue</h2>
        <button className="login-btn" onClick={handleLogin}>
          Login with Google
        </button>
      </div>
    </div>
  );
}
