import { Link } from "react-router-dom";
import { Users, Flame } from "lucide-react";

export function SpiceMeter({ spices, compact = false }) {
  return (
    <div className="space-y-3.5">
      {spices.map((s, i) => (
        <div key={s.name} data-testid={`spice-row-${s.name.toLowerCase().replace(/\s+/g, "-")}`}>
          <div className="flex items-baseline justify-between mb-1.5">
            <span className="text-sm font-semibold" style={{ color: "var(--nv-ink)" }}>{s.name}</span>
            <span className="text-sm">
              <span className="font-bold" style={{ color: i === 0 ? "var(--nv-accent)" : "var(--nv-green)" }}>
                {s.avg}{s.unit}
              </span>
              <span className="ml-1 text-xs" style={{ color: "var(--nv-muted)" }}>avg</span>
            </span>
          </div>
          <div className="nv-meter-track">
            <div className={`nv-meter-fill ${i === 0 ? "top" : ""}`} style={{ width: `${s.pct}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

export function RecipeCard({ r, to, tid }) {
  return (
    <Link to={to} data-testid={tid} className="nv-card overflow-hidden block nv-rise">
      <div className="relative h-40">
        <img src={r.image} alt={r.name} className="w-full h-full object-cover" />
        <span className="absolute top-3 left-3 nv-chip" style={{ fontSize: "0.62rem", letterSpacing: "0.12em", textTransform: "uppercase" }}>
          {r.category_label}
        </span>
      </div>
      <div className="p-4">
        <h3 className="font-display text-lg font-semibold leading-tight" style={{ color: "var(--nv-green-deep)" }}>
          {r.name}
        </h3>
        <p className="mt-1.5 text-sm leading-snug" style={{ color: "var(--nv-muted)" }}>{r.tagline}</p>
        <div className="mt-3 flex items-center gap-4 text-xs font-semibold" style={{ color: "var(--nv-muted)" }}>
          <span className="flex items-center gap-1.5"><Users size={14} />{r.porsi} porsi</span>
          <span className="flex items-center gap-1.5"><Flame size={14} />{r.source_count} sumber</span>
        </div>
      </div>
    </Link>
  );
}

export function SectionHead({ eyebrow, title, action }) {
  return (
    <div className="flex items-end justify-between mb-3.5">
      <div>
        <p className="nv-eyebrow mb-1">{eyebrow}</p>
        <h2 className="font-display text-xl font-semibold" style={{ color: "var(--nv-green-deep)" }}>{title}</h2>
      </div>
      {action}
    </div>
  );
}
