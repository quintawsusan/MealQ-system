import "./global.css";

import type { Metadata } from "next";
export const metadata: Metadata = {
  title: "MealQ | Cafeteria Flow",
  description: "Meal queue and cafeteria flow management",
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
