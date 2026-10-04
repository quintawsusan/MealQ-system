"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type {
  Schedule,
  Session,
  MyBatch,
  User,
  MealType,
} from "@/types";
import { Toast, useToast } from "@/components/Toast";

function time(t: string) {
  return t?.slice(0, 5) || "";
}

function date(d: string) {
  return new Date(`${d}T00:00:00`).toLocaleDateString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

export default function StudentHome() {
  const [user, setUser] = useState<User | null>(null);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [types, setTypes] = useState<MealType[]>([]);
  const [active, setActive] = useState<{
    session: Session;
    batch: MyBatch;
  } | null>(null);

  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  const { message, show } = useToast();

  async function load() {
    try {
      const [u, ss, tt, session] = await Promise.all([
        api.me(),
        api.schedules(),
        api.mealTypes(),
        api.activeSession(),
      ]);

      setUser(u);
      setSchedules(ss);
      setTypes(tt);

      if (session) {
        const batch = await api.myBatch(session.session_id);

        setActive({
          session,
          batch,
        });
      } else {
        setActive(null);
      }
    } catch (e) {
      show(
        e instanceof ApiError
          ? e.detail
          : "Could not load meal information",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function respond(r: "GOING" | "SKIPPED") {
    if (!active || !active.batch.response_window_open) return;

    setBusy(true);

    try {
      await api.respond(active.session.session_id, r);

      show(
        r === "GOING"
          ? "You are marked as going."
          : "You are marked as skipping.",
      );

      await load();
    } catch (e) {
      show(
        e instanceof ApiError
          ? e.detail
          : "Response has not been successfully submitted",
      );
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner" />
        Loading MealQ…
      </div>
    );
  }

  const typeName = (id: string) =>
    types.find((t) => t.meal_id === id)?.name || "Meal";

  const activeSchedules = schedules.filter((s) => s.is_active);

  const batchStatus = active?.batch.batch_status;

  return (
    <>
      <Toast message={message} />

      <div className="page-header">
        <div>
          <div className="eyebrow">Student dashboard</div>

          <h1 className="page-title">
            Hello, {user?.first_name}.
          </h1>

          <p className="page-subtitle">
            Check your assigned batch and upcoming cafeteria schedule.
          </p>
        </div>
      </div>

      <div className="card section-gap">
        <h3 className="card-title">How MealQ works</h3>

        <div className="grid grid-3" style={{ marginTop: 15 }}>
          <div>
            <strong>1. Wait for your batch</strong>

            <p className="muted" style={{ fontSize: 12 }}>
              Students are grouped according to the active session batch size.
            </p>
          </div>

          <div>
            <strong>2. Respond when called</strong>

            <p className="muted" style={{ fontSize: 12 }}>
              Choose “I’m going” or “I’m skipping” during the response window.
            </p>
          </div>

          <div>
            <strong>3. Head to the cafeteria</strong>

            <p className="muted" style={{ fontSize: 12 }}>
              A called batch moves through the serving flow at the configured
              interval.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card hero-card">
          <div className="card-title">
            {!active
              ? "Your next meal"
              : batchStatus === "WAITING"
                ? "Your batch is waiting"
                : batchStatus === "CALLED"
                  ? active.batch.response_window_open
                    ? "Your batch is being called"
                    : "Response window closed"
                  : batchStatus === "COMPLETED"
                    ? "Your batch is completed"
                    : "Your meal status"}
          </div>

          {active ? (
            <>
              <div
                className="muted"
                style={{ margin: "8px 0 14px" }}
              >
                Batch {active.batch.batch_number} · Position{" "}
                {active.batch.student_position}
              </div>

              <div
                className="call-number"
                style={{ fontSize: "34px" }}
              >
                {active.batch.student_number}
              </div>

              <p className="muted">
                {batchStatus === "WAITING" ? (
                  "Please wait. Your batch will be called when it is your turn."
                ) : batchStatus === "CALLED" &&
                  active.batch.response_window_open ? (
                  <>
                    Your batch has been called. Respond within{" "}
                    {active.session.response_window} seconds.
                  </>
                ) : batchStatus === "CALLED" ? (
                  "The response window is closed. Please wait for the next update."
                ) : batchStatus === "COMPLETED" ? (
                  "Your batch has completed its serving process."
                ) : (
                  "Please wait for your batch status to update."
                )}
              </p>

              <div className="response-actions">
                <button
                  className={`response-btn go ${
                    active.batch.response === "GOING"
                      ? "selected"
                      : ""
                  }`}
                  disabled={
                    busy ||
                    batchStatus !== "CALLED" ||
                    !active.batch.response_window_open ||
                    active.batch.response !== "NO_RESPONSE"
                  }
                  onClick={() => respond("GOING")}
                >
                  I’m going
                </button>

                <button
                  className={`response-btn skip ${
                    active.batch.response === "SKIPPED"
                      ? "selected"
                      : ""
                  }`}
                  disabled={
                    busy ||
                    batchStatus !== "CALLED" ||
                    !active.batch.response_window_open ||
                    active.batch.response !== "NO_RESPONSE"
                  }
                  onClick={() => respond("SKIPPED")}
                >
                  I’m skipping
                </button>
              </div>
            </>
          ) : (
            <>
              <div
                className="call-number"
                style={{ fontSize: 44 }}
              >
                —
              </div>

              <div>
                Wait for your serving batch to be displayed.
              </div>
            </>
          )}
        </div>

        <div className="card">
          <h3 className="card-title">Upcoming meals</h3>

          {activeSchedules.length === 0 ? (
            <div className="empty">
              No active schedules.
            </div>
          ) : (
            <div
              style={{
                display: "grid",
                gap: 0,
                marginTop: 12,
              }}
            >
              {activeSchedules.slice(0, 5).map((s) => (
                <div
                  key={s.schedule_id}
                  style={{
                    position: "relative",
                    padding: "11px 90px 11px 0",
                    borderBottom: "1px solid #f1efed",
                    width: "100%",
                    boxSizing: "border-box",
                  }}
                >
                  <div>
                    <strong style={{ fontSize: 13 }}>
                      {typeName(s.meal_type_id)}
                    </strong>

                    <div
                      className="muted"
                      style={{
                        fontSize: 11,
                        marginTop: 3,
                      }}
                    >
                      {date(s.meal_date)} ·{" "}
                      {time(s.start_time)}–
                      {time(s.end_time)}
                    </div>

                    <div
                      style={{
                        fontSize: 12,
                        marginTop: 6,
                      }}
                    >
                      <strong>Menu:</strong>{" "}
                      {s.menu_description || "Menu not provided"}
                    </div>
                  </div>

                  <span
                    className="badge active"
                    style={{
                      position: "absolute",
                      right: 20,
                      top: 11,
                    }}
                  >
                    Active
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}