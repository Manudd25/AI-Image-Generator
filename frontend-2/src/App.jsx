import { useState } from "react";
import axios from "axios";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
const MODEL_LABEL = import.meta.env.VITE_MODEL_LABEL || "SD v1.5 (Colab)";

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [imgSize, setImgSize] = useState("");

  const generate = async (e) => {
    e?.preventDefault();
    if (!prompt.trim()) return;

    setLoading(true);
    setErr("");
    setImage(null);
    setImgSize("");

    // 0) ping /health first to avoid CORS errors in console
    let backendOk = false;
    try {
      const ping = await fetch(`${API_BASE}/health`, { mode: "cors", cache: "no-store" });
      backendOk = ping.ok;
    } catch {
      backendOk = false;
    }

    if (backendOk) {
      try {
        const res = await axios.post(
          `${API_BASE}/generate`,
          { text: prompt.trim() },
          { timeout: 60000 }
        );
        if (!res?.data?.image) throw new Error("Backend returned no image");
        setImage(`data:image/png;base64,${res.data.image}`);
        return; // success
      } catch (error) {
        // Show friendly error without console noise
        const status = error?.response?.status;
        const detail =
          error?.response?.data?.detail ||
          error?.message ||
          "Unknown error contacting backend";
        setErr(`Colab API error${status ? ` (${status})` : ""}: ${detail}`);
        // (fall through to fallback)
      }
    } else {
      setErr("Backend offline — using fallback.");
    }

    // fallback (optional)
    try {
      const encoded = encodeURIComponent(prompt.trim());
      const url = `https://image.pollinations.ai/prompt/${encoded}?width=512&height=512&seed=0&nologo=true`;
      const r = await fetch(url, { mode: "cors", cache: "no-store" });
      if (!r.ok) throw new Error(`Pollinations HTTP ${r.status}`);
      const blob = await r.blob();
      const objUrl = URL.createObjectURL(blob);
      setImage(objUrl);
    } catch {
      setErr("Generation failed (backend offline and fallback failed).");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="paint-root">
      <div className="bg-elements">
        <div className="floating-orb orb-1" />
        <div className="floating-orb orb-2" />
        <div className="floating-orb orb-3" />
        <div className="floating-orb orb-4" />
      </div>

      <header className="paint-hero">
        <div className="title">
          <h1>Neo Paint Console</h1>
          <p className="subtitle">Describe your vision. We’ll paint it with photons. ✨</p>
        </div>
      </header>

      <form className="dock" onSubmit={generate}>
        <input
          className="dock-input"
          type="text"
          placeholder='Try: "futuristic gaming MacBook in neon green, close-up code glow"'
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
        <button className="dock-button" disabled={loading}>
          {loading ? "Painting..." : "Generate"}
        </button>
      </form>

      {/* NEW: info bar under the dock */}
      <div className="info-bar">
        <div className="info-left" title={prompt || "Prompt"}>
          {prompt ? prompt : "— Enter a prompt to begin —"}
        </div>
        <div className="info-right">
          <span className="chip chip-model">{MODEL_LABEL}</span>
          <span className="chip chip-count">1 img</span>
          {imgSize && <span className="chip chip-size">{imgSize}</span>}
        </div>
      </div>

      <main className="stage">
        {loading ? (
          <div className="canvas loading">
            <div className="spinner" />
            <div className="scanline" />
          </div>
        ) : image ? (
          <figure className="canvas">
            <img
              src={image}
              alt="Generated"
              onLoad={(e) =>
                setImgSize(`${e.currentTarget.naturalWidth}×${e.currentTarget.naturalHeight}`)
              }
            />
            <figcaption className="legend">
              <span className="dot" />
              {prompt}
            </figcaption>
          </figure>
        ) : (
          <div className="canvas idle">
            <div className="hint">
              <span className="kbd">Tip</span> Add styles like <em>oil painting</em>,{" "}
              <em>analog film</em>, <em>cyberpunk</em>, <em>studio ghibli</em>.
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        <span>Backend:</span> <code>{API_BASE}</code>
      </footer>
    </div>
  );
}
