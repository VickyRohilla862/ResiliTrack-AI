import React, { useState, useEffect } from 'react';

function Heatmap({ data }) {
  const [tableData, setTableData] = useState(null);
  const aspectOrder = [
    'Economic Stability',
    'Defense & Strategic Security',
    'Healthcare & Biological Readiness',
    'Cyber Resilience & Digital Infrastructure',
    'Demographic & Social Stability',
    'Energy Security',
    'Debt & Fiscal Sustainability'
  ];

  const getColorForScore = (score) => {
    // Higher score = greener, Lower score = redder
    if (score >= 80) return '#27ae60'; // Dark green
    if (score >= 60) return '#2ecc71'; // Light green
    if (score >= 40) return '#f39c12'; // Orange
    if (score >= 20) return '#e74c3c'; // Light red
    return '#c0392b'; // Dark red
  };

  useEffect(() => {
    if (data && data.aspect_scores) {
      setTableData(data.aspect_scores);
    }
  }, [data]);

  return (
    <div className="panel heatmap-panel">
      <div className="panel-header">
        <h3>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm2 3a1 1 0 000 2h10a1 1 0 100-2H5zm0 4a1 1 0 100 2h10a1 1 0 100-2H5z" clipRule="evenodd"/>
          </svg>
          Aspect Score Heatmap
        </h3>
      </div>
      <div className="panel-content">
        {tableData ? (
          <div className="heatmap-container">
            <table className="heatmap-table">
            <thead>
              <tr>
                <th>Country</th>
                <th>Economic Stability</th>
                <th>Defense &amp; Strategic Security</th>
                <th>Healthcare &amp; Biological Readiness</th>
                <th>Cyber Resilience &amp; Digital Infrastructure</th>
                <th>Demographic &amp; Social Stability</th>
                <th>Energy Security</th>
                <th>Debt &amp; Fiscal Sustainability</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(tableData).map(([country, aspects]) => (
                <tr key={country}>
                  <td style={{ fontWeight: 'bold', textAlign: 'left' }}>{country}</td>
                  {aspectOrder.map((aspect, idx) => {
                    const score = aspects[aspect];
                    return (
                      <td
                        key={idx}
                        className="score-cell"
                        style={{
                          backgroundColor: getColorForScore(score),
                          color: score >= 40 ? '#1a1a1a' : '#ffffff'
                        }}
                      >
                        {score}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        ) : (
          <p className="placeholder-text">Heatmap will appear here after analysis</p>
        )}
      </div>
    </div>
  );
}

export default Heatmap;
