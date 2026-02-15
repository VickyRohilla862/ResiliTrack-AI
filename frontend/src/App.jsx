import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ResiliencePage from './pages/ResiliencePage';
import DashboardPage from './pages/DashboardPage';
import SettingsPage from './pages/SettingsPage';
import LoginPage from './pages/LoginPage';
import {
  getAuthStatus,
  loginUser,
  registerUser,
  loginWithGoogle,
  logoutUser,
  setUserApiKey
} from './utils/api';

function App() {
  const [currentPage, setCurrentPage] = useState('resilience');
  const [analysisData, setAnalysisData] = useState(() => {
    try {
      const saved = localStorage.getItem('resilitrack_analysis_data');
      return saved ? JSON.parse(saved) : null;
    } catch (error) {
      return null;
    }
  });
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');
  const [fontSize, setFontSize] = useState(localStorage.getItem('fontSize') || 'medium');
  const [fontFamily, setFontFamily] = useState(
    localStorage.getItem('fontFamily') || "'IBM Plex Sans', 'Space Grotesk', sans-serif"
  );
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    const saved = localStorage.getItem('sidebarCollapsed');
    return saved !== null ? saved === 'true' : true; // Default to collapsed
  });
  const [authState, setAuthState] = useState({
    loading: true,
    authenticated: false,
    user: null,
    needsApiKey: false,
    error: ''
  });

  useEffect(() => {
    // Apply theme
    const themeClasses = [
      'dark-theme',
      'theme-ocean',
      'theme-forest',
      'theme-slate',
      'theme-mint',
      'theme-steel',
      'theme-rose',
      'theme-indigo',
      'theme-coffee',
      'theme-plum',
      'theme-charcoal',
      'theme-ice'
    ];
    document.body.classList.remove(...themeClasses);
    if (theme === 'dark') {
      document.body.classList.add('dark-theme');
    } else if (theme === 'ocean') {
      document.body.classList.add('theme-ocean');
    } else if (theme === 'forest') {
      document.body.classList.add('theme-forest');
    } else if (theme === 'slate') {
      document.body.classList.add('theme-slate');
    } else if (theme === 'mint') {
      document.body.classList.add('theme-mint');
    } else if (theme === 'steel') {
      document.body.classList.add('theme-steel');
    } else if (theme === 'rose') {
      document.body.classList.add('theme-rose');
    } else if (theme === 'indigo') {
      document.body.classList.add('theme-indigo');
    } else if (theme === 'coffee') {
      document.body.classList.add('theme-coffee');
    } else if (theme === 'plum') {
      document.body.classList.add('theme-plum');
    } else if (theme === 'charcoal') {
      document.body.classList.add('theme-charcoal');
    } else if (theme === 'ice') {
      document.body.classList.add('theme-ice');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    // Apply font size
    document.body.classList.remove('font-small', 'font-medium', 'font-large');
    document.body.classList.add(`font-${fontSize}`);
    localStorage.setItem('fontSize', fontSize);
  }, [fontSize]);

  useEffect(() => {
    // Apply font family
    const fontMap = {
      "'IBM Plex Sans', 'Space Grotesk', sans-serif": 'plex',
      "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif": 'segoe',
      'Arial, sans-serif': 'arial',
      "'Times New Roman', serif": 'times',
      "'Courier New', monospace": 'courier',
      'Georgia, serif': 'georgia'
    };
    document.body.classList.remove(
      'font-plex',
      'font-segoe',
      'font-arial',
      'font-times',
      'font-courier',
      'font-georgia'
    );
    document.body.classList.add(`font-${fontMap[fontFamily]}`);
    document.body.style.fontFamily = fontFamily;
    localStorage.setItem('fontFamily', fontFamily);
  }, [fontFamily]);

  useEffect(() => {
    const handleClear = () => {
      setAnalysisData(null);
    };

    window.addEventListener('resilitrack-clear', handleClear);
    return () => {
      window.removeEventListener('resilitrack-clear', handleClear);
    };
  }, []);

  useEffect(() => {
    const loadAuth = async () => {
      try {
        const status = await getAuthStatus();
        if (status?.authenticated) {
          const user = status.user || null;
          setAuthState({
            loading: false,
            authenticated: true,
            user,
            needsApiKey: !user?.has_api_key,
            error: ''
          });
        } else {
          setAuthState({
            loading: false,
            authenticated: false,
            user: null,
            needsApiKey: false,
            error: ''
          });
        }
      } catch (error) {
        setAuthState({
          loading: false,
          authenticated: false,
          user: null,
          needsApiKey: false,
          error: 'Unable to check login status.'
        });
      }
    };

    loadAuth();
  }, []);

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const toggleSidebar = () => {
    const newState = !sidebarCollapsed;
    setSidebarCollapsed(newState);
    localStorage.setItem('sidebarCollapsed', newState);
  };

  const handleAuthSuccess = (user) => {
    setAuthState({
      loading: false,
      authenticated: true,
      user,
      needsApiKey: !user?.has_api_key,
      error: ''
    });
  };

  const handleLogin = async (payload) => {
    try {
      const response = await loginUser(payload);
      handleAuthSuccess(response.user);
    } catch (error) {
      setAuthState((prev) => ({
        ...prev,
        error: error?.response?.data?.error || 'Login failed.'
      }));
    }
  };

  const handleRegister = async (payload) => {
    try {
      const response = await registerUser(payload);
      handleAuthSuccess(response.user);
    } catch (error) {
      setAuthState((prev) => ({
        ...prev,
        error: error?.response?.data?.error || 'Registration failed.'
      }));
    }
  };

  const handleGoogleLogin = async (credential) => {
    try {
      const response = await loginWithGoogle(credential);
      handleAuthSuccess(response.user);
    } catch (error) {
      setAuthState((prev) => ({
        ...prev,
        error: error?.response?.data?.error || 'Google login failed.'
      }));
    }
  };

  const handleLogout = async () => {
    try {
      await logoutUser();
    } finally {
      setAuthState({
        loading: false,
        authenticated: false,
        user: null,
        needsApiKey: false,
        error: ''
      });
    }
  };

  const handleApiKeySave = async (apiKey) => {
    try {
      const response = await setUserApiKey(apiKey);
      handleAuthSuccess(response.user);
      return response;
    } catch (error) {
      setAuthState((prev) => ({
        ...prev,
        error: error?.response?.data?.error || 'Failed to save API key.'
      }));
      throw error;
    }
  };

  if (authState.loading) {
    return (
      <div className="auth-loading">
        <div className="auth-spinner" />
        <span>Loading ResiliTrack AI...</span>
      </div>
    );
  }

  if (!authState.authenticated || authState.needsApiKey) {
    return (
      <LoginPage
        authState={authState}
        onLogin={handleLogin}
        onRegister={handleRegister}
        onGoogleLogin={handleGoogleLogin}
        onApiKeySave={handleApiKeySave}
        onLogout={handleLogout}
      />
    );
  }

  return (
    <div className="app-container">
      <Sidebar 
        currentPage={currentPage} 
        onPageChange={handlePageChange}
        collapsed={sidebarCollapsed}
        onToggle={toggleSidebar}
      />
      <div className="main-content">
        <div className={currentPage === 'resilience' ? 'page-active' : 'page-hidden'}>
          <ResiliencePage
            analysisData={analysisData}
            onAnalysisDataChange={setAnalysisData}
          />
        </div>
        <div className={currentPage === 'dashboard' ? 'page-active' : 'page-hidden'}>
          <DashboardPage analysisData={analysisData} />
        </div>
        <div className={currentPage === 'settings' ? 'page-active' : 'page-hidden'}>
          <SettingsPage
            theme={theme}
            setTheme={setTheme}
            fontSize={fontSize}
            setFontSize={setFontSize}
            fontFamily={fontFamily}
            setFontFamily={setFontFamily}
            user={authState.user}
            onLogout={handleLogout}
            onApiKeySave={handleApiKeySave}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
