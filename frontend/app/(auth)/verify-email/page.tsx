"use client";
import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import Logo from "@/components/Logo";
import { api, ApiError } from "@/lib/api";

function VerifyContent() {
  const p = useSearchParams();
  const [status, setStatus] = useState("Verifying your email…");
  useEffect(() => {
    const t = p.get("token");
    if (!t) {
      setStatus("No verification token was provided.");
      return;
    }
    api
      .verifyEmail(t)
      .then(() => setStatus("Your email is verified. You can now sign in."))
      .catch((e) =>
        setStatus(e instanceof ApiError ? e.detail : "Verification failed"),
      );
  }, [p]);
  return (
    <div className="login-page">
      <section className="login-art">
        <Logo />
        <div>
          <h1>Almost there.</h1>
          <p>Email verification activates your MealQ account before login.</p>
        </div>
      </section>
      
      <section className="auth-panel">
        <div className="auth-box">
          <Logo />
          <h1>Email verification</h1>
          <p>{status}</p>
          <Link
            href="/login"
            className="btn"
            style={{ display: "inline-block", textDecoration: "none" }}
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