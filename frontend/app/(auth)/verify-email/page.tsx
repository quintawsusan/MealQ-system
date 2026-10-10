"use client";
import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import Logo from "@/components/Logo";
import { api, ApiError } from "@/lib/api";

function VerifyContent() {
  const p = useSearchParams();
  const [status, setStatus] = useState("Verifying your email…");
  const [email, setEmail] = useState("");
  const [resendMessage, setResendMessage] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const token = p.get("token");

    if (!token) {
      setStatus("Invalid verification link. You can request a new link below.");
      return;
    }

    let cancelled = false;

    api
      .verifyEmail(token)
      .then(() => {
        if (!cancelled) {
          setStatus("Your email is verified. You can now sign in.");
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setStatus(
            e instanceof ApiError
              ? e.detail
              : "Verification failed. You can request a new link below.",
          );
        }
      });

    return () => {
      cancelled = true;
    };
  }, [p]);

  async function handleResend(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setResendMessage("");

    try {
      const result = await api.resendVerification(email.trim());
      setResendMessage(result.detail);
    } catch (e) {
      setResendMessage(
        e instanceof ApiError
          ? e.detail
          : "Unable to request a verification email. Please try again.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-page">
      <section className="login-art">
        <Logo />
        <div>
          <h1>Email Verification </h1>
          <p>Activate your MealQ account before login.</p>
        </div>
      </section>

      <section className="auth-panel">
        <div className="auth-box">
          <Logo />
          <h1>Email verification</h1>
          <p>{status}</p>

          <form
            className="auth-form"
            onSubmit={handleResend}
            style={{ marginTop: 24 }}
          >
            <h2>Need a new verification link?</h2>
            <p>Enter the email address you used to register.</p>

            <label htmlFor="verification-email">Email address</label>
            <input
              id="verification-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              placeholder="user@gmail.com"
              required
            />

            <button className="btn" type="submit" disabled={busy}>
              {busy ? "Sending…" : "Resend verification email"}
            </button>

            {resendMessage && (
              <p role="status" aria-live="polite">{resendMessage}</p>
            )}
          </form>

          <Link
            href="/login"
            className="btn"
            style={{
              display: "inline-block",
              textDecoration: "none",
              textAlign: "center",
              width: "30%",
              marginTop: 16,
            }}
          >
            Go to sign in
          </Link>
        </div>
      </section>
    </div>
  );
}

export default function Verify() {
  return (
    <Suspense fallback={<div>Verifying your email…</div>}>
      <VerifyContent />
    </Suspense>
  );
}
