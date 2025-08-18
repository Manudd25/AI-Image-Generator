# 🖼️ AI Image Generator 

A simple **AI-powered image generator** built with:
- **Backend:** FastAPI (Python) + Hugging Face Inference API  
- **Frontend:** React (Vite) + Axios
- **Deployment:** Azure App Service / Azure Static Web Apps  


Users can type a text prompt and instantly generate an AI image using **Stable Diffusion XL Turbo**.

---

## 🚀 Features
- Generate images from text prompts  
- Backend calls Hugging Face API securely with your token  
- Frontend React app with prompt input + image preview  
- CORS-enabled so frontend and backend work locally  
- Easy to extend with extra options (steps, width, height, etc.)
- Deployable on **Azure** (App Service for backend + Static Web App for frontend)


---

  
## 🤝 Collaboration

We split tasks between two developers:

Person A (Backend)

Setup FastAPI server

Connect to Hugging Face API

Handle prompt → image request

Return Base64-encoded images

Configure CORS

Person B (Frontend)

Build React interface

Create prompt input + button

Display generated image

Connect with backend using Axios

Add UI improvements (loading state, extra controls)
