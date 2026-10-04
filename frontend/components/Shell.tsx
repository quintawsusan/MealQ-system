"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Logo from "./Logo";
import { api } from "@/lib/api";
import { logout } from "@/lib/auth";
import type { User } from "@/types";

export default function Shell({children,role,}: {children: React.ReactNode;role: "STUDENT" | "ADMIN";}) {
  const path = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  useEffect(() => {
    api
      .me()
      .then(setUser)
      .catch(() => {});
  }, []);
    
  const links =
    role === "STUDENT"
      ? [
          ["/student", "Overview"],
          ["/student/profile", "Profile"],
        ]
      : [
          ["/admin", "Dashboard"],
          ["/admin/sessions", "Meal sessions"],
          ["/admin/schedules", "Schedules"],
          ["/admin/meal-types", "Meal types"],
          ["/admin/students", "Students"],
          ["/admin/users", "Users"],
          ["/admin/profile", "Profile"],
        ];
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Logo />
        <div className="side-label">
          {role === "STUDENT" ? "Student space" : "Administration"}
        </div>
        <nav>
          {links.map(([href, label]) => (
            <Link
              key={href}
              href={href}
              className={
                path === href || path.startsWith(href + "/") ? "active" : ""
              }
            >
              <span className="nav-dot" />
              {label}
            </Link>
          ))}
        </nav>
        <div className="side-bottom">
          <div className="user-mini">
            <div className="avatar">{user?.first_name?.[0] || "M"}</div>
            <div>
              <strong>
                {user ? `${user.first_name} ${user.last_name}` : "MealQ user"}
              </strong>
              <small>{user?.role?.replace("_", " ")}</small>
            </div>
          </div>
          <button
            className="logout-btn"
            onClick={async () => {
              await logout();
              router.replace("/login");
            }}
          >
            Sign out
          </button>
        </div>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  );
}
