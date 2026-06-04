# TruthGuard AI

**TruthGuard AI** is an advanced, multi-agent platform designed to combat misinformation in real-time. It combines a high-performance Flutter frontend with a robust Python backend powered by Google's Gemini models to verify claims, provide evidence-based verdicts, and generate educational awareness content.

## 🚀 Key Features

*   **🕵️‍♂️ Multi-Agent Verification System**:
    *   **Antigravity Agent**: Evidence-first verification engine that cross-references claims with trusted sources (WHO, UN, peer-reviewed journals).
    *   **Deep Search**: Performs exhaustive research for complex queries.
    *   **LLM Auditor**: Ensures accuracy and safety of generated responses.
*   **💬 Interactive Chat Interface**: Ask TruthGuard to verify any claim, rumor, or news piece instantly.
*   **🎨 Nano Banana Image Generation**: Automatically generates shareable "TRUE" or "FALSE" educational posters (infographics) using the **Gemini 2.5 Flash Image** model to visually debunk misinformation.
*   **🔥 Trending Misinformation Feed**: Stay updated with a curated feed of currently circulating false claims.
*   **📱 Cross-Platform Support**: Built with Flutter for seamless performance on iOS, Android, and Web.

## 🏗️ Architecture

The project follows a modern microservices architecture:

*   **Frontend**: `truth_guard_ai/` (Flutter)
    *   Implements Clean Architecture (Presentation, Domain, Data layers).
    *   Uses Riverpod for state management.
    *   GoRouter for navigation.
*   **Backend**: `backend/` (Python FastAPI)
    *   **`antigravity/`**: The core verification service.
    *   **`api-gateway/`**: Central entry point for routing requests.
    *   **`deep-search/`**: Advanced research agent.
    *   **`safety-plugins/`**: Content safety and moderation.

## 🛠️ Getting Started

### Prerequisites

*   **Flutter SDK**: [Install Flutter](https://docs.flutter.dev/get-started/install)
*   **Python 3.10+**: [Install Python](https://www.python.org/downloads/)
*   **Google Cloud API Key**: Access to Gemini models (AI Studio or Vertex AI).

### 1. Backend Setup

1.  Navigate to the Antigravity backend directory:
    ```bash
    cd backend/antigravity
    ```
2.  Create a `.env` file and add your Google API Key:
    ```env
    GOOGLE_API_KEY=your_api_key_here
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the server (from the project root):
    ```bash
    # Run from D:\ai-missinformation-truth_guard-ai2
    python -m backend.antigravity.main
    ```
    The server will start at `http://0.0.0.0:8002`.

### 2. Frontend Setup

1.  Navigate to the Flutter project directory:
    ```bash
    cd truth_guard_ai
    ```
2.  Install dependencies:
    ```bash
    flutter pub get
    ```
3.  Run the app:
    ```bash
    flutter run
    ```

## 🧪 Usage

1.  Open the app.
2.  On the **Home Screen**, browse trending false claims or use the "Analyze Now" input box.
3.  Type a claim (e.g., "Drinking hot water cures all diseases") and tap **Analyze Now**.
4.  You will be navigated to the **Chat Screen** where the Antigravity Agent will:
    *   Search for evidence.
    *   Provide a verdict (TRUE/FALSE/MISLEADING).
    *   (Optional) Generate an educational poster if requested.

## 🛡️ Security

*   Environment variables (`.env`) are git-ignored to protect sensitive API keys.
*   Backend services are isolated for better scalability and security.

---

*Built with ❤️ by the TruthGuard Team*
