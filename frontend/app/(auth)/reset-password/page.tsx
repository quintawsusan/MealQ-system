"use client";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import Logo from "@/components/Logo";
import { api, ApiError } from "@/lib/api";
import { Field } from "@/components/Field";

function ResetContent() {
  const params = useSearchParams();
  const [token, setToken] = useState(params.get("token") || "");
  const [password, setPassword] = useState("");
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.resetPassword({ token, new_password: password });
      setDone(true);
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : "Reset failed");
    }
  }

  return (
    <div className="login-page">
      <section className="login-art">
        <Logo />
        <div>
          <p>
            Choose a new password that meets minimum of eight
            characters.
          </p>
        </div>
      </section>
      <section className="auth-panel">
        <div className="auth-box">
          <Logo />
          <h1>Reset password</h1>
          
          <p>Enter the reset token from your email.</p>
          {done ? (
            <>
              <div className="success">Password changed successfully.</div>
              <div className="auth-footer">
                <Link href="/login">Sign in</Link>
              </div>
            </>
          ) : (
              
            <form className="auth-form" onSubmit={submit}>
              {error && <div className="alert">{error}</div>}
              <Field
                label="Reset token"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                required
                />
                
              <Field
                label="New password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength={8}
                required
                />
                
              <button className="btn">Reset password</button>
            </form>
          )}
        </div>
      </section>
    </div>
  );
}

export default function Reset() {
  return (
    <Suspense fallback={<div>Loading…</div>}>
      <ResetContent />
    </Suspense>
  );
}
