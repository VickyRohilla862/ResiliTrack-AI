import React, { useEffect, useMemo, useRef, useState } from 'react';

function LoginPage({
  authState,
  onLogin,
  onRegister,
  onGoogleLogin,
  onApiKeySave,
  onLogout
}) {
  const googleButtonRef = useRef(null);
  const [mode, setMode] = useState('login');
  const [formState, setFormState] = useState({
    name: '',
    email: '',
    password: ''
  });
  const [apiKey, setApiKey] = useState('');
  const [googleReady, setGoogleReady] = useState(false);

  const googleClientId = useMemo(() => import.meta.env.VITE_GOOGLE_CLIENT_ID || 'YOUR_GOOGLE_CLIENT_ID', []);

  useEffect(() => {
    if (!googleButtonRef.current) return;
    if (!googleClientId || googleClientId === 'YOUR_GOOGLE_CLIENT_ID') {
      setGoogleReady(false);
      return;
    }

    const tryInit = () => {
      if (!window.google || !window.google.accounts || !window.google.accounts.id) {
        return false;
      }

      window.google.accounts.id.initialize({
        client_id: googleClientId,
        callback: (response) => {
          if (response?.credential) {
            onGoogleLogin(response.credential);
          }
        }
      });

      window.google.accounts.id.renderButton(googleButtonRef.current, {
        theme: 'outline',
        size: 'large',
        width: 320,
        text: 'continue_with'
      });
      setGoogleReady(true);
      return true;
    };

    if (tryInit()) return;

    let attempts = 0;
    const timer = setInterval(() => {
      attempts += 1;
      if (tryInit() || attempts > 12) {
        clearInterval(timer);
      }
    }, 400);

    return () => clearInterval(timer);
  }, [googleClientId, onGoogleLogin]);

  const handleSubmit = (event) => {
    event.preventDefault();
    if (mode === 'login') {
      onLogin({ email: formState.email, password: formState.password });
    } else {
      onRegister({ name: formState.name, email: formState.email, password: formState.password });
    }
  };

  const handleApiKeySubmit = (event) => {
    event.preventDefault();
    if (apiKey.trim()) {
      Promise.resolve(onApiKeySave(apiKey.trim()))
        .then(() => setApiKey(''))
        .catch(() => {});
    }
  };

  const isAuthenticated = authState?.authenticated;
  const needsApiKey = authState?.needsApiKey;

  return (
    <div className="auth-shell">
      <div className="auth-glow" />
      <div className="auth-card">
        <div className="auth-header">
          <span className="auth-tag">ResiliTrack AI</span>
          <h1>{needsApiKey ? 'Add your Gemini API key' : 'Sign in to continue'}</h1>
          <p>
            {needsApiKey
              ? 'Your usage should run on your own Google AI Studio key.'
              : 'Use your Google account or email to unlock the resilience workspace.'}
          </p>
        </div>

        {!isAuthenticated && (
          <div className="auth-tabs" role="tablist" aria-label="Login mode">
            <button
              type="button"
              className={mode === 'login' ? 'auth-tab active' : 'auth-tab'}
              onClick={() => setMode('login')}
              role="tab"
              aria-selected={mode === 'login'}
            >
              Log in
            </button>
            <button
              type="button"
              className={mode === 'register' ? 'auth-tab active' : 'auth-tab'}
              onClick={() => setMode('register')}
              role="tab"
              aria-selected={mode === 'register'}
            >
              Create account
            </button>
          </div>
        )}

        {!isAuthenticated && (
          <div className="auth-google">
            <div className="auth-google-slot" ref={googleButtonRef} />
            {!googleReady && (
              <button
                type="button"
                className="auth-google-fallback"
                disabled={!googleClientId || googleClientId === 'YOUR_GOOGLE_CLIENT_ID'}
              >
                Continue with Google
              </button>
            )}
            {(googleClientId === 'YOUR_GOOGLE_CLIENT_ID') && (
              <div className="auth-hint">
                Add VITE_GOOGLE_CLIENT_ID and GOOGLE_CLIENT_ID to enable Google login.
              </div>
            )}
          </div>
        )}

        {!isAuthenticated && (
          <form className="auth-form" onSubmit={handleSubmit}>
            {mode === 'register' && (
              <label className="auth-field">
                <span>Name</span>
                <input
                  type="text"
                  value={formState.name}
                  onChange={(event) => setFormState({ ...formState, name: event.target.value })}
                  placeholder="Ada Lovelace"
                  required
                />
              </label>
            )}
            <label className="auth-field">
              <span>Email</span>
              <input
                type="email"
                value={formState.email}
                onChange={(event) => setFormState({ ...formState, email: event.target.value })}
                placeholder="you@gmail.com"
                required
              />
            </label>
            <label className="auth-field">
              <span>Password</span>
              <input
                type="password"
                value={formState.password}
                onChange={(event) => setFormState({ ...formState, password: event.target.value })}
                placeholder="Minimum 6 characters"
                required
              />
            </label>
            <button type="submit" className="auth-submit">
              {mode === 'login' ? 'Log in' : 'Create account'}
            </button>
          </form>
        )}

        {isAuthenticated && needsApiKey && (
          <form className="auth-form" onSubmit={handleApiKeySubmit}>
            <label className="auth-field">
              <span>Gemini API key</span>
              <input
                type="password"
                value={apiKey}
                onChange={(event) => setApiKey(event.target.value)}
                placeholder="AIza..."
                required
              />
            </label>
            <div className="auth-meta">
              Create one at{' '}
              <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer">
                Google AI Studio
              </a>
              .
            </div>
            <button type="submit" className="auth-submit">
              Save API key
            </button>
          </form>
        )}

        {authState?.error && (
          <div className="auth-error" role="alert">
            {authState.error}
          </div>
        )}

        {isAuthenticated && (
          <div className="auth-footer">
            <span>Signed in as {authState?.user?.email || 'user'}.</span>
            <button type="button" className="auth-link" onClick={onLogout}>
              Log out
            </button>
          </div>
        )}
      </div>
      <div className="auth-side">
        {!needsApiKey && (
          <div className="auth-side-card">
            <h2>Private usage, your key</h2>
            <p>
              You control spend by using your own Gemini API key. We never charge usage to the
              default project.
            </p>
            <ul>
              <li>Google OAuth or email login</li>
              <li>Per-user API key storage</li>
              <li>Chat locked until authenticated</li>
            </ul>
          </div>
        )}
        {needsApiKey && (
          <div className="auth-side-card">
            <h2>Get your API key</h2>
            <p>Follow these simple steps to create your own Gemini API key:</p>
            <ol className="auth-steps">
              <li>
                <strong>Visit Google AI Studio</strong>
                <span>Go to <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer">aistudio.google.com/app/apikey</a></span>
              </li>
              <li>
                <strong>Create a new API key</strong>
                <span>Click the "Create API Key" button (it's free)</span>
              </li>
              <li>
                <strong>Copy your key</strong>
                <span>Click the copy icon next to your new API key</span>
              </li>
              <li>
                <strong>Paste here</strong>
                <span>Paste it in the input field on the left</span>
              </li>
              <li>
                <strong>Save and start</strong>
                <span>Click "Save API key" to unlock ResiliTrack AI</span>
              </li>
            </ol>
          </div>
        )}
      </div>
    </div>
  );
}

export default LoginPage;
