import React, { useState, useRef, useEffect } from 'react';
import Chatbot from '../components/Chatbot';
import BarGraph from '../components/BarGraph';
import Heatmap from '../components/Heatmap';

function ResiliencePage({ analysisData: analysisDataProp, onAnalysisDataChange }) {
  const [analysisData, setAnalysisData] = useState(() => {
    if (analysisDataProp) return analysisDataProp;
    try {
      const saved = localStorage.getItem('resilitrack_analysis_data');
      return saved ? JSON.parse(saved) : null;
    } catch (error) {
      return null;
    }
  });
  const [graphHeight, setGraphHeight] = useState(50);
  const [chatbotWidth, setChatbotWidth] = useState(45);
  const [mobileView, setMobileView] = useState(() => (
    window.matchMedia('(max-width: 768px)').matches ? 'chat' : 'both'
  ));
  const resizerSize = 4;
  const isResizingHorizontal = useRef(false);
  const isResizingVertical = useRef(false);
  const containerRef = useRef(null);
  const graphsContainerRef = useRef(null);

  const handleHorizontalMouseDown = (e) => {
    isResizingHorizontal.current = true;
    e.preventDefault();
  };

  const handleVerticalMouseDown = (e) => {
    isResizingVertical.current = true;
    e.preventDefault();
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (isResizingHorizontal.current && graphsContainerRef.current) {
        const container = graphsContainerRef.current;
        const containerHeight = container.clientHeight;
        const usableHeight = Math.max(containerHeight - resizerSize, 1);
        const offset = e.clientY - container.getBoundingClientRect().top;
        const clampedOffset = Math.min(Math.max(offset, 0), usableHeight);
        const newHeight = (clampedOffset / usableHeight) * 100;
        if (newHeight > 30 && newHeight < 70) {
          setGraphHeight(newHeight);
        }
      }

      if (isResizingVertical.current && containerRef.current) {
        const container = containerRef.current;
        const containerWidth = container.clientWidth;
        const usableWidth = Math.max(containerWidth - resizerSize, 1);
        const offset = e.clientX - container.getBoundingClientRect().left;
        const clampedOffset = Math.min(Math.max(offset, 0), usableWidth);
        const newWidth = (clampedOffset / usableWidth) * 100;
        if (newWidth > 25 && newWidth < 70) {
          setChatbotWidth(newWidth);
        }
      }
    };

    const handleMouseUp = () => {
      isResizingHorizontal.current = false;
      isResizingVertical.current = false;
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  const handleAnalysisComplete = (data) => {
    setAnalysisData(data);
    if (onAnalysisDataChange) {
      onAnalysisDataChange(data);
    }
  };

  const handleAnalysisSelect = (data) => {
    setAnalysisData(data);
    if (onAnalysisDataChange) {
      onAnalysisDataChange(data);
    }
    if (window.matchMedia('(max-width: 768px)').matches) {
      setMobileView('charts');
    }
  };

  useEffect(() => {
    if (analysisData) {
      localStorage.setItem('resilitrack_analysis_data', JSON.stringify(analysisData));
    }
  }, [analysisData]);

  useEffect(() => {
    if (analysisDataProp !== undefined && analysisDataProp !== analysisData) {
      setAnalysisData(analysisDataProp);
    }
  }, [analysisDataProp, analysisData]);

  useEffect(() => {
    const handleClear = () => {
      setAnalysisData(null);
      if (onAnalysisDataChange) {
        onAnalysisDataChange(null);
      }
    };

    window.addEventListener('resilitrack-clear', handleClear);
    return () => {
      window.removeEventListener('resilitrack-clear', handleClear);
    };
  }, []);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(max-width: 768px)');
    const updateView = () => {
      setMobileView(mediaQuery.matches ? 'chat' : 'both');
    };

    updateView();
    mediaQuery.addEventListener('change', updateView);
    return () => mediaQuery.removeEventListener('change', updateView);
  }, []);

  const isMobile = mobileView !== 'both';

  return (
    <div className="page">
      {isMobile && (
        <div className="mobile-toggle">
          <button
            type="button"
            className={mobileView === 'chat' ? 'mobile-toggle-btn active' : 'mobile-toggle-btn'}
            onClick={() => setMobileView('chat')}
          >
            Chat
          </button>
          <button
            type="button"
            className={mobileView === 'charts' ? 'mobile-toggle-btn active' : 'mobile-toggle-btn'}
            onClick={() => setMobileView('charts')}
          >
            Charts
          </button>
        </div>
      )}
      <div 
        className="content-grid" 
        ref={containerRef}
      >
        {/* Chatbot Section */}
        <div
          className={`chatbot-panel ${isMobile && mobileView !== 'chat' ? 'mobile-hidden' : ''}`}
          style={isMobile ? { flex: '1 1 auto' } : { flex: `0 0 ${chatbotWidth}%` }}
        >
          <Chatbot
            onAnalysisComplete={handleAnalysisComplete}
            onSelectAnalysis={handleAnalysisSelect}
          />
        </div>

        {/* Vertical Resizer */}
        {!isMobile && (
          <div
            className="resizer vertical-resizer"
            onMouseDown={handleVerticalMouseDown}
            style={{ cursor: 'col-resize' }}
          />
        )}

        {/* Right Side Container */}
        <div
          className={`graphs-container ${isMobile && mobileView !== 'charts' ? 'mobile-hidden' : ''}`}
          ref={graphsContainerRef}
          style={{
            display: isMobile ? 'flex' : 'grid',
            flexDirection: isMobile ? 'column' : undefined,
            gap: isMobile ? '16px' : undefined,
            gridTemplateRows: isMobile ? undefined : `${graphHeight}% ${resizerSize}px ${100 - graphHeight}%`
          }}
        >
          {/* Bar Graph Section */}
          <div style={{ minHeight: 0, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <BarGraph data={analysisData} key={analysisData ? JSON.stringify(analysisData.country_scores) : 'empty'} />
          </div>

          {/* Horizontal Resizer */}
          {!isMobile && (
            <div 
              className="resizer horizontal-resizer"
              onMouseDown={handleHorizontalMouseDown}
              style={{ cursor: 'row-resize' }}
            />
          )}

          {/* Heatmap Section */}
          <div style={{ minHeight: 0, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <Heatmap data={analysisData} key={analysisData ? JSON.stringify(analysisData.aspect_scores) : 'empty'} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResiliencePage;
