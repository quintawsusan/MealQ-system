"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import type { MealType, Schedule, Session, Monitor, Student } from "@/types";
import { Toast, useToast } from "@/components/Toast";

export default function AdminHome() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  const [types, setTypes] = useState<MealType[]>([]);
  const [monitor, setMonitor] = useState<Monitor | null>(null);
  const { message, show } = useToast();
  async function load() {
    try {
      const [ss, sch, st, mt] = await Promise.all([
        api.sessions(),
        api.upcoming(7),
        api.students(),
        api.mealTypes(),
      ]);
      setSessions(ss);
      setSchedules(sch);
      setStudents(st);
      setTypes(mt);
      const active = ss.find((s) => s.status === "ACTIVE");
      if (active) setMonitor(await api.monitor(active.session_id));
      else setMonitor(null);
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not load dashboard");
    }
  }
  useEffect(() => {
    load();
    const t = setInterval(load, 4000);
    return () => clearInterval(t);
  }, []);
  const active = sessions.find((s) => s.status === "ACTIVE");

  return (
    <>
      <Toast message={message} />
      <div className="page-header">
        <div>
          <div className="eyebrow">Administration</div>
          <h1 className="page-title">MealQ Management Room</h1>
          <p className="page-subtitle">
            Manage schedules and observe the serving flow without changing
            backend rules.
          </p>
        </div>

        <div className="toolbar">
          <Link className="btn" href="/admin/sessions">
            Open meal sessions
          </Link>
        </div>
      </div>

      <div className="grid grid-4">
        <div className="card stat">
          <div className="label">Students</div>
          <div className="value">{students.length}</div>
          <div className="hint">Active student profiles</div>
        </div>

        <div className="card stat">
          <div className="label">Schedules</div>
          <div className="value">{schedules.length}</div>
          <div className="hint">Upcoming active meals</div>
        </div>

        <div className="card stat">
          <div className="label">Meal types</div>
          <div className="value">{types.length}</div>
          <div className="hint">Configured categories</div>
        </div>

        <div className="card stat">
          <div className="label">Session</div>
          <div className="value" style={{ fontSize: 18 }}>
            {active ? "ACTIVE" : "—"}
          </div>

          <div className="hint">Current meal session</div>
        </div>
      </div>

      {monitor ? (
        <div className="card section-gap">
          <div className="page-header" style={{ marginBottom: 12 }}>
            <div>
              <h3 className="card-title">Live serving monitor</h3>
              <p className="muted" style={{ fontSize: 12 }}>
                Batch {monitor.current_batch?.batch_number ?? "—"} is currently
                called.
              </p>
            </div>

            <Link
              href={`/admin/sessions/${monitor.session.session_id}`}
              className="btn secondary small"
            >
              Open session
            </Link>

          </div>

          <div className="grid grid-4">
            <div>
              <small className="muted">Total</small>
              <div className="kpi-ring">{monitor.total_students}</div>
            </div>

            <div>
              <small className="muted">Going</small>
              <div className="kpi-ring">{monitor.going}</div>
            </div>

            <div>
              <small className="muted">Skipped</small>
              <div className="kpi-ring">{monitor.skipped}</div>
            </div>

            <div>
              <small className="muted">No response</small>
              <div className="kpi-ring">{monitor.no_response}</div>
            </div>
            
          </div>
        </div>
      ) : (
        <div className="card section-gap empty">
          <strong>No active meal session</strong>
          <div>
            Start a scheduled session from Meal sessions when service is ready.
          </div>
          </div>
          
      )}
      <div className="grid grid-2 section-gap">
        <div className="card">
          <h3 className="card-title">Upcoming schedule</h3>
          <div style={{ marginTop: 10 }}>
            {schedules.slice(0, 6).map((s) => (
              <div
                key={s.schedule_id}
                style={{ padding: "11px 0", borderBottom: "1px solid #f1efed" }}
              >
                <strong>
                  {types.find((t) => t.meal_id === s.meal_type_id)?.name ||
                    "Meal"}
                </strong>
                <div className="muted" style={{ fontSize: 11 }}>
                  {s.meal_date} · {s.start_time.slice(0, 5)}–
                  {s.end_time.slice(0, 5)}
                </div>
              </div>
            ))}
            {!schedules.length && (
              <div className="empty">No upcoming schedules.</div>
            )}
          </div>
        </div>
        
        <div className="card">
          <h3 className="card-title">Quick actions</h3>
          <div className="grid" style={{ marginTop: 14 }}>
            <Link className="btn secondary" href="/admin/schedules">
              Create or edit a meal schedule
            </Link>
            <Link className="btn secondary" href="/admin/students">
              Manage students / import CSV
            </Link>
            <Link className="btn secondary" href="/admin/meal-types">
              Manage meal types
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}
