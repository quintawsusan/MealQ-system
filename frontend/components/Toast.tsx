"use client";
import { useEffect, useState } from "react";

export function useToast() {
  const [message, setMessage] = useState("");
  useEffect(() => {
    if (!message) return;
    const t = setTimeout(() => setMessage(""), 3500);
    return () => clearTimeout(t);
  }, [message]);
  return { message, show: setMessage };
}

export function Toast({ message }: { message: string }) {
  if (!message) return null;
  return <div className="toast">{message}</div>;
}
