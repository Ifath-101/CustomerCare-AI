import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000",
});

export const checkLogin = async () => {
  try {
    const res = await API.get("/auth/status");
    return res.data.logged_in;
  } catch (e) {
    console.error("Login status check failed:", e);
    return false;
  }
};

export const fetchStats = async (filter) => {
  try {
    const res = await API.get(`/emails/stats?filter=${filter}`);
    return res.data;
  } catch (e) {
    console.error("Stats fetch failed:", e);
    return {};
  }
};

export default API;
