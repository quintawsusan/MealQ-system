"use client";

import { useState } from "react";

export function Field({
  label,
  type = "text",
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & { label: string }) {
  const [showPassword, setShowPassword] = useState(false);

  const isPassword = type === "password";
  const inputType = isPassword && showPassword ? "text" : type;

  return (
    <label className="field">
      <span>{label}</span>

      <div className="password-input-wrapper">
        <input type={inputType} {...props} />

        {isPassword && (
          <button
            type="button"
            className="password-toggle"
            onClick={() => setShowPassword((prev) => !prev)}
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? "👁️" : "🙈"}
          </button>
        )}
      </div>
    </label>
  );
}

export function SelectField({
  label,
  children,
  ...props
}: React.SelectHTMLAttributes<HTMLSelectElement> & { label: string }) {
  return (
    <label className="field">
      <span>{label}</span>
      <select {...props}>{children}</select>
    </label>
  );
}