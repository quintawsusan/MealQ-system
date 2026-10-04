import Protected from "@/components/Protected";
import Shell from "@/components/Shell";
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <Protected roles={["STUDENT"]}>
      <Shell role="STUDENT">{children}</Shell>
    </Protected>
  );
}
