import { useEffect, useRef, useState } from "react";
import { Camera, X, SwitchCamera, AlertTriangle } from "lucide-react";
import { SCAN } from "@/constants/testIds";

const MAX_SIDE = 1024;

export function CameraCapture({ onCapture, onClose, onUnavailable }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [facing, setFacing] = useState("environment");
  const [error, setError] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setReady(false);
    setError(null);
    const stop = () => streamRef.current?.getTracks().forEach((t) => t.stop());
    if (!navigator.mediaDevices?.getUserMedia) {
      setError("Browser ini tidak mendukung kamera langsung.");
      return undefined;
    }
    navigator.mediaDevices
      .getUserMedia({ video: { facingMode: { ideal: facing }, width: { ideal: 1280 }, height: { ideal: 960 } }, audio: false })
      .then((stream) => {
        if (cancelled) { stream.getTracks().forEach((t) => t.stop()); return; }
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.onloadedmetadata = () => setReady(true);
        }
      })
      .catch((e) => {
        const denied = e?.name === "NotAllowedError";
        setError(denied ? "Izin kamera ditolak. Izinkan akses kamera atau unggah foto." : "Kamera tidak tersedia di perangkat ini.");
      });
    return () => { cancelled = true; stop(); };
  }, [facing]);

  const capture = () => {
    const v = videoRef.current;
    if (!v || !ready) return;
    const scale = Math.min(1, MAX_SIDE / Math.max(v.videoWidth, v.videoHeight));
    const canvas = document.createElement("canvas");
    canvas.width = Math.round(v.videoWidth * scale);
    canvas.height = Math.round(v.videoHeight * scale);
    canvas.getContext("2d").drawImage(v, 0, 0, canvas.width, canvas.height);
    onCapture(canvas.toDataURL("image/jpeg", 0.85));
  };

  return (
    <div className="relative rounded-3xl overflow-hidden bg-black" data-testid={SCAN.cameraView} style={{ aspectRatio: "4 / 5" }}>
      {!error && (
        <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover"
          style={{ transform: facing === "user" ? "scaleX(-1)" : "none" }} />
      )}
      {error && (
        <div className="absolute inset-0 grid place-items-center p-6 text-center text-white">
          <div>
            <AlertTriangle size={28} className="mx-auto mb-2" color="var(--nv-accent)" />
            <p className="text-sm leading-relaxed" data-testid={SCAN.cameraError}>{error}</p>
            <button onClick={onUnavailable} data-testid={SCAN.cameraFallbackBtn} className="nv-btn-accent mt-4 mx-auto">
              Unggah foto saja
            </button>
          </div>
        </div>
      )}
      <div className="absolute inset-x-0 top-0 p-3 flex items-center justify-between">
        <span className="nv-chip" style={{ background: "rgba(0,0,0,0.45)", color: "#fff", fontSize: "0.6rem", letterSpacing: "0.14em", textTransform: "uppercase" }}>
          {ready ? "Kamera aktif" : "Menyiapkan kamera…"}
        </span>
        <button onClick={onClose} data-testid={SCAN.cameraCloseBtn} aria-label="Tutup kamera"
          className="grid place-items-center w-9 h-9 rounded-full" style={{ background: "rgba(0,0,0,0.45)" }}>
          <X size={18} color="#fff" />
        </button>
      </div>
      {!error && (
        <div className="absolute inset-x-0 bottom-0 p-4 flex items-center justify-center gap-6">
          <span className="w-11" />
          <button onClick={capture} disabled={!ready} data-testid={SCAN.cameraShutterBtn} aria-label="Ambil foto"
            className="grid place-items-center w-16 h-16 rounded-full border-4 border-white disabled:opacity-50 transition-transform active:scale-95"
            style={{ background: "var(--nv-accent)" }}>
            <Camera size={24} color="#fff" />
          </button>
          <button onClick={() => setFacing((f) => (f === "user" ? "environment" : "user"))} data-testid={SCAN.cameraFlipBtn}
            aria-label="Ganti kamera" className="grid place-items-center w-11 h-11 rounded-full" style={{ background: "rgba(255,255,255,0.2)" }}>
            <SwitchCamera size={18} color="#fff" />
          </button>
        </div>
      )}
    </div>
  );
}
