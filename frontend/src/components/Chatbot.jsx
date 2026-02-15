import React, { useState, useRef, useEffect } from 'react';
import { analyzeScenario, getChatHistory, addChatMessage, deleteChatMessage } from '../utils/api';

function Chatbot({ onAnalysisComplete, onSelectAnalysis }) {
  const aspectOrder = [
    'Economic Stability',
    'Defense & Strategic Security',
    'Healthcare & Biological Readiness',
    'Cyber Resilience & Digital Infrastructure',
    'Demographic & Social Stability',
    'Energy Security',
    'Debt & Fiscal Sustainability'
  ];
  const defaultMessages = [
    {
      id: 'welcome',
      text: 'Welcome to ResiliTrack AI.',
      sender: 'bot',
      isWelcome: true
    }
  ];
  const [messages, setMessages] = useState(defaultMessages);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [expandedMessages, setExpandedMessages] = useState(() => new Set());
  const [expandedSummaries, setExpandedSummaries] = useState(() => new Set());
  const messagesEndRef = useRef(null);
  const containerRef = useRef(null);
  const shouldAutoScrollRef = useRef(false);

  const createMessageId = () => `${Date.now()}-${Math.random().toString(16).slice(2)}`;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (!shouldAutoScrollRef.current) return;
    scrollToBottom();
    shouldAutoScrollRef.current = false;
  }, [messages]);

  const refreshHistory = async () => {
    try {
      const response = await getChatHistory();
      const history = response?.history || [];
      if (!history.length) {
        shouldAutoScrollRef.current = false;
        setMessages(defaultMessages);
        if (onAnalysisComplete) {
          onAnalysisComplete(null);
        }
        return;
      }
      const mapped = history.map((item) => ({
        id: item.id,
        text: item.message,
        sender: item.sender,
        scenario: item.scenario,
        analysisData: item.analysis_data || null,
        createdAt: item.created_at
      }));
      shouldAutoScrollRef.current = true;
      setMessages([...defaultMessages, ...mapped]);
      const lastWithAnalysis = [...mapped].reverse().find((item) => item.analysisData);
      if (lastWithAnalysis && onAnalysisComplete) {
        onAnalysisComplete(lastWithAnalysis.analysisData);
      }
    } catch (error) {
      setMessages(defaultMessages);
    }
  };

  useEffect(() => {
    refreshHistory();
  }, []);

  useEffect(() => {
    const handleClear = () => {
      setMessages(defaultMessages);
    };
    const handleFocus = () => {
      refreshHistory();
    };

    window.addEventListener('resilitrack-chat-cleared', handleClear);
    window.addEventListener('focus', handleFocus);
    return () => {
      window.removeEventListener('resilitrack-chat-cleared', handleClear);
      window.removeEventListener('focus', handleFocus);
    };
  }, []);

  const findLastBotMessageForScenario = (scenarioText, list) => {
    if (!scenarioText) return null;
    const source = list || messages;
    return [...source]
      .reverse()
      .find((message) => message.sender === 'bot' && message.scenario === scenarioText) || null;
  };

  const handleRegenerate = (scenarioText, messageId, sender) => {
    if (!scenarioText || isLoading) return;

    if (sender === 'user') {
      const lastBotMessage = findLastBotMessageForScenario(scenarioText, messages);
      if (!lastBotMessage) return;
      runScenario(scenarioText, lastBotMessage.id);
      return;
    }

    runScenario(scenarioText, messageId);
  };

  const runScenario = async (scenarioText, botMessageIdToDelete) => {
    setIsLoading(true);
    shouldAutoScrollRef.current = true;
    const pendingId = createMessageId();

    const pendingMessage = {
      id: pendingId,
      text: 'Analyzing scenario... preparing resilience update.',
      sender: 'bot',
      scenario: scenarioText,
      pending: true,
      createdAt: Date.now()
    };

    // Delete old bot message from database if we have a database ID
    if (botMessageIdToDelete && typeof botMessageIdToDelete === 'number') {
      deleteChatMessage(botMessageIdToDelete).catch(() => {});
    }

    // Delete old bot message and add pending in a single setState to avoid race conditions
    setMessages((prev) => {
      let updated = prev;

      if (botMessageIdToDelete) {
        // Always delete the bot message by ID (never delete user messages)
        updated = prev.filter((message) => message.id !== botMessageIdToDelete);
      }

      // Add pending message in same update
      return [...updated, pendingMessage];
    });

    try {
      const result = await analyzeScenario(scenarioText);

      const finalText = result.analysis || 'Analysis completed. Check the charts for results.';
      setMessages((prev) => prev.map((message) => (
        message.id === pendingId
          ? {
              ...message,
              text: finalText,
              analysisData: result,
              pending: false
            }
          : message
      )));

      addChatMessage({
        message: finalText,
        sender: 'bot',
        scenario: scenarioText,
        analysis_data: result
      }).then((response) => {
        if (response?.message_id) {
          // Update the message with the database ID
          setMessages((prev) => prev.map((message) => (
            message.id === pendingId
              ? { ...message, id: response.message_id }
              : message
          )));
        }
      }).catch(() => {});

      if (onAnalysisComplete) {
        onAnalysisComplete(result);
      }
    } catch (error) {
      const errorText = 'Sorry, there was an error analyzing your scenario. Please try again.';
      setMessages((prev) => prev.map((message) => (
        message.id === pendingId
          ? {
              ...message,
              text: errorText,
              retryable: true,
              pending: false
            }
          : message
      )));
      addChatMessage({
        message: errorText,
        sender: 'bot',
        scenario: scenarioText
      }).then((response) => {
        if (response?.message_id) {
          // Update the error message with the database ID
          setMessages((prev) => prev.map((message) => (
            message.id === pendingId
              ? { ...message, id: response.message_id }
              : message
          )));
        }
      }).catch(() => {});
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (event) => {
    event.preventDefault();

    const scenarioText = input.trim();
    if (!scenarioText) return;

    const userMessageId = createMessageId();
    const userMessage = {
      id: userMessageId,
      text: scenarioText,
      sender: 'user',
      scenario: scenarioText
    };

    shouldAutoScrollRef.current = true;
    setMessages((prev) => [...prev, userMessage]);
    addChatMessage({
      message: scenarioText,
      sender: 'user',
      scenario: scenarioText
    }).then((response) => {
      if (response?.message_id) {
        // Update user message with database ID
        setMessages((prev) => prev.map((msg) => (
          msg.id === userMessageId
            ? { ...msg, id: response.message_id }
            : msg
        )));
      }
    }).catch(() => {});
    setInput('');
    await runScenario(scenarioText);
  };

  const buildImpactSummary = (analysisData) => {
    if (!analysisData?.impacts?.length) return [];

    const countryMap = new Map();
    analysisData.impacts.forEach((impact) => {
      const country = impact.country;
      if (!countryMap.has(country)) {
        countryMap.set(country, new Map());
      }
      const aspectMap = countryMap.get(country);
      const aspect = impact.aspect;
      const existing = aspectMap.get(aspect) || { delta: 0, reasons: new Set() };
      existing.delta += impact.delta || 0;
      if (impact.reason) {
        existing.reasons.add(impact.reason);
      }
      aspectMap.set(aspect, existing);
    });

    const countrySummary = [];
    countryMap.forEach((aspectMap, country) => {
      const aspects = Array.from(aspectMap.entries()).map(([aspect, data]) => ({
        aspect,
        delta: data.delta,
        reason: Array.from(data.reasons)[0]
      }));
      const totalImpact = aspects.reduce((sum, item) => sum + Math.abs(item.delta), 0);
      countrySummary.push({ country, totalImpact, aspects });
    });

    return countrySummary
      .sort((a, b) => b.totalImpact - a.totalImpact)
      .map((entry) => ({
        country: entry.country,
        aspects: entry.aspects
          .sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta))
          .slice(0, 2)
      }));
  };

  const buildImpactDetails = (analysisData) => {
    if (!analysisData?.aspect_scores) return [];

    const aspectDeltas = analysisData.aspect_deltas || {};
    const aspectReasons = analysisData.aspect_reasons || {};
    const countrySummary = [];

    Object.entries(analysisData.aspect_scores).forEach(([country, aspects]) => {
      const aspectEntries = aspectOrder.map((aspect) => {
        const delta = aspectDeltas[country]?.[aspect] ?? 0;
        const reason = aspectReasons[country]?.[aspect] || '';

        return {
          aspect,
          delta,
          score: aspects[aspect],
          reason
        };
      });

      countrySummary.push({
        country,
        aspects: aspectEntries
      });
    });

    return countrySummary
      .sort((a, b) => a.country.localeCompare(b.country));
  };

  const formatReason = (item) => {
    if (!item.reason || item.reason === 'no significant change') return '';
    let clean = item.reason.trim();
    if (clean.endsWith('.')) clean = clean.slice(0, -1);
    if (clean.length > 160) {
      clean = `${clean.slice(0, 157)}...`;
    }
    return clean;
  };

  const toggleExpanded = (messageId) => {
    setExpandedMessages((prev) => {
      const next = new Set(prev);
      if (next.has(messageId)) {
        next.delete(messageId);
      } else {
        next.add(messageId);
      }
      return next;
    });
  };

  const toggleSummary = (messageId) => {
    setExpandedSummaries((prev) => {
      const next = new Set(prev);
      if (next.has(messageId)) {
        next.delete(messageId);
      } else {
        next.add(messageId);
      }
      return next;
    });
  };

  const isLongText = (text) => (text || '').length > 280;

  const shouldHideSummaryText = (text) => {
    if (!text) return true;
    return text.startsWith('Fallback reasoning applied due to unavailable structured interpretation');
  };

  return (
    <div className="panel chatbot-panel">
      <div className="panel-header">
        <h3>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd"/>
          </svg>
          AI Chatbot
        </h3>
      </div>
      <div className="panel-content">
        <div className="chat-messages" ref={containerRef}>
          {messages.map((message, index) => {
            const lastUserIndex = [...messages].reverse().findIndex((item) => item.sender === 'user');
            const lastBotIndex = [...messages].reverse().findIndex((item) => item.sender === 'bot');
            const lastUserActualIndex = lastUserIndex !== -1 ? messages.length - 1 - lastUserIndex : -1;
            const lastBotActualIndex = lastBotIndex !== -1 ? messages.length - 1 - lastBotIndex : -1;

            const showRegenerate = message.scenario && (index === lastUserActualIndex || index === lastBotActualIndex);
            const isWelcome = message.isWelcome || (message.id === 'welcome' && message.sender === 'bot');
            const isBotResponse = message.sender === 'bot' && !isWelcome && !shouldHideSummaryText(message.text);

            return (
              <div key={message.id} className={`message ${message.sender}-message`}>
                <div className="message-content">
                  {isWelcome ? (
                    <div className="welcome-card">
                      <div className="welcome-title">Welcome to ResiliTrack AI</div>
                      <div className="welcome-subtitle">
                        Analyze how compound shocks shift resilience across 10 countries. Enter a
                        scenario to see score changes, rankings, and concise reasons.
                      </div>
                      <div className="welcome-label">Example prompts</div>
                      <ul className="welcome-list">
                        <li>"A cyberattack knocks out regional power grids during a winter storm"</li>
                        <li>"Debt markets tighten after a regional banking collapse"</li>
                        <li>"A fast-moving outbreak disrupts trade and healthcare capacity"</li>
                      </ul>
                      <div className="welcome-hint">Tip: mention region, sector, and shock type.</div>
                    </div>
                  ) : message.sender === 'user' ? (
                    <div className="message-text">{message.text}</div>
                  ) : (
                    isBotResponse && (
                      <div className={`bot-response ${expandedSummaries.has(message.id) ? 'expanded' : 'collapsed'}`}>
                        <div className="message-text-block">
                          <div className="message-text">
                            {message.text}
                          </div>
                        </div>
                        {message.analysisData?.impacts && (
                          <div className="analysis-explanations">
                            <div className="explanation-title">Aspect changes</div>
                            {buildImpactDetails(message.analysisData).map((entry) => (
                              <div className="explanation-country" key={entry.country}>
                                <div className="country-line">
                                  <span className="country-name">{entry.country}</span>
                                  <ul className="country-aspects">
                                    {entry.aspects.map((item, idx) => (
                                      <li key={idx}>
                                        <span className="aspect-name">{item.aspect}</span>
                                        <span className="aspect-score">
                                          {item.score}/100
                                        </span>
                                        <span className="aspect-text">
                                          {100 - item.score} points deducted
                                          {formatReason(item)
                                            ? ` because ${formatReason(item)}`
                                            : ''}
                                        </span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )
                  )}
                  {isBotResponse && (isLongText(message.text) || message.analysisData?.impacts) && (
                    <div className="summary-toggle-row">
                      <button
                        type="button"
                        className="summary-toggle"
                        onClick={() => toggleSummary(message.id)}
                      >
                        {expandedSummaries.has(message.id) ? 'Show less' : 'Show more'}
                      </button>
                    </div>
                  )}
                  {(message.analysisData || showRegenerate) && (
                    <div className="message-actions">
                      {message.sender === 'bot' && message.analysisData && onSelectAnalysis && (
                        <button
                          type="button"
                          className="analysis-link"
                          onClick={() => onSelectAnalysis(message.analysisData)}
                          disabled={isLoading}
                        >
                          View charts for this response
                        </button>
                      )}
                      {showRegenerate && (
                        <button
                          type="button"
                          className="icon-button regen-icon"
                          onClick={() => handleRegenerate(message.scenario, message.id, message.sender)}
                          disabled={isLoading}
                          aria-label="Regenerate response"
                          data-label="Regenerate response"
                        >
                          <svg width="14" height="14" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                            <path d="M4.707 4.707a7 7 0 019.9 0l.768-.768a1 1 0 011.707.707V8a1 1 0 01-1 1h-3.354a1 1 0 01-.707-1.707l.768-.768a5 5 0 10.87 5.87 1 1 0 111.732 1A7 7 0 114.707 4.707z"/>
                          </svg>
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
          {isLoading && (
            <div className="message bot-message">
              <div className="message-content">
                <div className="loading"></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <form onSubmit={handleSendMessage} className="chat-input-container">
          <input
            type="text"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Enter a pandemic headline..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !input.trim()}>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"/>
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}

export default Chatbot;
