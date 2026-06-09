# Deployment Instructions - Vercel

This project is configured for seamless deployment on Vercel as a monorepo containing:
- **Backend**: Python FastAPI service running as Vercel Serverless Functions.
- **Frontend**: React (Vite/TypeScript) SPA built and hosted as static assets.

The repository is configured with a root-level `vercel.json` that automatically orchestrates both builds and routes incoming traffic:
* `/api/*` routes are handled by the FastAPI serverless functions (`backend/factguard/main.py`).
* All other routes are handled by the React static build (`frontend/dist/`).

---

## 🚀 Deployment Steps (via GitHub Integration)

This is the recommended, zero-setup approach to deploy the application.

### Step 1: Add Environment Variables in Vercel
Since the backend uses Google's Gemini models, you must provide your Gemini API key.
1. Go to your **Vercel Dashboard** and click **Add New...** -> **Project**.
2. Import your repository: `truth_guard-ai-misinformation-detector-main`.
3. In the **Configure Project** section, expand **Environment Variables**.
4. Add the following variable:
   * **Name**: `GOOGLE_API_KEY`
   * **Value**: *[Your Gemini API Key]*
5. Expand **Build and Development Settings**:
   * **Framework Preset**: Keep as **Other** or **Vite**.
   * **Root Directory**: Keep as `./` (root).
   * **Build Command**: Keep empty (or default). Vercel reads `vercel.json` to build the frontend and backend automatically.

### Step 2: Deploy
1. Click the **Deploy** button.
2. Vercel will install dependencies, compile the React frontend, set up the Python FastAPI serverless functions, and publish your site.

---

## 🛠️ Deploying via Vercel CLI (Alternative)

If you have Vercel CLI installed locally and authenticated:

1. Run the following command from the root directory:
   ```bash
   npx vercel --prod
   ```
2. Follow the interactive prompts to link the project and deploy it.
3. Make sure to set your `GOOGLE_API_KEY` in the Vercel Dashboard settings under the deployed project.
