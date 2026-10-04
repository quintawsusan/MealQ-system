"use client";
import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { MealType } from "@/types";
import { Field } from "@/components/Field";
import { Toast, useToast } from "@/components/Toast";

export default function MealTypes() {
  const [items, setItems] = useState<MealType[]>([]);
  const [open, setOpen] = useState(false);
  const [edit, setEdit] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const { message, show } = useToast();
  async function load() {
    try {
      setItems(await api.mealTypes());
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not load meal types");
    }
  }
  useEffect(() => {
    load();
  }, []);
  function start(x?: MealType) {
    setEdit(x?.meal_id || null);
    setName(x?.name || "");
    setDescription(x?.description || "");
    setOpen(true);
  }
  async function save(e: React.FormEvent) {
    e.preventDefault();
    try {
      if (edit) await api.updateMealType(edit, { name, description });
      else await api.createMealType({ name, description });
      setOpen(false);
      show("Meal type saved");
      load();
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not save meal type");
    }
  }
  async function del(id: string) {
    if (!confirm("Delete this meal type?")) return;
    try {
      await api.deleteMealType(id);
      show("Meal type deleted");
      load();
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not delete meal type");
    }
  }
  return (
    <>
      <Toast message={message} />
      <div className="page-header">
        <div>
          <h1 className="page-title">Meal types</h1>
          <p className="page-subtitle">
            Maintain the meal categories referenced by schedules.
          </p>
        </div>
        <button className="btn" onClick={() => start()}>
          Add meal type
        </button>
      </div>
      <div className="grid grid-3">
        {items.map((x) => (
          <div className="card" key={x.meal_id}>
            <h3 className="card-title">{x.name}</h3>
            <p className="muted" style={{ fontSize: 12, minHeight: 34 }}>
              {x.description || "No description"}
            </p>
            <div className="actions">
              <button className="btn secondary small" onClick={() => start(x)}>
                Edit
              </button>
              <button
                className="btn danger small"
                onClick={() => del(x.meal_id)}
              >
                Delete
              </button>
            </div>
          </div>
        ))}
        {!items.length && <div className="card empty">No meal types yet.</div>}
      </div>
      {open && (
        <div className="modal-backdrop">
          <div className="modal">
            <div className="modal-header">
              <h2>{edit ? "Edit meal type" : "Add meal type"}</h2>
              <button className="close" onClick={() => setOpen(false)}>
                ×
              </button>
            </div>
            <form className="auth-form" onSubmit={save}>
              <Field
                label="Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                maxLength={30}
                required
              />
              <Field
                label="Description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                maxLength={255}
              />
              <button className="btn">Save meal type</button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
