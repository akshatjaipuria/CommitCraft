# CommitCraft AI | System Architecture & Design Specification

CommitCraft AI is an agentic Git assistant designed to automate the generation of high-quality, conventional commit messages. This document provides a high-level overview of the system architecture, component interactions, and engineering principles.

---

## 🏛️ System Overview

The application follows a **Modular Monolith** architecture with a clear separation between the frontend (Static Web), the backend API (FastAPI), and the Reasoning Engine (Agentic Loop).

### Core Components
1.  **Frontend (Vanilla JS/CSS)**: A premium, glassmorphic UI that handles user inputs and renders agent reasoning.
2.  **API Layer (FastAPI)**: A high-performance ASGI server that exposes endpoints for folder picking and commit generation.
3.  **Agentic Engine (Gemini 2.0/3.0)**: A multi-step reasoning loop built using the `google-genai` SDK.
4.  **Service Layer (GitTools)**: A dedicated service for safe interaction with the local Git CLI.

---

## 🤖 Reasoning Engine: Iterative Loops

CommitCraft AI supports two distinct execution strategies to balance between reliability and manual control. These are configured at server startup via CLI arguments.

### 1. Stateful Loop (Default)
- **SDK**: `client.chats.create`
- **Logic**: The agent uses API-managed chat sessions. This allows the model to maintain internal memory of previous tool calls and results, leading to highly accurate context-aware suggestions.
- **Workflow**: User Query → Agent Iteration (1-5) → Tool Use → Final Answer.

### 2. Stateless Loop
- **SDK**: `client.models.generate_content`
- **Logic**: For developers who want to see exactly how context is managed. The engine manually concatenates the full conversation history into a single string for every turn.
- **Workflow**: Context Building → Full Prompt Submission → Response Parsing → History Update.

---

## ⚡ Concurrency & Performance

To ensure a smooth user experience, CommitCraft AI is designed to be **Async-First**:

-   **Non-Blocking Event Loop**: All heavy I/O tasks (LLM calls, Git subprocesses) are offloaded to background worker threads using `anyio.to_thread`.
-   **Native Windows Integration**: The folder picker uses a separate PowerShell process to bypass the thread-safety limitations of GUI libraries like `tkinter`.
-   **Thread-Safe Logging**: Logs are managed via a background queue and a dedicated worker thread, preventing disk I/O from stalling the reasoning process.

---

## 🛠️ Service Interactions

### Git Service
The `services/git_tools.py` module acts as a safe abstraction layer. It uses `subprocess.run` with `CREATE_NO_WINDOW` flags to interact with the Git CLI without spawning intrusive terminal windows.

### Logger Service
The `core/logger.py` module provides a robust event-tracking system. It implements an exponential backoff retry mechanism to handle file-access conflicts, common in Windows environments.

---

## 📁 Directory Structure

```text
CommitCraft/
├── main.py              # FastAPI Entry Point & CLI Configuration
├── core/
│   ├── agent.py         # Reasoning Engine (Stateful/Stateless logic)
│   └── logger.py        # Thread-safe Async Logging
├── services/
│   └── git_tools.py     # Git CLI Abstraction Layer
├── static/
│   ├── index.html       # UI Structure
│   ├── style.css        # Premium Glassmorphic Design
│   └── script.js        # Frontend Interaction Logic
└── agent.log            # System & Agent Event Logs
```

---

## 🚀 Scalability & Future Work
- **Async Git**: Transitioning from `subprocess` to a native async git library.
- **Persistent Sessions**: Adding local storage to remember repository paths across reloads.
- **Custom Patterns**: Allowing users to define custom commit templates via the UI.
