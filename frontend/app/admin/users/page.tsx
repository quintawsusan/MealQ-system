"use client";
import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { Role, User } from "@/types";
import { Field, SelectField } from "@/components/Field";
import { Toast, useToast } from "@/components/Toast";
export default function Users() {
  const [items, setItems] = useState<User[]>([]);
  const [me, setMe] = useState<User | null>(null);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    user_name: "",
    email: "",
    password: "",
  });
  const { message, show } = useToast();
  async function load() {
    try {
      const [u, users] = await Promise.all([api.me(), api.users()]);
      setMe(u);
      setItems(users);
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not load users");
    }
  }
  useEffect(() => {
    load();
  }, []);
  async function create(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.createAdmin(form);
      setOpen(false);
      show("Admin account created");
      load();
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not create admin");
    }
  }
  async function toggle(u: User) {
    try {
      await api.updateUser(u.user_id, { is_active: !u.is_active });
      show("User updated");
      load();
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not update user");
    }
  }
  async function role(u: User, e: React.ChangeEvent<HTMLSelectElement>) {
    try {
      await api.updateUser(u.user_id, { role: e.target.value as Role });
      show("Role updated");
      load();
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not change role");
    }
  }
  async function unlock(u: User) {
    try {
      await api.unlock(u.user_id);
      show("Account unlocked");
      load();
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not unlock account");
    }
  }
  async function remove(u: User) {
    if (!confirm(`Delete ${u.user_name}?`)) return;
    try {
      await api.deleteUser(u.user_id);
      show("User deleted");
      load();
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not delete user");
    }
  }
  const canCreate = me?.role === "SUPER_ADMIN";
  return (
    <>
      <Toast message={message} />
      <div className="page-header">
        <div>
          <div className="eyebrow">Access control</div>
          <h1 className="page-title">Users</h1>
          <p className="page-subtitle">
            Manage student accounts and, for Super Admins, administrative
            accounts.
          </p>
        </div>
        {canCreate && (
          <button className="btn" onClick={() => setOpen(true)}>
            Create admin
          </button>
        )}
      </div>
      <div className="card">
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>User</th>
                <th>Role</th>
                <th>Verification</th>
                <th>Account</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((u) => (
                <tr key={u.user_id}>
                  <td>
                    <strong>
                      {u.first_name} {u.last_name}
                    </strong>
                    <div className="muted" style={{ fontSize: 11 }}>
                      @{u.user_name} · {u.email}
                    </div>
                  </td>
                  <td>
                    {canCreate &&
                    u.role !== "SUPER_ADMIN" &&
                    u.user_id !== me?.user_id ? (
                      <SelectField
                        label=""
                        value={u.role}
                        onChange={(e) => role(u, e)}
                      >
                        <option>STUDENT</option>
                        <option>ADMIN</option>
                      </SelectField>
                    ) : (
                      <span className="badge scheduled">{u.role}</span>
                    )}
                  </td>
                  <td>
                    <span
                      className={`badge ${u.email_verified ? "active" : "error"}`}
                    >
                      {u.email_verified ? "VERIFIED" : "UNVERIFIED"}
                    </span>
                  </td>
                  <td>
                    <span
                      className={`badge ${u.is_active && !u.locked ? "active" : "error"}`}
                    >
                      {u.locked
                        ? "LOCKED"
                        : u.is_active
                          ? "ACTIVE"
                          : "INACTIVE"}
                    </span>
                  </td>
                  <td>
                    <div className="actions">
                      {u.locked && (
                        <button
                          className="btn secondary small"
                          onClick={() => unlock(u)}
                        >
                          Unlock
                        </button>
                      )}
                      {u.user_id !== me?.user_id && (
                        <button
                          className="btn secondary small"
                          onClick={() => toggle(u)}
                        >
                          {u.is_active ? "Deactivate" : "Activate"}
                        </button>
                      )}
                      {u.user_id !== me?.user_id &&
                        u.role !== "SUPER_ADMIN" && (
                          <button
                            className="btn danger small"
                            onClick={() => remove(u)}
                          >
                            Delete
                          </button>
                        )}
                    </div>
                  </td>
                </tr>
              ))}
              {!items.length && (
                <tr>
                  <td colSpan={5}>
                    <div className="empty">No users found.</div>
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
              <h2>Create admin account</h2>
              <button className="close" onClick={() => setOpen(false)}>
                ×
              </button>
            </div>
            <form className="form-grid" onSubmit={create}>
              <Field
                label="First name"
                value={form.first_name}
                onChange={(e) =>
                  setForm({ ...form, first_name: e.target.value })
                }
                required
              />
              <Field
                label="Last name"
                value={form.last_name}
                onChange={(e) =>
                  setForm({ ...form, last_name: e.target.value })
                }
                required
              />
              <Field
                label="Username"
                value={form.user_name}
                onChange={(e) =>
                  setForm({ ...form, user_name: e.target.value })
                }
                required
              />
              <Field
                label="Email"
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
              />
              <div className="full">
                <Field
                  label="Password"
                  type="password"
                  minLength={8}
                  value={form.password}
                  onChange={(e) =>
                    setForm({ ...form, password: e.target.value })
                  }
                  required
                />
              </div>
              <div className="full">
                <button className="btn">Create admin</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
