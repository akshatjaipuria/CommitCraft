import subprocess
import anyio
import argparse
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from core.agent import CommitAgent

# --- Initialize Application ---
app = FastAPI(title="CommitCraft AI")
agent = CommitAgent()

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRequest(BaseModel):
    """Schema for the generation request."""
    query: str
    repo_path: str

# --- Static File Serving ---
@app.get("/")
async def serve_index(): 
    return FileResponse("static/index.html")

@app.get("/{filename}")
async def serve_static(filename: str):
    """Serves CSS, JS, and other assets from the static folder."""
    file_path = os.path.join("static", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}

# --- API Endpoints ---
@app.post("/generate")
async def generate_commit(request: AgentRequest):
    """
    Triggers the agentic reasoning process.
    Uses the execution strategy (stateful/stateless) defined at server startup.
    """
    return await agent.run(request.query, request.repo_path, app.state.agent_mode)

@app.post("/pick-folder")
async def pick_folder():
    """
    Opens a native Windows folder browser dialog using a PowerShell subprocess.
    This bypasses thread-safety issues found in libraries like tkinter.
    """
    try:
        # PowerShell command to show the FolderBrowserDialog
        ps_cmd = [
            "powershell", "-NoProfile", "-Command",
            "Add-Type -AssemblyName System.Windows.Forms; "
            "$f = New-Object System.Windows.Forms.FolderBrowserDialog; "
            "$f.Description = 'Select Repository Folder'; "
            "if($f.ShowDialog() -eq 'OK') { $f.SelectedPath } else { '' }"
        ]
        
        # 0x08000000 = CREATE_NO_WINDOW
        result = await anyio.to_thread.run_sync(
            lambda: subprocess.check_output(ps_cmd, text=True, encoding="utf-8", errors="replace", creationflags=0x08000000).strip()
        )
        return {"path": result.replace('/', '\\') if result else ""}
    except Exception as e:
        return {"error": str(e), "path": ""}

# --- Server Startup ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CommitCraft AI - Agentic Git Assistant")
    parser.add_argument("--stateful", action="store_true", help="Use API-managed chat sessions (default)")
    parser.add_argument("--stateless", action="store_true", help="Use manual context management")
    args = parser.parse_args()

    # Configuration precedence: --stateless overrides the default stateful behavior
    app.state.agent_mode = "stateless" if args.stateless else "stateful"
    
    print(f"\n🚀 CommitCraft AI is starting...")
    print(f"🔧 Strategy: {app.state.agent_mode.upper()} LOOP")
    print(f"🌐 Server: http://localhost:8000\n")

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
