"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { Batch, Monitor } from "@/types";
import { Toast, useToast } from "@/components/Toast";

export default function SessionDetail() {
  const { id } = useParams<{ id: string }>();
  const [m, setM] = useState<Monitor | null>(null);
  const [batches, setBatches] = useState<Batch[]>([]);
  const { message, show } = useToast();

  async function load() {
    try {
      setM(await api.monitor(id));
      setBatches(await api.batches(id));
    } catch (e) {
      show(e instanceof ApiError ? e.detail : "Could not load session");
    }
  }
  useEffect(() => {
    load();
    const t = setInterval(load, 2500);
    return () => clearInterval(t);
  }, [id]);
  if (!m)
    return (
      <>
        <Toast message={message} />
        <div className="empty">Loading session…</div>
      </>
    );
  return (
    <>
      <Toast message={message} />
      <div className="page-header">
        <div>
          <div className="eyebrow">Session monitor</div>
          <h1 className="page-title">Live serving flow</h1>
          <p className="page-subtitle">Session {m.session.session_id}</p>
        </div>
        <span className={`badge ${m.session.status.toLowerCase()}`}>
          {m.session.status}
        </span>
      </div>

      <div className="grid grid-4">
        <div className="card stat">
          <div className="label">Students</div>
          <div className="value">{m.total_students}</div>
        </div>

        <div className="card stat">
          <div className="label">Going</div>
          <div className="value">{m.going}</div>
        </div>

        <div className="card stat">
          <div className="label">Skipped</div>
          <div className="value">{m.skipped}</div>
        </div>

        <div className="card stat">
          <div className="label">No response</div>
          <div className="value">{m.no_response}</div>
        </div>
      </div>

      <div className="card section-gap">
        <div className="page-header" style={{ marginBottom: 10 }}>
          <div>
            <h3 className="card-title">Current batch {m.current_batch?.batch_number ?? "—"}</h3>
            <p className="muted" style={{ fontSize: 12 }}>
              
              Called batches: {m.called_batches} · Waiting: {m.waiting_batches}{" "}
              · Completed: {m.completed_batches}
            </p>
          </div>
        </div>

        {m.current_batch ? (
          <div className="members">
            {m.current_batch.members.map((x) => (
              <span
                key={x.student_id}
                className={`member-chip ${x.response.toLowerCase()}`}
              >
                {x.student_number} · {x.response.replace("_", " ")}
              </span>
            ))}
          </div>
        ) : (
          <div className="empty">No batch is currently called.</div>
        )}
      </div>

      <div className="card section-gap">
        <h3 className="card-title">All batches</h3>
        <div className="batch-list" style={{ marginTop: 14 }}>
          {batches.map((b) => (
            <BatchCard key={b.batch_id} batch={b} />
          ))}
        </div>
      </div>
    </>
  );
}
function BatchCard({ batch: b }: { batch: Batch }) {
  const c = b.members.reduce(
    (a, x) => {
      a[x.response] = (a[x.response] || 0) + 1;
      return a;
    },
    {} as Record<string, number>,
  );
  return (
    <div className={`batch-card ${b.status.toLowerCase()}`}>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <strong>Batch {b.batch_number}</strong>
        <span className={`badge ${b.status.toLowerCase()}`}>{b.status}</span>
      </div>
      <div className="muted" style={{ fontSize: 11, marginTop: 5 }}>
        {c.GOING || 0} going · {c.SKIPPED || 0} skipped · {c.NO_RESPONSE || 0}{" "}
        no response
      </div>
      <div className="members">
        {b.members.map((x) => (
          <span
            key={x.student_id}
            className={`member-chip ${x.response.toLowerCase()}`}
          >
            {x.student_number}
          </span>
        ))}
      </div>
    </div>
  );
}
