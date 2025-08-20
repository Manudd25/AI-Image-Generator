import { useState } from "react";
import axios from "axios"
import "./App.css";

function App() {
  const [prompt, setPrompt] = useState("");
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);

  const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";


  const generateImage = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setImage(null);
    try {
      const res = await axios.post(`${API_BASE}/generate`, { text: prompt });
      setImage(`data:image/png;base64,${res.data.image}`);
    } catch (err) {
      console.error(err);
      alert(err?.response?.data?.detail || "Generation failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <h1>AI Image Generator</h1>
      <input
        type="text"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Enter a text..."
        className="prompt-input"
      />

      <button onClick={generateImage} disabled={loading}>
        {loading ? "Generating..." : "Generate"}
      </button>

      {image && (
        <div className="image-wrapper">
          <img src={image} alt="Generated" width="512" />
        </div>
      )}
    </div>
  );
}

export default App;
