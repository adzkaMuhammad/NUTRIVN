import { useEffect, useState, useRef } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { ArrowLeft, Scan as ScanIcon, Sparkles, Info, Image as ImageIcon, RotateCcw } from "lucide-react";
import Layout from "@/components/Layout";
import { SpiceMeter } from "@/components/common";
import { getRecipes, postScan } from "@/lib/api";
import { SCAN } from "@/constants/testIds";

export default function ScanPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const fileRef = useRef(null);

  const [benchmarks, setBenchmarks] = useState([]);
  const [selected, setSelected] = useState(null);
  const [measure, setMeasure] = useState(params.get("measure") === "true");
  const [imageB64, setImageB64] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    getRecipes().then((rs) => {
      setBenchmarks(rs);
      setSelected(rs[0]?.slug || null);
    });
  }, []);

  const onFile = (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = () => setImageB64(reader.result);
    reader.readAsDataURL(f);
  };

  const runScan = async () => {
    if (!selected) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await postScan({ benchmark_slug: selected, measure, image_base64: imageB64 });
      setResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => { setResult(null); setImageB64(null); };

  return (
    <Layout>
      <div className="px-5 pt-4 space-y-6">
        <button onClick={() => navigate("/")} data-testid={SCAN.back}
          className="flex items-center gap-1.5 text-sm font-semibold" style={{ color: "var(--nv-muted)" }}>
          <ArrowLeft size={16} /> kembali ke beranda
        </button>

        <div>
          <p className="nv-eyebrow mb-1" style={{ color: "var(--nv-accent)" }}>Camera studio</p>
          <h1 className="font-display text-[1.7rem] font-semibold leading-tight" style={{ color: "var(--nv-green-deep)" }}>
            Kenali isi piringmu.
          </h1>
          <p className="mt-2 text-sm leading-relaxed" style={{ color: "var(--nv-muted)" }}>
            Pilih benchmark menu untuk simulasi beta, lalu tentukan apakah kamu ingin mengukur bumbunya juga.
          </p>
        </div>

        {!result && (
          <>
            {/* camera frame */}
            <div className="rounded-3xl p-7 text-center text-white relative overflow-hidden nv-rise"
              style={{ background: "linear-gradient(160deg, var(--nv-green-mid), var(--nv-green-deep))" }}>
              <label htmlFor="scan-file" className="cursor-pointer block">
                <span className="grid place-items-center w-16 h-16 mx-auto rounded-2xl mb-3" style={{ background: "rgba(255,255,255,0.14)" }}>
                  {imageB64 ? <ImageIcon size={28} /> : <ScanIcon size={28} />}
                </span>
                <p className="font-display text-xl font-semibold">{imageB64 ? "Foto siap dianalisis" : "Arahkan ke makananmu"}</p>
                <p className="text-sm text-white/75 mt-1.5 max-w-xs mx-auto">
                  {imageB64 ? "Ketuk untuk ganti foto, lalu mulai scan." : "Unggah / ambil foto, atau pilih menu benchmark di bawah."}
                </p>
              </label>
              <input id="scan-file" ref={fileRef} data-testid={SCAN.uploadInput} type="file"
                accept="image/*" capture="environment" className="hidden" onChange={onFile} />
              <span className="nv-chip mt-4" style={{ background: "rgba(255,255,255,0.14)", color: "#fff", fontSize: "0.6rem", letterSpacing: "0.14em", textTransform: "uppercase" }}>
                Kamera beta · preview
              </span>
            </div>

            {/* benchmark select */}
            <div className="nv-card p-4 nv-rise" style={{ animationDelay: "60ms" }}>
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="font-bold text-sm" style={{ color: "var(--nv-green-deep)" }}>Benchmark menu</p>
                  <p className="text-xs" style={{ color: "var(--nv-muted)" }}>Dipakai sebagai pembanding beta</p>
                </div>
                <span className="nv-chip" style={{ fontSize: "0.62rem" }}>beta dataset</span>
              </div>
              <div className="grid grid-cols-1 gap-2.5">
                {benchmarks.map((b) => (
                  <button key={b.slug} data-testid={SCAN.benchmark(b.slug)} onClick={() => setSelected(b.slug)}
                    className="text-left rounded-2xl px-4 py-3 border transition-all"
                    style={{
                      borderColor: selected === b.slug ? "var(--nv-green)" : "var(--nv-line)",
                      background: selected === b.slug ? "var(--nv-green-soft)" : "#fff",
                    }}>
                    <p className="font-bold text-sm" style={{ color: "var(--nv-green-deep)" }}>{b.name}</p>
                    <p className="text-xs" style={{ color: "var(--nv-muted)" }}>{b.category_label} · {b.source_count} sumber</p>
                  </button>
                ))}
              </div>
            </div>

            {/* measure toggle */}
            <div className="nv-card p-4 flex items-center justify-between gap-3 nv-rise" style={{ animationDelay: "120ms" }}>
              <div className="flex items-start gap-3">
                <span className="grid place-items-center w-10 h-10 rounded-xl shrink-0" style={{ background: "var(--nv-green-soft)" }}>
                  <Sparkles size={18} color="var(--nv-green)" />
                </span>
                <div>
                  <p className="font-bold text-sm" style={{ color: "var(--nv-green-deep)" }}>Ukur &amp; Analisis Bumbu</p>
                  <p className="text-xs leading-snug" style={{ color: "var(--nv-muted)" }}>
                    Tambahkan rata-rata takaran rempah dari sumber resep.
                  </p>
                </div>
              </div>
              <button role="switch" aria-checked={measure} data-testid={SCAN.measureToggle}
                onClick={() => setMeasure((v) => !v)}
                className="relative w-12 h-7 rounded-full shrink-0 transition-colors"
                style={{ background: measure ? "var(--nv-green)" : "#cfd8c8" }}>
                <span className="absolute top-1 w-5 h-5 rounded-full bg-white transition-all"
                  style={{ left: measure ? "26px" : "4px" }} />
              </button>
            </div>

            <p className="flex items-center gap-1.5 text-xs" style={{ color: "var(--nv-muted)" }}>
              <Info size={13} /> Fitur ukur bersifat opsional. Scan tetap bisa dilakukan tanpa analisis bumbu.
            </p>

            <button onClick={runScan} disabled={loading} data-testid={SCAN.startBtn}
              className="nv-btn-primary w-full">
              {loading ? "Menganalisis…" : <>Mulai scan makanan <ScanIcon size={18} /></>}
            </button>
          </>
        )}

        {result && (
          <div className="space-y-5 nv-rise" data-testid={SCAN.resultCard}>
            <div className="nv-card overflow-hidden">
              <img src={result.image} alt={result.menu_name} className="w-full h-44 object-cover" />
              <div className="p-5">
                <span className="nv-chip" style={{ fontSize: "0.62rem", textTransform: "uppercase", letterSpacing: "0.1em" }}>{result.category_label}</span>
                <h2 className="font-display text-2xl font-semibold mt-2" style={{ color: "var(--nv-green-deep)" }}>{result.menu_name}</h2>
                <div className="mt-3 rounded-2xl p-3.5 flex items-start gap-2.5" style={{ background: "var(--nv-green-soft)" }}>
                  <Sparkles size={16} color="var(--nv-green)" className="mt-0.5 shrink-0" />
                  <p className="text-sm leading-relaxed" style={{ color: "var(--nv-ink)" }}>{result.insight}</p>
                </div>
                <p className="text-xs mt-3" style={{ color: "var(--nv-muted)" }}>{result.vision_note}</p>
              </div>
            </div>

            {result.spices && (
              <div className="nv-card p-5" data-testid={SCAN.resultSpice}>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="nv-eyebrow" style={{ color: "var(--nv-accent)" }}>Spice meter</p>
                    <h3 className="font-display text-lg font-semibold" style={{ color: "var(--nv-green-deep)" }}>Rata-rata bumbu menu</h3>
                  </div>
                  <span className="nv-chip" style={{ fontSize: "0.6rem" }}>{result.source_count} resep</span>
                </div>
                <SpiceMeter spices={result.spices} />
              </div>
            )}

            <div className="flex gap-3">
              <button onClick={reset} data-testid={SCAN.resetBtn} className="nv-btn-primary flex-1" style={{ background: "#fff", color: "var(--nv-green)", border: "1px solid var(--nv-line)" }}>
                <RotateCcw size={16} /> Scan lagi
              </button>
              <Link to={`/recipes/${result.benchmark_slug}`} className="nv-btn-accent flex-1">
                Lihat resep lengkap
              </Link>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
