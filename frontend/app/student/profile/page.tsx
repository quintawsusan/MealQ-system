"use client";
import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { Device, Student, User } from "@/types";
import { Field } from "@/components/Field";
import { Toast, useToast } from "@/components/Toast";

function PasswordForm({ show }: { show: (m: string) => void }) {
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      await api.changePassword({
        current_password: current,
        new_password: next,
      });
      setCurrent("");
      setNext("");
      show("Password changed");
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not change password");
    } finally {
      setBusy(false);
    }
  }
  return (
    <form className="auth-form" onSubmit={submit}>
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

      <button
        className="btn"
        disabled={busy}
        style={{
          background: "#f97316",
          color: "white",
          padding: "12px 24px",
          width: "fit-content",
          borderRadius: "8px",
          fontSize: "15px",
          fontWeight: 600,
        }}
      >
        {busy ? "Changing…" : "Change password"}
      </button>
    </form>
  );
}
export default function Profile() {
  const [u, setU] = useState<User | null>(null);
  const [s, setS] = useState<Student | null>(null);
  const [d, setD] = useState<Device | null>(null);
  const [id, setId] = useState("");
  const [busy, setBusy] = useState(false);
  const { message, show } = useToast();
  async function load() {
    try {
      const [a, b] = await Promise.all([api.me(), api.studentMe()]);
      setU(a);
      setS(b);
      const dev = await api.device().catch(() => null);
      setD(dev);
      setId(dev?.device_identifier || "");
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Unable to load profile");
    }
  }
  useEffect(() => {
    load();
  }, []);
  async function saveDevice(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      if (d) await api.updateDevice({ device_identifier: id });
      else await api.registerDevice(id);
      show("Device saved");
      await load();
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not save device");
    } finally {
      setBusy(false);
    }
  }
  async function remove() {
    try {
      await api.deleteDevice();
      setD(null);
      setId("");
      show("Device removed");
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not remove device");
    }
  }
  return (
    <>
      <Toast message={message} />
      <div className="page-header">
        <div>
          <div className="eyebrow">Student profile</div>
          <h1 className="page-title">Your account</h1>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <div style={{ display: "grid", gap: 13, marginTop: 15 }}>
            <div>
              <small className="card-title">Name</small>
              <div>
                <div>{u ? `${u.first_name} ${u.last_name}` : "—"}</div>
              </div>
            </div>

            <div>
              <small className="card-title">Username</small>
              <div>{u?.user_name || "—"}</div>
            </div>
            <div>
              <small className="card-title">Email</small>
              <div>{u?.email || "—"}</div>
            </div>
          </div>
        </div>

        <div className="card">
          <div style={{ display: "grid", gap: 13, marginTop: 15 }}>
            <div>
              <small className="card-title">Student number</small>
              <div>{s?.student_number || "—"}</div>
            </div>
            <div>
              <small className="card-title">Class</small>
              <div>
                <div>{s?.class_name || "—"}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="card section-gap">
        <h3 className="card-title">Assigned device</h3>

        <form
          className="form-grid"
          onSubmit={saveDevice}
          style={{ marginTop: 15 }}
        >
          <Field
            label="Laptop Number"
            value={id}
            onChange={(e) => setId(e.target.value)}
            required
          />
          <div style={{ display: "flex", alignItems: "end", gap: 8 }}>
            <button className="btn" disabled={busy}>
              {busy ? "Saving…" : d ? "Update device" : "Register device"}
            </button>
            {d && (
              <button type="button" className="btn danger" onClick={remove}>
                Remove
              </button>
            )}
          </div>
        </form>
      </div>
      <div className="card section-gap">
        <h3 className="card-title">Change password</h3>
        <PasswordForm show={show} />
      </div>
    </>
  );
}
