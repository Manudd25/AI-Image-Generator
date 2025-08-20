# ai-image-colab (Diffusers on Colab + FastAPI + ngrok)

## Backend (Colab)
1. Open `colab_api.ipynb` in Google Colab.
2. Runtime → Change runtime type → GPU.
3. Run cells to install deps, load model, set ngrok token, start FastAPI.
4. Copy the printed `PUBLIC API URL` (e.g., https://xxxxx.ngrok-free.app).

## Frontend
1. In `frontend/.env.development` set:
   VITE_API_BASE=https://xxxxx.ngrok-free.app
2. `npm install` (first time), then `npm run dev`.

Notes:
- Keep the Colab cell running; the URL changes on restart.
- Use 512x512, 20–25 steps for speed on free GPUs.
