"use client";
import Link from "next/link";
import { useState } from "react";
import Logo from "@/components/Logo";
import { api, ApiError } from "@/lib/api";
import { Field } from "@/components/Field";

export default function Forgot() {
  const [identifier, setIdentifier] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.forgotPassword(identifier);
      setSent(true);
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : "Unable to request reset");
    }
  }
  return (
    <div className="login-page">
      <section className="login-art">
        <Logo />
        <div className="landingpage-content">
          <h1>Reset access.</h1>
          <p>Request a password reset using your account email.</p>
        </div>
      </section>

      <section className="auth-panel">
        <div className="auth-box">
          <Logo />
          <h1>Forgot password?</h1>
          <p>We’ll send reset instructions in a few minutes.</p>
          {sent ? (
            <div className="success">
              If an account matches, a password reset email has been sent.
            </div>
          ) : (
            <form className="auth-form" onSubmit={submit}>
              {error && <div className="alert">{error}</div>}
              <Field
                label="Username or email"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                required
              />
              <button className="btn">Send reset instructions</button>
            </form>
          )}
          <div className="auth-footer">
            <Link href="/login">Back to sign in</Link>
          </div>
        </div>
      </section>
    </div>
  );
}
