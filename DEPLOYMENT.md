# Deployment Instructions - Vercel

This project is configured for deployment on Vercel using a hybrid approach:
- **Backend**: Python (FastAPI) running as Serverless Functions.
- **Frontend**: Flutter Web (Static Assets).

## Prerequisites
1.  **Vercel Account**: Sign up at [vercel.com](https://vercel.com).
2.  **Vercel CLI** (Optional but recommended): `npm i -g vercel`.
3.  **Flutter Installed**: To build the web app locally.

## Steps

### 1. Build the Flutter Web App
Since Vercel doesn't support Flutter builds natively, you must build the web assets locally and commit them (or deploy via CLI).

```bash
cd truth_guard_ai
flutter build web --release
```

### 2. Prepare for Deployment
Ensure the `truth_guard_ai/build/web` folder is **NOT** ignored by Git.
- Check `.gitignore` files.
- If `build/` is ignored, you can force add it:
  ```bash
  git add -f truth_guard_ai/build/web
  ```

### 3. Deploy
#### Option A: Connect to GitHub (Recommended)
1.  Push your code (including `truth_guard_ai/build/web`) to a GitHub repository.
2.  Go to Vercel Dashboard -> "Add New..." -> "Project".
3.  Import your repository.
4.  **Important**:
    - **Framework Preset**: Select "Other".
    - **Root Directory**: Keep as `./` (root).
    - **Build Command**: Leave empty (or `echo "Skipping build"`).
    - **Output Directory**: Leave default (Vercel will use `vercel.json`).
5.  Click **Deploy**.

#### Option B: Vercel CLI
Run the following command from the root directory:
```bash
vercel deploy
```

## Environment Variables
If you use API keys (like `GOOGLE_API_KEY`), add them in the Vercel Project Settings -> **Environment Variables**.
