import { useState } from "react";
import axios from "axios"
import "./App.css";

function App() {
  const [prompt, setPrompt] = useState("");
  const [image, setImage] = useState(null);

  const generateImage = async () => {
    const res = await axios.post("http://localhost:8000/generate", {
      text: prompt,
    });
    setImage(`data:image/png;base64,${res.data.image}`);
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
      <button onClick={generateImage}>Generate</button>

      {image && (
        <div className="image-wrapper">
          <img src={image} alt="Generated" width="512" />
        </div>
      )}
    </div>
  );
}

export default App;
