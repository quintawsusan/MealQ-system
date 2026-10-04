"use client";
import { useEffect, useRef, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { Student } from "@/types";
import { Field, SelectField } from "@/components/Field";
import { Toast, useToast } from "@/components/Toast";

export default function Students() {
  const [items, setItems] = useState<Student[]>([]);
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<Student | null>(null);
  const [className, setClassName] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);
  const { message, show } = useToast();
  async function load() {
    try {
      setItems(await api.students());
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not load students");
    }
  }
  useEffect(() => {
    load();
  }, []);
  function edit(s: Student) {
    setSelected(s);
    setClassName(s.class_name || "");
    setOpen(true);
  }
  async function save(e: React.FormEvent) {
    e.preventDefault();
    if (!selected) return;
    try {
      await api.updateStudent(selected.student_id, { class_name: className });
      setOpen(false);
      show("Student updated");
      load();
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not update student");
    }
  }
  async function remove(id: string) {
    if (
      !confirm(
        "Delete this student profile? The backend will block deletion when session history exists.",
      )
    )
      return;
    try {
      await api.deleteStudent(id);
      show("Student deleted");
      load();
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not delete student");
    }
  }
  async function upload() {
    const f = fileRef.current?.files?.[0];
    if (!f) return;
    try {
      const result = await api.importStudents(f);
      show(`Imported ${result.total_created} students`);
      load();
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "CSV import failed");
    }
  }
  return (
    <>
      <Toast message={message} />
      <div className="page-header">
        <div>
          <div className="eyebrow">Student management</div>
          <h1 className="page-title">Students</h1>
          <p className="page-subtitle">
            Active student profiles used when meal sessions generate serving
            batches.
          </p>
        </div>
        <div className="toolbar">
          <input
            ref={fileRef}
            type="file"
            accept=".csv"
            hidden
            onChange={upload}
          />
          <button
            className="btn secondary"
            onClick={() => fileRef.current?.click()}
          >
            Import CSV
          </button>
        </div>
      </div>
      <div className="notice" style={{ marginBottom: 15 }}>
        CSV columns required by the backend:{" "}
        <strong>student_number, first_name, last_name, class_name</strong>. Bulk
        import generates the username and temporary password on the server.
      </div>
      <div className="card">
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Student no.</th>
                <th>Class</th>
                <th>Student ID</th>
                <th>Created</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {items.map((s) => (
                <tr key={s.student_id}>
                  <td>
                    <strong>#{s.student_number}</strong>
                  </td>
                  <td>{s.class_name || "—"}</td>
                  <td style={{ fontSize: 10 }}>{s.student_id}</td>
                  <td>{new Date(s.created_at).toLocaleDateString()}</td>
                  <td>
                    <div className="actions">
                      <button
                        className="btn secondary small"
                        onClick={() => edit(s)}
                      >
                        Edit class
                      </button>
                      <button
                        className="btn danger small"
                        onClick={() => remove(s.student_id)}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {!items.length && (
                <tr>
                  <td colSpan={5}>
                    <div className="empty">No active students found.</div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      {open && selected && (
        <div className="modal-backdrop">
          <div className="modal">
            <div className="modal-header">
              <h2>Edit student</h2>
              <button className="close" onClick={() => setOpen(false)}>
                ×
              </button>
            </div>
            <form className="auth-form" onSubmit={save}>
              <div className="notice">Student #{selected.student_number}</div>
              <SelectField
                label="Class"
                value={className}
                onChange={(e) => setClassName(e.target.value)}
              >
                <option>Anita B</option>
                <option>Ada Lab</option>
                <option>Lovelace</option>
              </SelectField>
              <button className="btn">Save class</button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
