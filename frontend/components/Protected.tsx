"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { Role, User } from "@/types";
export default function Protected({
  children,
  roles,
}: {
  children: React.ReactNode;
  roles?: Role[];
}) {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  useEffect(() => {
    api
      .me()
      .then((u: User) => {
        if (roles && !roles.includes(u.role)) {
          router.replace(u.role === "STUDENT" ? "/student" : "/admin");
          return;
        }
        setReady(true);
      })
      .catch(() => router.replace("/login"));
  }, [router, roles]);
  return ready ? (
    <>{children}</>
  ) : (
    <div className="loading-screen">
      <div className="spinner" />
      Checking your session…
    </div>
  );
}
