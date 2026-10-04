import Protected from "@/components/Protected";
import Shell from "@/components/Shell";
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <Protected roles={["ADMIN", "SUPER_ADMIN"]}>
      <Shell role="ADMIN">{children}</Shell>
    </Protected>
  );
}
