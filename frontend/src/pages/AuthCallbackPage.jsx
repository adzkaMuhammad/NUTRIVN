import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Leaf } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { AUTH } from "@/constants/testIds";

export default function AuthCallbackPage() {
  const navigate = useNavigate();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (user) { localStorage.setItem("nv_welcomed", "1"); navigate("/", { replace: true }); }
  }, [user, navigate]);

  useEffect(() => {
    const t = setTimeout(() => { if (!user) navigate("/login?error=1", { replace: true }); }, 10000);
    return () => clearTimeout(t);
  }, [user, navigate]);

  return (
    <div className="nv-shell grid place-items-center text-white" data-testid={AUTH.callback}
      style={{ background: "var(--nv-green-deep)", paddingBottom: 0 }}>
      <div className="text-center">
        <span className="grid place-items-center w-14 h-14 mx-auto rounded-2xl animate-pulse" style={{ background: "rgba(255,255,255,0.14)" }}>
          <Leaf size={26} />
        </span>
        <p className="mt-4 text-sm text-white/80">{loading ? "Menyambungkan akunmu…" : "Hampir selesai…"}</p>
      </div>
    </div>
  );
}
