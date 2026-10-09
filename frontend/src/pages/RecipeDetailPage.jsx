import { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Users, Flame, Camera, Heart, Sparkles } from "lucide-react";
import { toast } from "sonner";
import Layout from "@/components/Layout";
import { SpiceMeter } from "@/components/common";
import { getRecipe, getInsight } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { DETAIL } from "@/constants/testIds";

export default function RecipeDetailPage() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { user, isFavorite, toggleFavorite } = useAuth();
  const [r, setR] = useState(null);
  const [insight, setInsight] = useState(null);
  const fav = isFavorite(slug);

  const onFav = () => {
    if (!user) {
      toast("Masuk dulu untuk menyimpan favorit", { action: { label: "Masuk", onClick: () => navigate("/login") } });
      return;
    }
    toggleFavorite(slug);
  };

  useEffect(() => {
    getRecipe(slug).then(setR).catch(() => navigate("/recipes"));
    getInsight(slug).then((d) => setInsight(d.text)).catch(() => {});
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slug]);

  if (!r) return <Layout><div className="p-5 text-sm" style={{ color: "var(--nv-muted)" }}>Memuat…</div></Layout>;

  return (
    <Layout>
      <div className="px-5 pt-4 space-y-5">
        <button onClick={() => navigate(-1)} data-testid={DETAIL.back}
          className="flex items-center gap-1.5 text-sm font-semibold" style={{ color: "var(--nv-muted)" }}>
          <ArrowLeft size={16} /> kembali
        </button>

        <div className="nv-card overflow-hidden nv-rise">
          <div className="relative h-56">
            <img src={r.image} alt={r.name} className="w-full h-full object-cover" />
            <button onClick={onFav} data-testid={DETAIL.favBtn} aria-pressed={fav} aria-label="Simpan favorit"
              className="absolute top-3 right-3 grid place-items-center w-10 h-10 rounded-full transition-transform active:scale-90"
              style={{ background: "rgba(255,255,255,0.9)" }}>
              <Heart size={18} color="var(--nv-accent)" fill={fav ? "var(--nv-accent)" : "none"} />
            </button>
            <span className="absolute top-3 left-3 nv-chip" style={{ fontSize: "0.62rem", textTransform: "uppercase", letterSpacing: "0.1em" }}>
              {r.category_label}
            </span>
          </div>
          <div className="p-5">
            <h1 className="font-display text-2xl font-semibold" style={{ color: "var(--nv-green-deep)" }}>{r.name}</h1>
            <p className="mt-2 text-sm leading-relaxed" style={{ color: "var(--nv-muted)" }}>{r.tagline}</p>
            <div className="mt-3 flex items-center gap-4 text-xs font-semibold" style={{ color: "var(--nv-muted)" }}>
              <span className="flex items-center gap-1.5"><Users size={14} />{r.porsi} porsi</span>
              <span className="flex items-center gap-1.5"><Flame size={14} />{r.source_count} sumber resep</span>
            </div>
            <Link to={`/scan?measure=true&benchmark=${r.slug}`} data-testid={DETAIL.scanThis} className="nv-btn-primary mt-4 w-full">
              <Camera size={17} /> Scan menu ini
            </Link>
          </div>
        </div>

        {insight && (
          <div className="rounded-3xl p-5 nv-rise" data-testid={DETAIL.insight} style={{ background: "var(--nv-accent-soft)" }}>
            <div className="flex items-center gap-2 mb-2">
              <Sparkles size={16} color="var(--nv-accent)" />
              <p className="nv-eyebrow" style={{ color: "var(--nv-accent)" }}>Insight rasa</p>
            </div>
            <p className="text-sm leading-relaxed" style={{ color: "var(--nv-ink)" }}>{insight}</p>
          </div>
        )}

        <div className="nv-card p-5 nv-rise">
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="nv-eyebrow" style={{ color: "var(--nv-accent)" }}>Spice meter</p>
              <h2 className="font-display text-xl font-semibold" style={{ color: "var(--nv-green-deep)" }}>Rata-rata bumbu menu</h2>
            </div>
            <span className="nv-chip shrink-0" style={{ fontSize: "0.58rem" }}>Beta · {r.source_count} resep</span>
          </div>
          <SpiceMeter spices={r.spices} />
          <p className="text-xs mt-5 leading-relaxed" style={{ color: "var(--nv-muted)" }}>
            Benchmark beta dari {r.source_count} sumber resep. Pakai sebagai panduan, bukan takaran mutlak.
          </p>
        </div>

        <div className="nv-card p-5 nv-rise">
          <h3 className="font-bold text-sm mb-3" style={{ color: "var(--nv-green-deep)" }}>Sumber resep</h3>
          <div className="flex flex-wrap gap-2">
            {r.sources.map((s, i) => (
              <span key={i} className="nv-chip" style={{ background: "var(--nv-green-soft)", fontSize: "0.72rem" }}>
                {s.name} · {s.porsi} porsi
              </span>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}
