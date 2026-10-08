import { useEffect, useState } from "react";
import { Search, SlidersHorizontal } from "lucide-react";
import Layout from "@/components/Layout";
import { RecipeCard } from "@/components/common";
import { getRecipes, getCategories } from "@/lib/api";
import { RECIPES as TID } from "@/constants/testIds";

export default function RecipesPage() {
  const [cats, setCats] = useState([]);
  const [active, setActive] = useState("semua");
  const [q, setQ] = useState("");
  const [items, setItems] = useState([]);

  useEffect(() => { getCategories().then(setCats); }, []);
  useEffect(() => {
    const t = setTimeout(() => {
      getRecipes({ category: active === "semua" ? undefined : active, q: q || undefined }).then(setItems);
    }, 200);
    return () => clearTimeout(t);
  }, [active, q]);

  return (
    <Layout>
      <div className="px-5 pt-4 space-y-5">
        <div className="flex items-start justify-between">
          <div>
            <p className="nv-eyebrow mb-1" style={{ color: "var(--nv-accent)" }}>Beta kitchen</p>
            <h1 className="font-display text-[1.7rem] font-semibold leading-tight" style={{ color: "var(--nv-green-deep)" }}>
              Jelajah rasa yang lebih sadar.
            </h1>
            <p className="mt-2 text-sm leading-relaxed max-w-xs" style={{ color: "var(--nv-muted)" }}>
              Semua insight bumbu di sini dibuat dari daftar bumbu NutriVane dan benchmark resep terkurasi.
            </p>
          </div>
          <span className="nv-chip shrink-0" style={{ fontSize: "0.6rem", letterSpacing: "0.1em", textTransform: "uppercase" }}>Beta dataset</span>
        </div>

        <div className="flex items-center gap-2.5">
          <div className="nv-card flex items-center gap-2.5 px-4 py-3 flex-1">
            <Search size={17} color="var(--nv-muted)" />
            <input data-testid={TID.search} value={q} onChange={(e) => setQ(e.target.value)}
              placeholder="Cari menu…" className="bg-transparent outline-none text-sm w-full" />
          </div>
          <span className="grid place-items-center w-11 h-11 nv-card shrink-0"><SlidersHorizontal size={17} color="var(--nv-green)" /></span>
        </div>

        <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1">
          {cats.map((c) => (
            <button key={c.key} data-testid={TID.filter(c.key)} onClick={() => setActive(c.key)}
              className={`nv-pill-tab ${active === c.key ? "active" : ""}`}
              style={active !== c.key ? { background: "#fff", border: "1px solid var(--nv-line)" } : {}}>
              {c.label}
            </button>
          ))}
        </div>

        <div className="space-y-4">
          {items.length === 0 && (
            <p className="text-sm text-center py-8" style={{ color: "var(--nv-muted)" }}>Tidak ada menu yang cocok.</p>
          )}
          {items.map((r) => (
            <RecipeCard key={r.slug} r={r} to={`/recipes/${r.slug}`} tid={TID.card(r.slug)} />
          ))}
        </div>
      </div>
    </Layout>
  );
}
