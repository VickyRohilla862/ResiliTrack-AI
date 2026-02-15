import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
});

export const getAuthStatus = async () => {
  try {
    const response = await api.get('/api/auth/me');
    return response.data;
  } catch (error) {
    console.error('Error checking auth status:', error);
    throw error;
  }
};

export const registerUser = async (payload) => {
  try {
    const response = await api.post('/api/auth/register', payload);
    return response.data;
  } catch (error) {
    console.error('Error registering:', error);
    throw error;
  }
};

export const loginUser = async (payload) => {
  try {
    const response = await api.post('/api/auth/login', payload);
    return response.data;
  } catch (error) {
    console.error('Error logging in:', error);
    throw error;
  }
};

export const loginWithGoogle = async (credential) => {
  try {
    const response = await api.post('/api/auth/google', { credential });
    return response.data;
  } catch (error) {
    console.error('Error with Google login:', error);
    throw error;
  }
};

export const logoutUser = async () => {
  try {
    const response = await api.post('/api/auth/logout');
    return response.data;
  } catch (error) {
    console.error('Error logging out:', error);
    throw error;
  }
};

export const setUserApiKey = async (apiKey) => {
  try {
    const response = await api.post('/api/auth/api-key', { api_key: apiKey });
    return response.data;
  } catch (error) {
    console.error('Error saving API key:', error);
    throw error;
  }
};

// Analyze pandemic scenario
export const analyzeScenario = async (headline) => {
  try {
    const response = await api.post('/api/analyze', {
      headline: headline
    });
    return response.data;
  } catch (error) {
    console.error('Error analyzing scenario:', error);
    throw error;
  }
};

// Get analysis results
export const getAnalysisResults = async () => {
  try {
    const response = await api.get('/api/results');
    return response.data;
  } catch (error) {
    console.error('Error fetching results:', error);
    throw error;
  }
};

// Get chat history
export const getChatHistory = async () => {
  try {
    const response = await api.get('/api/chat-history');
    return response.data;
  } catch (error) {
    console.error('Error fetching chat history:', error);
    throw error;
  }
};

export const addChatMessage = async (payload) => {
  try {
    const response = await api.post('/api/chat-history', payload);
    return response.data;
  } catch (error) {
    console.error('Error adding chat message:', error);
    throw error;
  }
};

export const clearChatHistory = async () => {
  try {
    const response = await api.delete('/api/chat-history');
    return response.data;
  } catch (error) {
    console.error('Error clearing chat history:', error);
    throw error;
  }
};

export const deleteChatMessage = async (messageId) => {
  try {
    const response = await api.delete(`/api/chat-history/${messageId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting message:', error);
    throw error;
  }
};

export const deleteUserAccount = async () => {
  try {
    const response = await api.delete('/api/auth/account');
    return response.data;
  } catch (error) {
    console.error('Error deleting account:', error);
    throw error;
  }
};

export default api;
