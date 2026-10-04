"use client";
import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { User } from "@/types";
import { Field } from "@/components/Field";
import { Toast, useToast } from "@/components/Toast";

export default function AdminProfile() {
  const [u, setU] = useState<User | null>(null);
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [busy, setBusy] = useState(false);
  const { message, show } = useToast();
  useEffect(() => {
    api
      .me()
      .then(setU)
      .catch((e) =>
        show(e instanceof ApiError ? e.detail : "Unable to load profile"),
      );
  }, []);
  async function change(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      await api.changePassword({
        current_password: current,
        new_password: next,
      });
      setCurrent("");
      setNext("");
      show("Password changed.");
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not change password");
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <Toast message={message} />
      <div className="page-header">
        <div>
          <div className="eyebrow">Account</div>
          <h1 className="page-title">Admin profile</h1>
          <p className="page-subtitle">
            Your authenticated account details and password controls.
          </p>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h3 className="card-title">Account</h3>
          <div style={{ display: "grid", gap: 12, marginTop: 15 }}>
            <div>
              <small className="muted">Name</small>
              <div>
                <strong>{u ? `${u.first_name} ${u.last_name}` : "—"}</strong>
              </div>
            </div>
            <div>
              <small className="muted">Username</small>
              <div>{u?.user_name}</div>
            </div>
            <div>
              <small className="muted">Email</small>
              <div>{u?.email}</div>
            </div>
            <div>
              <small className="muted">Role</small>
              <div>
                <span className="badge scheduled">{u?.role}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="card-title">Change password</h3>
          <form
            className="auth-form"
            style={{ marginTop: 15 }}
            onSubmit={change}
          >
            <Field
              label="Current password"
              type="password"
              value={current}
              onChange={(e) => setCurrent(e.target.value)}
              required
            />

            <Field
              label="New password"
              type="password"
              minLength={8}
              value={next}
              onChange={(e) => setNext(e.target.value)}
              required
            />

            <button className="btn" disabled={busy}>
              {busy ? "Changing…" : "Change password"}
            </button>
          </form>
        </div>
      </div>
    </>
  );
}
