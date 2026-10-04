"use client";
import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { MealType, Schedule } from "@/types";
import { Field, SelectField } from "@/components/Field";
import { Toast, useToast } from "@/components/Toast";

const empty = {
  meal_type_id: "",
  meal_date: "",
  start_time: "06:20",
  end_time: "07:00",
  menu_description: "",
  is_active: true,
};
export default function Schedules() {
  const [items, setItems] = useState<Schedule[]>([]);
  const [types, setTypes] = useState<MealType[]>([]);
  const [open, setOpen] = useState(false);
  const [edit, setEdit] = useState<string | null>(null);
  const [form, setForm] = useState(empty);
  const { message, show } = useToast();
  async function load() {
    try {
      setItems(await api.schedules());
      setTypes(await api.mealTypes());
    } catch (e) {
      show(
        e instanceof ApiError
          ? e.detail
          : "Oops! Could not load updated meal schedule",
      );
    }
  }

  useEffect(() => {
    load();
  }, []);

  function newItem() {
    setEdit(null);
    setForm({
      ...empty,
      meal_date: new Date().toISOString().slice(0, 10),
      meal_type_id: types[0]?.meal_id || "",
    });
    setOpen(true);
  }

  function editItem(s: Schedule) {
    setEdit(s.schedule_id);
    setForm({
      meal_type_id: s.meal_type_id,
      meal_date: s.meal_date,
      start_time: s.start_time.slice(0, 5),
      end_time: s.end_time.slice(0, 5),
      menu_description: s.menu_description || "",
      is_active: s.is_active,
    });
    setOpen(true);
  }

  async function save(e: React.FormEvent) {
    e.preventDefault();
    try {
      if (edit) await api.updateSchedule(edit, form);
      else await api.createSchedule(form);
      setOpen(false);
      show("Schedule saved");
      load();
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not save schedule");
    }
  }

  async function activate(id: string) {
    try {
      const schedule = items.find((s) => s.schedule_id === id);

      if (!schedule) {
        show("Schedule not found.");
        return;
      }

      await api.updateSchedule(id, {
        meal_type_id: schedule.meal_type_id,
        meal_date: schedule.meal_date,
        start_time: schedule.start_time.slice(0, 5),
        end_time: schedule.end_time.slice(0, 5),
        menu_description: schedule.menu_description || "",
        is_active: true,
      });

      show("Schedule activated.");
      await load();
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not activate schedule");
    }
  }

  async function deactivate(id: string) {
    if (!confirm("Deactivate this schedule?")) return;
    try {
      await api.deactivateSchedule(id);
      show("Schedule deactivated");
      load();
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not deactivate schedule");
    }
  }

  return (
    <>
      <Toast message={message} />
      <div className="page-header">
        <div>
          <div className="eyebrow">Planning</div>
          <h1 className="page-title">Meal schedules</h1>
          <p className="page-subtitle">
            Define when each meal is available and what is being served.
          </p>
        </div>

        <button className="btn" onClick={newItem}>
          Add schedule
        </button>
      </div>

      <div className="card">
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Meal</th>
                <th>Time</th>
                <th>Menu</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {items.map((s) => (
                <tr key={s.schedule_id}>
                  <td>{s.meal_date}</td>
                  <td>
                    <strong>
                      {types.find((t) => t.meal_id === s.meal_type_id)?.name ||
                        "—"}
                    </strong>
                  </td>
                  <td>
                    {s.start_time.slice(0, 5)}–{s.end_time.slice(0, 5)}
                  </td>
                  <td>{s.menu_description || "—"}</td>
                  <td>
                    <span
                      className={`badge ${s.is_active ? "active" : "completed"}`}
                    >
                      {s.is_active ? "ACTIVE" : "INACTIVE"}
                    </span>
                  </td>
                  <td>
                    <div className="actions">
                      <button
                        className="btn secondary small"
                        onClick={() => editItem(s)}
                      >
                        Edit
                      </button>

                      {s.is_active ? (
                        <button
                          className="btn secondary small"
                          onClick={() => deactivate(s.schedule_id)}
                        >
                          Deactivate
                        </button>
                      ) : (
                        <button
                          className="btn"
                          onClick={() => activate(s.schedule_id)}
                        >
                          Activate
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {!items.length && (
                <tr>
                  <td colSpan={6}>
                    <div className="empty">No schedules updated.</div>
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
              <h2>{edit ? "Edit schedule" : "Add schedule"}</h2>
              <button className="close" onClick={() => setOpen(false)}>
                ×
              </button>
            </div>

            <form className="form-grid" onSubmit={save}>
              <SelectField
                label="Meal type"
                value={form.meal_type_id}
                onChange={(e) =>
                  setForm({ ...form, meal_type_id: e.target.value })
                }
                required
              >
                <option value="">Select meal type</option>
                {types.map((t) => (
                  <option key={t.meal_id} value={t.meal_id}>
                    {t.name}
                  </option>
                ))}
              </SelectField>

              <Field
                label="Date"
                type="date"
                value={form.meal_date}
                onChange={(e) =>
                  setForm({ ...form, meal_date: e.target.value })
                }
                required
              />

              <Field
                label="Start time"
                type="time"
                value={form.start_time}
                onChange={(e) =>
                  setForm({ ...form, start_time: e.target.value })
                }
                required
              />

              <Field
                label="End time"
                type="time"
                value={form.end_time}
                onChange={(e) => setForm({ ...form, end_time: e.target.value })}
                required
              />

              <div className="full">
                <Field
                  label="Menu description"
                  value={form.menu_description}
                  onChange={(e) =>
                    setForm({ ...form, menu_description: e.target.value })
                  }
                />
              </div>

              <div className="full">
                <button className="btn">Save schedule</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
