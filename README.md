# 🚀 CommitCraft AI

**CommitCraft AI** is a premium, agentic Git assistant designed to write high-quality, conventional commit messages for you. By leveraging the power of Gemini 3.0, it analyzes your repository's staged changes and history to craft the perfect description of your work.

[Link to the demo](https://youtu.be/WDHDgPPjDtI)

## ✨ Features

*   **Agentic Reasoning**: Uses a multi-step "Chain-of-Thought" loop to gather context before writing.
*   **Deep Repository Analysis**: Automatically retrieves staged diffs, file statuses, and recent commit history.
*   **Dual Execution Strategies**:
    *   **Stateful (Default)**: Uses API-managed chat sessions for maximum reliability.
    *   **Stateless**: Uses manual context concatenation for transparent history management.
*   **Premium UI**: A modern, glassmorphic web interface with real-time status updates.
*   **Native Windows Integration**: Built-in PowerShell folder picker and robust file-safe logging.

## 🛠️ Tech Stack

*   **Backend**: Python, FastAPI, Uvicorn
*   **LLM**: Google Gemini (`google-genai` SDK)
*   **Frontend**: HTML5, Vanilla CSS (Glassmorphism), JavaScript
*   **Concurrency**: AnyIO for non-blocking I/O

## 🚀 Getting Started

### 1. Prerequisites
*   Python 3.10+
*   Git installed and in your PATH
*   A Gemini API Key (get one at [Google AI Studio](https://aistudio.google.com/))

### 2. Installation
Clone the repository and install dependencies:
```powershell
git clone https://github.com/your-repo/CommitCraft.git
cd CommitCraft
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory and add your API key:
```text
GEMINI_API_KEY=your_api_key_here
```

### 4. Running the App
Start the server in the default **Stateful** mode:
```powershell
python main.py
```
Or try the **Stateless** mode:
```powershell
python main.py --stateless
```

Open your browser and navigate to `http://localhost:8000`.

## 📖 How It Works

1.  **Select Repo**: Use the native folder picker to select your project directory.
2.  **Give Instructions**: (Optional) Tell the agent if you want a specific style (e.g., "Make it funny" or "Be very technical").
3.  **Run Agent**: Watch as the agent iterates through your repository to understand your changes.
4.  **Copy & Commit**: Copy the generated message and use it for your `git commit`.

## 📜 License
MIT License. See `LICENSE` for more details.

---
*Built with ❤️ by Antigravity*
