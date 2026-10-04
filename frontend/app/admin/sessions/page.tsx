"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import type { MealType, Schedule, Session } from "@/types";
import { Field, SelectField } from "@/components/Field";
import { Toast, useToast } from "@/components/Toast";

export default function Sessions() {
  const [items, setItems] = useState<Session[]>([]);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [types, setTypes] = useState<MealType[]>([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    schedule_id: "",
    batch_size: "5",
    release_interval_seconds: "120",
    response_window: "60",
  });
  const { message, show } = useToast();

  async function load() {
    try {
      const [a, b, c] = await Promise.all([
        api.sessions(),
        api.schedules("active_only=true"),
        api.mealTypes(),
      ]);
      setItems(a);
      setSchedules(b);
      setTypes(c);
      if (!form.schedule_id && b[0])
        setForm((f) => ({ ...f, schedule_id: b[0].schedule_id }));
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not load sessions");
    }
  }
  useEffect(() => {
    load();
  }, []);

  async function create(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.createSession({
        ...form,
        batch_size: Number(form.batch_size),
        release_interval_seconds: Number(form.release_interval_seconds),
        response_window: Number(form.response_window),
      });
      setOpen(false);
      show("Meal session created");
      load();
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not create session");
    }
  }

  async function action(
    id: string,
    a: "start" | "pause" | "resume" | "complete" | "advance" | "delete",
  ) {
    try {
      if (a === "start") await api.startSession(id);
      if (a === "pause") await api.pauseSession(id);
      if (a === "resume") await api.resumeSession(id);
      if (a === "complete") await api.completeSession(id);
      if (a === "advance") await api.advance(id, true);
      if (a === "delete") {
        const confirmed = window.confirm(
          "Delete this scheduled meal session? This cannot be undone.",
        );

        if (!confirmed) return;

        console.log("DELETE CLICKED", id);
        await api.deleteSession(id);
        console.log("DELETE REQUEST FINISHED", id);
      }

      show(`Session ${a} complete`);
      await load();
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Action failed");
    }
  }

  const typeFor = (sid: string) => {
    const s = schedules.find((x) => x.schedule_id === sid);
    return types.find((t) => t.meal_id === s?.meal_type_id)?.name || "Meal";
  };

  return (
    <>
      <Toast message={message} />
      <div className="page-header">
        <div>
          <div className="eyebrow">Operations</div>
          <h1 className="page-title">Meal sessions</h1>
          <p className="page-subtitle">
            Create a session from a schedule, then control its serving flow.
          </p>
        </div>

        <button className="btn" onClick={() => setOpen(true)}>
          Create session
        </button>
      </div>

      <div className="card">
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Meal</th>
                <th>Status</th>
                <th>Batch size</th>
                <th>Release</th>
                <th>Response</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((s) => (
                <tr key={s.session_id}>
                  <td>
                    <strong>{typeFor(s.schedule_id)}</strong>
                    <div className="muted" style={{ fontSize: 10 }}>
                      {s.schedule_id.slice(0, 8)}…
                    </div>
                  </td>
                  <td>
                    <span className={`badge ${s.status.toLowerCase()}`}>
                      {s.status}
                    </span>
                  </td>
                  <td>{s.batch_size}</td>
                  <td>{s.release_interval_seconds}s</td>
                  <td>{s.response_window}s</td>
                  <td>
                    <div className="actions">
                      {s.status === "SCHEDULED" && (
                        <>
                          <button
                            className="btn small"
                            onClick={() => action(s.session_id, "start")}
                          >
                            Start
                          </button>

                          <button
                            className="btn danger small"
                            onClick={() => action(s.session_id, "delete")}
                          >
                            Delete
                          </button>
                        </>
                      )}
                      {s.status === "ACTIVE" && (
                        <>
                          <button
                            className="btn secondary small"
                            onClick={() => action(s.session_id, "pause")}
                          >
                            Pause
                          </button>
                          <button
                            className="btn small"
                            onClick={() => action(s.session_id, "advance")}
                          >
                            Advance
                          </button>
                          <button
                            className="btn danger small"
                            onClick={() => action(s.session_id, "complete")}
                          >
                            Complete
                          </button>
                        </>
                      )}
                      {s.status === "PAUSED" && (
                        <button
                          className="btn small"
                          onClick={() => action(s.session_id, "resume")}
                        >
                          Resume
                        </button>
                      )}
                      <Link
                        className="btn secondary small"
                        href={`/admin/sessions/${s.session_id}`}
                      >
                        Monitor
                      </Link>
                    </div>
                  </td>
                </tr>
              ))}
              {!items.length && (
                <tr>
                  <td colSpan={6}>
                    <div className="empty">No meal sessions yet.</div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      {open && (
        <div className="modal-backdrop">
          <div className="modal">
            <div className="modal-header">
              <h2>Create meal session</h2>
              <button className="close" onClick={() => setOpen(false)}>
                ×
              </button>
            </div>
            <form className="form-grid" onSubmit={create}>
              <div className="full">
                <SelectField
                  label="Schedule"
                  value={form.schedule_id}
                  onChange={(e) =>
                    setForm({ ...form, schedule_id: e.target.value })
                  }
                  required
                >
                  <option value="">Select schedule</option>
                  {schedules.map((s) => (
                    <option key={s.schedule_id} value={s.schedule_id}>
                      {typeFor(s.schedule_id)} · {s.meal_date} ·{" "}
                      {s.start_time.slice(0, 5)}
                    </option>
                  ))}
                </SelectField>
              </div>
              <Field
                label="Batch size"
                type="number"
                min="1"
                value={form.batch_size}
                onChange={(e) =>
                  setForm({ ...form, batch_size: e.target.value })
                }
              />
              <Field
                label="Release interval (seconds)"
                type="number"
                min="1"
                value={form.release_interval_seconds}
                onChange={(e) =>
                  setForm({ ...form, release_interval_seconds: e.target.value })
                }
              />
              <Field
                label="Response window (seconds)"
                type="number"
                min="1"
                value={form.response_window}
                onChange={(e) =>
                  setForm({ ...form, response_window: e.target.value })
                }
              />
              <div className="full">
                <button className="btn">Create session</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
