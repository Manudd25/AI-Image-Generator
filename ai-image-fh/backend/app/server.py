import os, base64
from io import BytesIO
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from PIL import Image, UnidentifiedImageError
from dotenv import load_dotenv

import requests

# 1) Load env and read token/model FIRST
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN missing. Add it to backend/.env")

# Use a widely-open model while testing; switch back later if you want
DEFAULT_MODEL = os.getenv("HF_MODEL", "runwayml/stable-diffusion-v1-5")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")

# 2) Now build headers
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Accept": "image/png",   # tell HF we want raw image bytes
}

app = FastAPI(title="AI Image Generator API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN] if FRONTEND_ORIGIN != "*" else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Prompt to generate the image")
    negative_prompt: Optional[str] = None
    width: Optional[int] = Field(None, ge=256, le=1024)
    height: Optional[int] = Field(None, ge=256, le=1024)
    guidance_scale: Optional[float] = Field(None, ge=0, le=20)
    num_inference_steps: Optional[int] = Field(None, ge=1, le=50)
    seed: Optional[int] = None
    model: Optional[str] = Field(None, description="Override model name (optional)")

class GenerateResponse(BaseModel):
    image: str
    model: str

def pil_to_base64_png(img: Image.Image) -> str:
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

@app.get("/")
def root():
    return {"ok": True, "hint": "Use GET /health, POST /generate, or open /docs"}

@app.get("/health")
def health():
    return {"status": "ok", "model": DEFAULT_MODEL}

@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    model_name = req.model or DEFAULT_MODEL
    url = f"https://api-inference.huggingface.co/models/{model_name}"

    params: Dict[str, Any] = {}
    if req.negative_prompt is not None: params["negative_prompt"] = req.negative_prompt
    if req.guidance_scale is not None: params["guidance_scale"] = req.guidance_scale
    if req.num_inference_steps is not None: params["num_inference_steps"] = req.num_inference_steps
    if req.width is not None: params["width"] = req.width
    if req.height is not None: params["height"] = req.height
    if req.seed is not None: params["seed"] = req.seed

    payload: Dict[str, Any] = {"inputs": req.text}
    if params: payload["parameters"] = params

    try:
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=60)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Network error contacting Hugging Face: {e}")

    if resp.status_code != 200:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text[:300]
        raise HTTPException(status_code=502, detail=f"Hugging Face error ({resp.status_code}): {detail}")

    ctype = resp.headers.get("content-type", "")
    if "image" not in ctype.lower():
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text[:300]
        raise HTTPException(status_code=502, detail=f"Expected image from model but got non-image response: {detail}")

    try:
        img = Image.open(BytesIO(resp.content)).convert("RGB")
    except UnidentifiedImageError:
        raise HTTPException(status_code=502, detail="Received non-image bytes from model")

    return GenerateResponse(image=pil_to_base64_png(img), model=model_name)