import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Sparkles, ArrowRight } from "lucide-react";
import Layout from "@/components/Layout";
import { RecipeCard } from "@/components/common";
import { getMoods, getMood } from "@/lib/api";
import { MOOD } from "@/constants/testIds";

export default function MoodPage() {
  const [params, setParams] = useSearchParams();
  const [moods, setMoods] = useState([]);
  const [selected, setSelected] = useState(params.get("selected") || "berenergi");
  const [detail, setDetail] = useState(null);

  useEffect(() => { getMoods().then(setMoods); }, []);
  useEffect(() => {
    getMood(selected).then(setDetail).catch(() => {});
    setParams({ selected }, { replace: true });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected]);

  const current = moods.find((m) => m.key === selected);

  return (
    <Layout>
      <div className="px-5 pt-4 space-y-6">
        <div>
          <p className="nv-eyebrow mb-1" style={{ color: "var(--nv-accent)" }}>Mood check-in</p>
          <h1 className="font-display text-[1.7rem] font-semibold leading-tight" style={{ color: "var(--nv-green-deep)" }}>
            Makan sesuai kebutuhan harimu.
          </h1>
          <p className="mt-2 text-sm leading-relaxed" style={{ color: "var(--nv-muted)" }}>
            Pilih perasaanmu. NutriVane bantu memulai dari pilihan sederhana, bukan menghakimi.
          </p>
        </div>

        {/* mood selector panel */}
        <div className="rounded-3xl p-5 text-white relative overflow-hidden nv-rise"
          style={{ background: "linear-gradient(150deg, var(--nv-green-mid), var(--nv-green-deep))" }}>
          <div className="flex items-start justify-between">
            <span className="grid place-items-center w-11 h-11 rounded-2xl" style={{ background: "rgba(255,255,255,0.14)" }}>
              <Sparkles size={20} />
            </span>
            <span className="text-4xl leading-none">{current?.emoji}</span>
          </div>
          <h2 className="font-display text-xl font-semibold mt-4">{current?.question}</h2>
          <p className="text-sm text-white/75 mt-1.5">{current?.helper}</p>

          <div className="grid grid-cols-2 gap-2.5 mt-4">
            {moods.map((m) => {
              const on = m.key === selected;
              return (
                <button key={m.key} data-testid={MOOD.option(m.key)} onClick={() => setSelected(m.key)}
                  className="rounded-2xl px-4 py-3 text-left transition-all flex items-center gap-2.5"
                  style={{
                    background: on ? "#fff" : "rgba(255,255,255,0.1)",
                    color: on ? "var(--nv-green-deep)" : "#fff",
                  }}>
                  <span className="text-xl">{m.emoji}</span>
                  <span className="font-bold text-sm">{m.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* curated */}
        <section className="nv-rise" style={{ animationDelay: "80ms" }}>
          <div className="flex items-end justify-between mb-3.5">
            <div>
              <p className="nv-eyebrow mb-1">Curated for you</p>
              <h2 className="font-display text-xl font-semibold" style={{ color: "var(--nv-green-deep)" }}>
                Pilihan {current?.label?.toLowerCase()}
              </h2>
            </div>
            <Link to="/recipes" data-testid={MOOD.seeAll} className="flex items-center gap-1 text-xs font-bold" style={{ color: "var(--nv-accent)" }}>
              semua resep <ArrowRight size={13} />
            </Link>
          </div>
          <div className="space-y-4">
            {detail?.recipes?.map((r) => (
              <RecipeCard key={r.slug} r={r} to={`/recipes/${r.slug}`} tid={MOOD.recipe(r.slug)} />
            ))}
          </div>
        </section>
      </div>
    </Layout>
  );
}
