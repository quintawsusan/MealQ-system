"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import Logo from "@/components/Logo";
import { api, ApiError } from "@/lib/api";
import { Field } from "@/components/Field";

export default function Setup() {
  const [required, setRequired] = useState<boolean | null>(null);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    user_name: "",
    email: "",
    password: "",
  });
  useEffect(() => {
    api
      .setupStatus()
      .then((x) => setRequired(x.first_super_admin_required))
      .catch((e) =>
        setError(
          e instanceof ApiError ? e.detail : "Could not check setup status",
        ),
      );
  }, []);
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.createFirstSuperAdmin(form);
      setDone(true);
    } catch (e) {
      setError(
        e instanceof ApiError ? e.detail : "Could not create Super Admin",
      );
    }
  }
  let content: React.ReactNode;
  if (required === null) content = <p>Checking setup status…</p>;
  else if (!required)
    content = (
      <>
        <div className="success">
          A Super Admin already exists. Initial setup is complete.
        </div>
        <div className="auth-footer">
          <Link href="/login">Go to sign in</Link>
        </div>
      </>
    );
  else if (done)
    content = (
      <>
        <div className="success">
          Super Admin created. Verify the email if email verification is
          enabled, then sign in.
        </div>
        <div className="auth-footer">
          <Link href="/login">Go to sign in</Link>
        </div>
      </>
    );
  else
    content = (
      <>
        <p>Create the first Super Admin account.</p>
        {error && (
          <div className="alert" style={{ marginBottom: 15 }}>
            {error}
          </div>
        )}
        <form className="form-grid" onSubmit={submit}>
          <Field
            label="First name"
            value={form.first_name}
            onChange={(e) => setForm({ ...form, first_name: e.target.value })}
            required
          />

          <Field
            label="Last name"
            value={form.last_name}
            onChange={(e) => setForm({ ...form, last_name: e.target.value })}
            required
          />

          <Field
            label="Username"
            value={form.user_name}
            onChange={(e) => setForm({ ...form, user_name: e.target.value })}
            required
          />

          <Field
            label="Email"
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
          />

          <div className="full">
            <Field
              label="Password"
              type="password"
              minLength={8}
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
            />
          </div>

          <div className="full">
            <button className="btn">Create Super Admin</button>
          </div>
        </form>
      </>
    );
  return (
    <div className="login-page">
      <section className="login-art">
        <Logo />
        <div className="landingpage-content ">
          <h1>Manage MealQ securely</h1>
          <p>
            The system permits only one Super Admin.
          </p>
        </div>
      </section>

      <section className="auth-panel">
        <div className="auth-box">
          <h1>Initial Admin setup</h1>
          {content}
        </div>
      </section>
    </div>
  );
}
