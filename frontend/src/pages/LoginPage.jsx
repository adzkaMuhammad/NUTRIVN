import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Leaf, UserRound, ShieldCheck, Flame, Heart } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { AUTH } from "@/constants/testIds";

const GoogleIcon = () => (
  <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
    <path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9 3.5l6.7-6.7C35.6 2.6 30.2 0 24 0 14.6 0 6.5 5.4 2.6 13.2l7.8 6.1C12.3 13.6 17.7 9.5 24 9.5z"/>
    <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.7c-.6 3-2.3 5.5-4.8 7.2l7.5 5.8c4.4-4.1 7.1-10.1 7.1-17.5z"/>
    <path fill="#FBBC05" d="M10.4 28.7c-.5-1.5-.8-3-.8-4.7s.3-3.2.8-4.7l-7.8-6.1C.9 16.6 0 20.2 0 24s.9 7.4 2.6 10.8l7.8-6.1z"/>
    <path fill="#34A853" d="M24 48c6.2 0 11.6-2 15.4-5.6l-7.5-5.8c-2.1 1.4-4.8 2.3-7.9 2.3-6.3 0-11.7-4.1-13.6-9.8l-7.8 6.1C6.5 42.6 14.6 48 24 48z"/>
  </svg>
);

export default function LoginPage() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const { user, loading, authEnabled, signInWithGoogle } = useAuth();

  useEffect(() => { if (!loading && user) navigate("/", { replace: true }); }, [user, loading, navigate]);

  const continueAsGuest = () => { localStorage.setItem("nv_welcomed", "1"); navigate("/", { replace: true }); };

  return (
    <div className="nv-shell flex flex-col text-white" data-testid={AUTH.page}
      style={{ background: "linear-gradient(170deg, var(--nv-green-mid) 0%, var(--nv-green-deep) 70%)", paddingBottom: 0 }}>
      <div className="flex-1 px-7 pt-16 pb-8 flex flex-col">
        <div className="nv-rise">
          <span className="grid place-items-center w-16 h-16 rounded-3xl" style={{ background: "rgba(255,255,255,0.14)" }}>
            <Leaf size={30} color="#fff" />
          </span>
          <p className="nv-eyebrow mt-8" style={{ color: "rgba(255,255,255,0.65)" }}>Beta 2.0</p>
          <h1 className="font-display text-4xl font-semibold leading-[1.1] mt-2">
            Selamat datang<br />di NutriVane<span style={{ color: "var(--nv-accent)" }}>.</span>
          </h1>
          <p className="mt-4 text-sm leading-relaxed text-white/75 max-w-xs">
            Kenali bumbu di balik setiap piring. Masuk untuk menyimpan streak, jumlah piring, dan menu favoritmu.
          </p>
        </div>

        <div className="mt-8 space-y-2.5 nv-rise" style={{ animationDelay: "80ms" }}>
          {[
            { icon: Flame, text: "Streak & jumlah piring tersimpan per akun" },
            { icon: Heart, text: "Simpan menu favorit untuk diakses kapan saja" },
            { icon: ShieldCheck, text: "Data aman di Supabase, hanya kamu yang bisa melihatnya" },
          ].map(({ icon: Icon, text }) => (
            <div key={text} className="flex items-center gap-3 text-sm text-white/85">
              <span className="grid place-items-center w-8 h-8 rounded-xl shrink-0" style={{ background: "rgba(255,255,255,0.12)" }}>
                <Icon size={15} />
              </span>
              {text}
            </div>
          ))}
        </div>

        <div className="mt-auto pt-10 space-y-3 nv-rise" style={{ animationDelay: "160ms" }}>
          {params.get("error") && (
            <p className="text-xs text-center rounded-xl py-2 px-3" data-testid={AUTH.error} style={{ background: "rgba(227,130,79,0.25)" }}>
              Login belum berhasil. Coba lagi ya.
            </p>
          )}
          <button onClick={signInWithGoogle} disabled={!authEnabled} data-testid={AUTH.googleBtn}
            className="w-full flex items-center justify-center gap-3 rounded-full py-3.5 font-bold text-sm transition-transform active:scale-[0.98] disabled:opacity-60"
            style={{ background: "#fff", color: "var(--nv-green-deep)" }}>
            <GoogleIcon /> Masuk dengan Google
          </button>
          {!authEnabled && (
            <p className="text-[0.7rem] text-center text-white/60 leading-snug" data-testid={AUTH.notConfigured}>
              Login Google aktif setelah REACT_APP_SUPABASE_URL &amp; REACT_APP_SUPABASE_PUBLISHABLE_KEY diisi.
            </p>
          )}
          <button onClick={continueAsGuest} data-testid={AUTH.guestBtn}
            className="w-full flex items-center justify-center gap-2 rounded-full py-3.5 font-semibold text-sm border border-white/30 text-white/90">
            <UserRound size={16} /> Lanjut sebagai tamu
          </button>
        </div>
      </div>
    </div>
  );
}
