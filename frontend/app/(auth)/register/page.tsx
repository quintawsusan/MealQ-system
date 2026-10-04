"use client";
import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Logo from "@/components/Logo";
import { api, ApiError } from "@/lib/api";
import { Field, SelectField } from "@/components/Field";

export default function Register() {
  const router = useRouter();
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    user_name: "",
    email: "",
    password: "",
    student_number: "",
    class_name: "Anita B",
  });
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const [busy, setBusy] = useState(false);
  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.register({
        ...form,
        student_number: Number(form.student_number),
      });
      setDone(true);
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : "Registration failed");
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="login-page">
      <section className="login-art">
        <Logo />
        <div className="landingpage-content">
          <h1>Your place in the queue starts here.</h1>
          <p>
            Create your student account, then use MealQ to see your assigned
            serving batch and respond when it is called.
          </p>
        </div>
      </section>

      <section className="auth-panel">
        <div className="auth-box">
          {done ? (
            <>
              <h1>Check your email</h1>
              <p>
                Your account was created. Verify your email before signing in.
              </p>
              <Link
                className="btn"
                href="/login"
                style={{ display: "inline-block", textDecoration: "none" }}
              >
                Back to sign in
              </Link>
            </>
          ) : (
            <>
              <h1>Create student account</h1>
              {error && (
                <div className="alert" style={{ marginBottom: 15 }}>
                  {error}
                </div>
              )}
              <form className="auth-form" onSubmit={submit}>
                <div className="form-grid">
                  <Field
                    label="First name"
                    value={form.first_name}
                    onChange={(e) => set("first_name", e.target.value)}
                    required
                  />

                  <Field
                    label="Last name"
                    value={form.last_name}
                    onChange={(e) => set("last_name", e.target.value)}
                    required
                  />

                  <Field
                    label="Username"
                    value={form.user_name}
                    onChange={(e) => set("user_name", e.target.value)}
                    required
                    minLength={3}
                  />

                  <Field
                    label="Email"
                    type="email"
                    value={form.email}
                    onChange={(e) => set("email", e.target.value)}
                    required
                  />

                  <Field
                    label="Student number"
                    type="number"
                    value={form.student_number}
                    onChange={(e) => set("student_number", e.target.value)}
                    required
                  />

                  <SelectField
                    label="Class"
                    value={form.class_name}
                    onChange={(e) => set("class_name", e.target.value)}
                  >
                    <option>Anita B</option>
                    <option>Ada Lab</option>
                    <option>Lovelace</option>
                  </SelectField>

                  <div className="full">
                    <Field
                      label="Password"
                      type="password"
                      value={form.password}
                      onChange={(e) => set("password", e.target.value)}
                      required
                      minLength={8}
                    />
                  </div>
                </div>

                <button className="btn" disabled={busy}>
                  {busy ? "Creating account…" : "Create account"}
                </button>
              </form>
              <div className="auth-footer">
                Already registered? <Link href="/login">Sign in</Link>
              </div>
            </>
          )}
        </div>
      </section>
    </div>
  );
}
