"use client";
import { api, clearAccessToken, setAccessToken } from "./api";
import type { User } from "@/types";
const REFRESH = "mealq_refresh_token";
export function saveSession(data: any) {
  setAccessToken(data.access_token);
  localStorage.setItem(REFRESH, data.refresh_token);
}
export function getRefreshToken() {
  return typeof window !== "undefined" ? localStorage.getItem(REFRESH) : null;
}
export function clearSession() {
  clearAccessToken();
  localStorage.removeItem(REFRESH);
  localStorage.removeItem("mealq_user");
}
export async function login(identifier: string, password: string) {
  return await api.login({ identifier, password });
}

export async function verifyMfa(challengeToken: string, code: string) {
  const data = await api.verifyMfa({
    challenge_token: challengeToken,
    code,
  });

  saveSession(data);

  const user = await api.me();
  localStorage.setItem("mealq_user", JSON.stringify(user));

  return user as User;
}
export async function logout() {
  const r = getRefreshToken();
  try {
    if (r) await api.logout(r);
  } finally {
    clearSession();
  }
}
