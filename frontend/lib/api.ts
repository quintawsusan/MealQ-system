import type { Role, Session } from "@/types";
const API_URL = (
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"
).replace(/\/$/, "");

export class ApiError extends Error {
  status: number;
  detail: string;
  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

let accessToken: string | null = null;
export function setAccessToken(token: string | null) {
  accessToken = token;
  if (typeof window !== "undefined") {
    if (token) localStorage.setItem("mealq_access_token", token);
    else localStorage.removeItem("mealq_access_token");
  }
}

export function getAccessToken() {
  if (accessToken) return accessToken;
  if (typeof window !== "undefined")
    accessToken = localStorage.getItem("mealq_access_token");
  return accessToken;
}

export function clearAccessToken() {
  setAccessToken(null);
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  retry = true,
): Promise<T> {
  const headers = new Headers(options.headers);

  if (
    options.body &&
    !(typeof FormData !== "undefined" && options.body instanceof FormData) &&
    !headers.has("Content-Type")
  )
    headers.set("Content-Type", "application/json");
  const token = getAccessToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  let res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    cache: "no-store",
  });

  if (res.status === 401 && retry && typeof window !== "undefined") {
    const refresh = localStorage.getItem("mealq_refresh_token");
    if (refresh) {
      const rr = await fetch(`${API_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refresh }),
      });
      if (rr.ok) {
        const data = await rr.json();
        setAccessToken(data.access_token);
        return request<T>(path, options, false);
      }
    }
  }

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      detail =
        typeof body.detail === "string"
          ? body.detail
          : JSON.stringify(body.detail || body);
    } catch {}
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  login: (body: any) =>
    request<any>("/auth/login", { method: "POST", body: JSON.stringify(body) }),

  verifyMfa: (body: { challenge_token: string; code: string }) =>
    request<any>("/auth/verify-mfa", { method: "POST", body: JSON.stringify(body), }),

  register: (body: any) =>
    request<any>("/auth/register", {method: "POST",body: JSON.stringify(body),}),

  me: () => request<any>("/auth/me"),

  verifyEmail: (token: string) =>
    request<any>(`/auth/verify-email?token=${encodeURIComponent(token)}`),

    resendVerification: (email: string) =>
    request<{ detail: string }>("/auth/resend-verification", {
      method: "POST",
      body: JSON.stringify({ email }),
    }),
  forgotPassword: (identifier: string) =>
    request<any>("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ identifier }),
    }),

  resetPassword: (body: any) =>
    request<void>("/auth/reset-password", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  changePassword: (body: any) =>
    request<void>("/auth/change-password", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  logout: (refresh_token: string) =>
    request<void>("/auth/logout", {
      method: "POST",
      body: JSON.stringify({ refresh_token }),
    }),

  setupStatus: () => request<any>("/auth/setup/status"),
  createFirstSuperAdmin: (body: any) =>
    request<any>("/auth/setup/first-super-admin", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  createAdmin: (body: any) =>
    request<any>("/auth/admin/users", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  unlock: (id: string) =>
    request<any>(`/auth/users/${id}/unlock`, { method: "POST" }),
  auditLogs: (limit = 100) => request<any[]>(`/auth/audit-logs?limit=${limit}`),
  students: (offset = 0, limit = 500) =>
    request<any[]>(`/students?offset=${offset}&limit=${limit}`),
  studentMe: () => request<any>("/students/me"),

  updateStudent: (id: string, body: any) =>
    request<any>(`/students/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  deleteStudent: (id: string) =>
    request<void>(`/students/${id}`, { method: "DELETE" }),

  importStudents: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return request<any>("/students/import", { method: "POST", body: fd });
  },

  users: (offset = 0, limit = 500) =>
    request<any[]>(`/users?offset=${offset}&limit=${limit}`),
  updateUser: (id: string, body: any) =>
    request<any>(`/users/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  deleteUser: (id: string) =>
    request<void>(`/users/${id}`, { method: "DELETE" }),
  mealTypes: () => request<any[]>("/meal-types"),

  createMealType: (body: any) =>
    request<any>("/meal-types", { method: "POST", body: JSON.stringify(body) }),

  updateMealType: (id: string, body: any) =>
    request<any>(`/meal-types/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  deleteMealType: (id: string) =>
    request<void>(`/meal-types/${id}`, { method: "DELETE" }),

  schedules: (params = "") =>
    request<any[]>(`/meal-schedules${params ? `?${params}` : ""}`),

  upcoming: (days = 7) =>
    request<any[]>(`/meal-schedules/upcoming?days=${days}`),

  createSchedule: (body: any) =>
    request<any>("/meal-schedules", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  updateSchedule: (id: string, body: any) =>
    request<any>(`/meal-schedules/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  deactivateSchedule: (id: string) =>
    request<void>(`/meal-schedules/${id}`, { method: "DELETE" }),

  sessions: (status?: string) =>
    request<any[]>(`/meal-sessions${status ? `?status=${status}` : ""}`),
  getSession: (id: string) => request<any>(`/meal-sessions/${id}`),

  activeSession: () => request<Session | null>("/meal-sessions/active"),

  createSession: (body: any) =>
    request<any>("/meal-sessions", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  startSession: (id: string) =>
    request<any>(`/meal-sessions/${id}/start`, { method: "POST" }),

  pauseSession: (id: string) =>
    request<any>(`/meal-sessions/${id}/pause`, { method: "POST" }),

  resumeSession: (id: string) =>
    request<any>(`/meal-sessions/${id}/resume`, { method: "POST" }),

  completeSession: (id: string) =>
    request<any>(`/meal-sessions/${id}/complete`, { method: "POST" }),

  advance: (id: string, force = false) =>
    request<any>(`/meal-sessions/${id}/advance?force=${force}`, {method: "POST"}),

  deleteSession: (id: string) =>
    request<void>(`/meal-sessions/${id}`, { method: "DELETE" }),

  batches: (id: string) => request<any[]>(`/meal-sessions/${id}/batches`),

  currentBatch: (id: string) =>
    request<any>(`/meal-sessions/${id}/current-batch`),
  myBatch: (id: string) => request<any>(`/meal-sessions/${id}/my-batch`),

  monitor: (id: string) => request<any>(`/meal-sessions/${id}/monitor`),
  respond: (id: string, response: "GOING" | "SKIPPED") =>
    request<any>(`/meal-sessions/${id}/responses/me`, {
      method: "POST",
      body: JSON.stringify({ response }),
    }),

  responses: (id: string) => request<any[]>(`/meal-sessions/${id}/responses`),

  device: () => request<any>("/devices/me"),

  registerDevice: (device_identifier: string) =>
    request<any>("/devices/me", {
      method: "POST",
      body: JSON.stringify({ device_identifier }),
    }),

  updateDevice: (body: any) =>
    request<any>("/devices/me", {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  deleteDevice: () => request<void>("/devices/me", { method: "DELETE" }),
};
export { API_URL };
