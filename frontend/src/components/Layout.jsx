import { NavLink, useLocation } from "react-router-dom";
import { Home, Camera, BookOpen, Sparkles, Leaf, LogIn } from "lucide-react";
import { NAV, HOME, AUTH } from "@/constants/testIds";
import { useAuth } from "@/context/AuthContext";

const items = [
  { to: "/", label: "Beranda", icon: Home, tid: NAV.home, end: true },
  { to: "/scan", label: "Scan", icon: Camera, tid: NAV.scan },
  { to: "/recipes", label: "Resep", icon: BookOpen, tid: NAV.recipes },
  { to: "/mood", label: "Mood", icon: Sparkles, tid: NAV.mood },
];

export function TopBar() {
  const { user } = useAuth();
  return (
    <header className="nv-topbar px-5 py-3.5 flex items-center justify-between">
      <NavLink to="/" data-testid={HOME.brand} className="flex items-center gap-2">
        <span className="grid place-items-center w-9 h-9 rounded-xl" style={{ background: "var(--nv-green)" }}>
          <Leaf size={18} color="#fff" />
        </span>
        <span className="font-display text-xl font-semibold" style={{ color: "var(--nv-green-deep)" }}>
          NutriVane<span style={{ color: "var(--nv-accent)" }}>.</span>
        </span>
      </NavLink>
      <div className="flex items-center gap-2.5">
        <span className="nv-chip" style={{ fontSize: "0.64rem", letterSpacing: "0.14em" }}>BETA 2.0</span>
        {user ? (
          <NavLink to="/profile" data-testid={AUTH.topbarAvatar} aria-label="Profil"
            className="grid place-items-center w-9 h-9 rounded-full font-bold text-sm overflow-hidden"
            style={{ background: "var(--nv-accent-soft)", color: "var(--nv-accent)" }}>
            {user.avatar_url
              ? <img src={user.avatar_url} alt={user.name} className="w-full h-full object-cover" referrerPolicy="no-referrer" />
              : (user.name || "?").charAt(0).toUpperCase()}
          </NavLink>
        ) : (
          <NavLink to="/login" data-testid={AUTH.topbarLogin}
            className="flex items-center gap-1.5 rounded-full px-3.5 py-2 text-xs font-bold text-white"
            style={{ background: "var(--nv-green)" }}>
            <LogIn size={14} /> Masuk
          </NavLink>
        )}
      </div>
    </header>
  );
}

export function BottomNav() {
  const { pathname } = useLocation();
  return (
    <nav className="nv-bottomnav">
      {items.map(({ to, label, icon: Icon, tid, end }) => {
        const active = end ? pathname === "/" : pathname.startsWith(to);
        return (
          <NavLink key={to} to={to} data-testid={tid}
            className={`nv-navitem ${active ? "active" : ""}`}>
            <Icon size={20} strokeWidth={active ? 2.4 : 2} />
            <span>{label}</span>
          </NavLink>
        );
      })}
    </nav>
  );
}

export default function Layout({ children, showTop = true }) {
  return (
    <div className="nv-shell">
      {showTop && <TopBar />}
      <main>{children}</main>
      <BottomNav />
    </div>
  );
}
