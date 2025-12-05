import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",
});

// Return { logged_in: true/false }
export const checkLogin = async () => {
  try {
    const res = await API.get("/auth/status");
    return res.data;
  } catch (e) {
    console.error("Login status check failed:", e);
    return { logged_in: false };
  }
};

export const fetchStats = async (filter) => {
  try {
    const res = await API.get(`/emails/stats?filter=${filter}`);
    return res.data;
  } catch (e) {
    console.error("Stats fetch failed:", e);
    return {
      total: 0,
      inquiries: 0,
      complaints: 0,
      replied: 0,
    };
  }
};

// ⭐ NEW — matches backend /emails/unread-count
export const getUnreadCount = async () => {
  try {
    const res = await API.get("/emails/unread-count");
    return res.data; // { unread: number }
  } catch (e) {
    console.error("Unread fetch failed:", e);
    return { unread: 0 };
  }
};

export default API;
