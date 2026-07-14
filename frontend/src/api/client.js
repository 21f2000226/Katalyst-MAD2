const TOKEN_KEY = "access_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  // FormData sets its own Content-Type (with boundary)
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(path, { ...options, headers });
  let data = null;
  const text = await response.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { message: text };
    }
  }

  if (!response.ok) {
    const error = new Error(data?.message || "Request failed");
    error.status = response.status;
    error.data = data;
    throw error;
  }
  return data;
}

export async function openAuthedFile(path) {
  // open resume in a new tab
  const token = getToken();
  const response = await fetch(path, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) throw new Error("Could not load file");
  const blob = await response.blob();
  window.open(URL.createObjectURL(blob), "_blank");
}

// blob URL for in-page PDF iframe
export async function fetchAuthedBlob(path) {
  const token = getToken();
  const response = await fetch(path, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) throw new Error("Could not load file");
  const blob = await response.blob();
  const contentType = blob.type || response.headers.get("Content-Type") || "";
  return {
    url: URL.createObjectURL(blob),
    contentType,
    isPdf: contentType.includes("pdf") || path.toLowerCase().endsWith(".pdf"),
  };
}
