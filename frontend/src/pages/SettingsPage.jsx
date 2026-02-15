import React, { useState } from 'react';
import { clearChatHistory, deleteUserAccount } from '../utils/api';

function SettingsPage({
  theme,
  setTheme,
  fontSize,
  setFontSize,
  fontFamily,
  setFontFamily,
  user,
  onLogout,
  onApiKeySave
}) {
  const [chatStatus, setChatStatus] = useState('');
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [confirmAction, setConfirmAction] = useState(null);
  const [apiKey, setApiKey] = useState('');
  const [apiKeyStatus, setApiKeyStatus] = useState('');

  const handleDeleteChat = () => {
    setChatStatus('');
    setConfirmAction('delete-chat');
    setIsConfirmOpen(true);
  };

  const handleDeleteAccount = () => {
    setApiKeyStatus('');
    setConfirmAction('delete-account');
    setIsConfirmOpen(true);
  };

  const handleConfirmDelete = async () => {
    try {
      if (confirmAction === 'delete-chat') {
        await clearChatHistory();
        localStorage.removeItem('resilitrack_analysis_data');
        window.dispatchEvent(new Event('resilitrack-clear'));
        window.dispatchEvent(new Event('resilitrack-chat-cleared'));
        setChatStatus('Chat is now cleared.');
      } else if (confirmAction === 'delete-account') {
        await deleteUserAccount();
        window.location.href = import.meta.env.BASE_URL;
      }
    } catch (error) {
      if (confirmAction === 'delete-chat') {
        setChatStatus('Unable to clear chat right now.');
      } else {
        setApiKeyStatus('Unable to delete account right now.');
      }
    } finally {
      setIsConfirmOpen(false);
      setConfirmAction(null);
    }
  };

  const handleCancelDelete = () => {
    setIsConfirmOpen(false);
    setConfirmAction(null);
  };

  const handleApiKeySubmit = async (event) => {
    event.preventDefault();
    if (!apiKey.trim()) return;
    try {
      await onApiKeySave(apiKey.trim());
      setApiKey('');
      setApiKeyStatus('API key updated.');
    } catch (error) {
      setApiKeyStatus('Unable to update API key.');
    }
  };

  return (
    <div className="page settings-page">
      <div className="header">
        <h1>Settings</h1>
        <p>Customize your experience</p>
      </div>
      <div className="settings-container">
        <div className="setting-group">
          <h3>Appearance</h3>
          <div className="setting-item">
            <label htmlFor="themeSelect">Theme</label>
            <select 
              id="themeSelect" 
              value={theme}
              onChange={(e) => setTheme(e.target.value)}
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="ocean">Ocean</option>
              <option value="forest">Forest</option>
              <option value="slate">Slate</option>
              <option value="mint">Mint</option>
              <option value="steel">Steel</option>
              <option value="rose">Rose</option>
              <option value="indigo">Indigo</option>
              <option value="coffee">Coffee</option>
              <option value="plum">Plum</option>
              <option value="charcoal">Charcoal</option>
              <option value="ice">Ice</option>
            </select>
          </div>
        </div>
        <div className="setting-group">
          <h3>Typography</h3>
          <div className="setting-item">
            <label htmlFor="fontSelect">Font Family</label>
            <select 
              id="fontSelect"
              value={fontFamily}
              onChange={(e) => setFontFamily(e.target.value)}
            >
              <option value="'IBM Plex Sans', 'Space Grotesk', sans-serif">Default (IBM Plex Sans)</option>
              <option value="Arial, sans-serif">Arial</option>
              <option value="'Times New Roman', serif">Times New Roman</option>
              <option value="'Courier New', monospace">Courier New</option>
              <option value="Georgia, serif">Georgia</option>
              <option value="'Comic Sans MS', 'Comic Sans', cursive">Comic Sans</option>
            </select>
          </div>
          <div className="setting-item">
            <label htmlFor="fontSizeSelect">Font Size</label>
            <select 
              id="fontSizeSelect"
              value={fontSize}
              onChange={(e) => setFontSize(e.target.value)}
            >
              <option value="small">Small</option>
              <option value="medium">Medium</option>
              <option value="large">Large</option>
            </select>
          </div>
        </div>

        <div className="setting-group">
          <h3>Data</h3>
          <div className="setting-item">
            <button type="button" className="danger-link" onClick={handleDeleteChat}>
              Delete chat
            </button>
            {chatStatus && (
              <div className="setting-status" role="status">
                {chatStatus}
              </div>
            )}
          </div>
        </div>

        <div className="setting-group">
          <h3>Account</h3>
          <div className="setting-item">
            <div className="setting-meta">
              Signed in as {user?.email || 'user'}.
            </div>
            <button type="button" className="secondary-link" onClick={onLogout}>
              Log out
            </button>
          </div>
          <form className="setting-item" onSubmit={handleApiKeySubmit}>
            <label htmlFor="apiKeyInput">Gemini API key</label>
            <input
              id="apiKeyInput"
              type="password"
              className="api-key-input"
              value={apiKey}
              onChange={(event) => setApiKey(event.target.value)}
              placeholder="Your new Gemini API key"
            />
            <button type="submit" className="primary-link">
              Update API key
            </button>
            <p className="setting-help">
              Create one at <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer">Google AI Studio</a>.
            </p>
            {apiKeyStatus && (
              <div className="setting-status" role="status">
                {apiKeyStatus}
              </div>
            )}
          </form>
          <div className="setting-item">
            <button type="button" className="danger-link" onClick={handleDeleteAccount}>
              Delete account
            </button>
          </div>
        </div>
      </div>

      {isConfirmOpen && (
        <div className="modal-backdrop" role="presentation">
          <div className="modal" role="dialog" aria-modal="true" aria-labelledby="confirm-title">
            {confirmAction === 'delete-chat' && (
              <>
                <h4 id="confirm-title">Clear chat history?</h4>
                <p>This will remove all saved chat messages.</p>
              </>
            )}
            {confirmAction === 'delete-account' && (
              <>
                <h4 id="confirm-title">Delete account?</h4>
                <p>This will permanently delete your account and all associated data. This action cannot be undone.</p>
              </>
            )}
            <div className="modal-actions">
              <button type="button" className="modal-cancel" onClick={handleCancelDelete}>
                Cancel
              </button>
              <button type="button" className="modal-danger" onClick={handleConfirmDelete}>
                {confirmAction === 'delete-chat' ? 'Clear chat' : 'Delete account'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SettingsPage;
