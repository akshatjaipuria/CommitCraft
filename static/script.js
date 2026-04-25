/**
 * CommitCraft AI - Frontend Controller
 * Manages UI interactions, API communication, and state.
 */

// --- UI Elements ---
const DOM = {
    repoPath: document.getElementById('repo-path'),
    queryInput: document.getElementById('query-input'),
    browseBtn: document.getElementById('browse-btn'),
    generateBtn: document.getElementById('generate-btn'),
    mainLoader: document.getElementById('main-loader'),
    thinkingBar: document.getElementById('thinking-bar'),
    statusLabel: document.getElementById('agent-status'),
    resultSection: document.getElementById('result-section'),
    commitMessage: document.getElementById('commit-message'),
    rationale: document.getElementById('agent-rationale'),
    copyBtn: document.getElementById('copy-btn'),
    copyFeedback: document.getElementById('copy-feedback'),
    btnText: document.querySelector('.btn-text')
};

/**
 * Updates the visual status of the agent.
 * @param {string} text - Message to display
 * @param {boolean} isThinking - Whether to show the progress bar
 */
function updateStatus(text, isThinking = false) {
    DOM.statusLabel.textContent = text;
    isThinking ? DOM.thinkingBar.classList.remove('hidden') : DOM.thinkingBar.classList.add('hidden');
}

/**
 * Opens the native Windows folder picker via the backend.
 */
async function handleBrowse() {
    try {
        DOM.browseBtn.disabled = true;
        const response = await fetch('/pick-folder', { method: 'POST' });
        const data = await response.json();
        if (data.path) DOM.repoPath.value = data.path;
    } catch (err) {
        console.error("Browse Error:", err);
    } finally {
        DOM.browseBtn.disabled = false;
    }
}

/**
 * Triggers the commit generation process.
 */
async function handleGenerate() {
    const query = DOM.queryInput.value.trim();
    const repoPath = DOM.repoPath.value.trim();
    
    if (!query || !repoPath) {
        updateStatus('Missing information: Please provide instructions and a repository path.');
        return;
    }

    // Enter Loading State
    DOM.resultSection.classList.add('hidden');
    DOM.generateBtn.disabled = true;
    DOM.mainLoader.classList.remove('hidden');
    DOM.btnText.classList.add('hidden');
    updateStatus('Analyzing repository changes...', true);

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, repo_path: repoPath })
        });
        
        const data = await response.json();

        if (data.error) {
            updateStatus('Error: ' + data.error);
            return;
        }

        // Render Result
        if (data.result) {
            DOM.commitMessage.textContent = data.result;
            DOM.rationale.textContent = data.reasoning || "Based on staged changes and commit history.";
            DOM.resultSection.classList.remove('hidden');
            updateStatus('Analysis complete.');
            
            // Smoothly scroll to the new suggestion
            setTimeout(() => {
                DOM.resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        }
    } catch (err) {
        updateStatus('Server error: Connection lost.');
    } finally {
        DOM.generateBtn.disabled = false;
        DOM.mainLoader.classList.add('hidden');
        DOM.btnText.classList.remove('hidden');
    }
}

/**
 * Handles copying the commit message to the clipboard.
 */
function handleCopy() {
    const text = DOM.commitMessage.textContent;
    if (!text) return;

    navigator.clipboard.writeText(text).then(() => {
        DOM.copyFeedback.style.opacity = '1';
        setTimeout(() => DOM.copyFeedback.style.opacity = '0', 2000);
    });
}

// --- Event Listeners ---
DOM.browseBtn.addEventListener('click', handleBrowse);
DOM.generateBtn.addEventListener('click', handleGenerate);
DOM.copyBtn.addEventListener('click', handleCopy);
