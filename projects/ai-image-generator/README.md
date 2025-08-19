# 🖼️ AI Image Generator

This repo holds multiple ways to build an AI image generators.

A simple **AI-powered image generator** built with:

- **Backend:** FastAPI (Python) + Hugging Face Inference API
- **Frontend:** React (Vite) + Axios

Users can type a text prompt and instantly generate an AI image using **Stable Diffusion XL Turbo**.

---

## 🚀 Features

- Generate images from text prompts
- Backend calls Hugging Face API securely with your token
- Frontend React app with prompt input + image preview
- CORS-enabled so frontend and backend work locally
- Easy to extend with extra options (steps, width, height, etc.)

- `variants/ai-image-colab`: Colab GPU backend (Diffusers + FastAPI + ngrok) + React frontend.
- `variants/ai-image-hf` (planned): FastAPI calling Hugging Face Inference API.
- `variants/ai-image-fal` (planned): FastAPI calling fal.ai (free community tier).
- `variants/ai-image-pollinations` (planned): FastAPI calling Pollinations (no API key).

Each variant has its own README with run instructions.
