"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Logo from "@/components/Logo";
import { login, verifyMfa } from "@/lib/auth";
import { ApiError } from "@/lib/api";
import { Field } from "@/components/Field";

export default function Login() {
  const router = useRouter();

  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const [challengeToken, setChallengeToken] = useState("");
  const [mfaStep, setMfaStep] = useState(false);

  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submitLogin(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");

    try {
      const data = await login(identifier, password);

      if (data.mfa_required && data.challenge_token) {
        setChallengeToken(data.challenge_token);
        setMfaStep(true);
        return;
      }

      setError("Unexpected login response.");
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : "Unable to sign in");
    } finally {
      setBusy(false);
    }
  }

  async function submitMfa(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");

    try {
      const user = await verifyMfa(challengeToken, code);

      router.replace(user.role === "STUDENT" ? "/student" : "/admin");
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : "Unable to verify code");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-page">
      <section className="login-art">
        <Logo />
        <div className="landingpage-content">
          <h1>Meals Queue Coordination</h1>
          <p>
            MealQ coordinates cafeteria serving batches so that students know
            when to serve and staff can manage the queue flow efficiently.
          </p>
        </div>
      </section>

      <section className="auth-panel">
        <div className="auth-box">
          {!mfaStep ? (
            <>
              <h1>Welcome!</h1>
              <p>Sign in with your MealQ username or email.</p>

              {error && (
                <div className="alert" style={{ marginBottom: 15 }}>
                  {error}
                </div>
              )}

              <form className="auth-form" onSubmit={submitLogin}>
                <Field
                  label="Username or email"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  autoComplete="username"
                  required
                />

                <Field
                  label="Password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  required
                />

                <button className="btn" disabled={busy}>
                  {busy ? "Signing in…" : "Sign in"}
                </button>

                <div className="auth-links">
                  <span />
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "flex-start",
                      gap: 8,
                      width: "100%",
                      marginTop: 12,
                    }}
                  >
                    <Link href="/forgot-password">Forgot password?</Link>
                    <Link href="/verify-email">Resend verification email</Link>
                  </div>
                </div>
              </form>

              <div className="auth-footer">
                Student without an account?{" "}
                <Link href="/register">Create a student account</Link>
                <br />
                <span style={{ display: "inline-block", marginTop: 8 }}>
                  First Admin?{" "}
                  <Link href="/setup">Initial Super Admin setup</Link>
                </span>
              </div>
            </>
          ) : (
            <>
              <h1>Verify your login</h1>

              <p>
                We sent a 6-digit verification code to your email address. Enter
                the code below to continue.
              </p>

              {error && (
                <div className="alert" style={{ marginBottom: 15 }}>
                  {error}
                </div>
              )}

              <form className="auth-form" onSubmit={submitMfa}>
                <Field
                  label="Verification code"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  inputMode="numeric"
                  maxLength={6}
                  autoComplete="one-time-code"
                  required
                />

                <button className="btn" disabled={busy}>
                  {busy ? "Verifying…" : "Verify code"}
                </button>
              </form>
            </>
          )}
        </div>
      </section>
    </div>
  );
}
