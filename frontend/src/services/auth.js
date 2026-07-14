import { reactive } from "vue";
import { api, clearToken, getToken, setToken } from "../api/client";

// Auth service: login/register, restore session on refresh, logout, role home paths.

export const authState = reactive({
  user: null,
  loading: false,
});


// Calls /api/auth/login, saves the JWT in localStorage, and keeps the user in memory.
export async function login(username, password) {
  const data = await api("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  setToken(data.access_token);
  authState.user = data.user;
  return data.user;
}


// Creates a student or company account. the register page still sends them to login after.
export async function register(payload) {
  return api("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}


// On app start (and when the router needs it): if a token exists, ask /me who we are.
// Bad or expired tokens get cleared so the UI does not think we are still signed in.
export async function fetchMe() {
  if (!getToken()) {
    authState.user = null;
    return null;
  }
  authState.loading = true;
  try {
    const data = await api("/api/auth/me");
    authState.user = data.user;
    return data.user;
  } catch {
    clearToken();
    authState.user = null;
    return null;
  } finally {
    authState.loading = false;
  }
}


// Clears the token and user locally. We do not call a logout API; the JWT just expires later.
export function logout() {
  clearToken();
  authState.user = null;
}


//adfter login, send each role to its main page (admin dashboard, company drives, student drives).
export function dashboardPathForRole(role) {
  if (role === "admin") return "/admin";
  if (role === "company") return "/company/drives";
  if (role === "student") return "/student/drives";
  return "/login";
}
