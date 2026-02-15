import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function BarGraph({ data }) {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    console.log('BarGraph received new data:', data); // Debug log
    if (data && data.country_scores) {
      // Convert to array of [country, score] pairs and sort by score descending
      const sortedEntries = Object.entries(data.country_scores)
        .sort((a, b) => b[1] - a[1]);
      
      const labels = sortedEntries.map(entry => entry[0]);
      const scores = sortedEntries.map(entry => entry[1]);

      setChartData({
        labels: labels,
        datasets: [
          {
            label: 'Total Resilience Score',
            data: scores,
            backgroundColor: [
              '#FF6B6B',
              '#4ECDC4',
              '#45B7D1',
              '#FFA07A',
              '#98D8C8',
              '#F7DC6F',
              '#BB8FCE',
              '#85C1E2',
              '#F8B88B',
              '#52C41A'
            ],
            borderColor: [
              '#FF5252',
              '#3DBBB2',
              '#3399B8',
              '#FF8B6D',
              '#7EC9B4',
              '#F5C84D',
              '#A975BA',
              '#6AACCD',
              '#F5A76A',
              '#389E0D'
            ],
            borderWidth: 2,
            borderRadius: 5,
            hoverBackgroundColor: [
              '#FF5252',
              '#3DBBB2',
              '#3399B8',
              '#FF8B6D',
              '#7EC9B4',
              '#F5C84D',
              '#A975BA',
              '#6AACCD',
              '#F5A76A',
              '#389E0D'
            ]
          }
        ]
      });
    }
  }, [data]);

  return (
    <div className="panel graph-panel">
      <div className="panel-header">
        <h3>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"/>
          </svg>
          Resilience Leaderboard
        </h3>
      </div>
      <div className="panel-content">
        {chartData ? (
          <div className="chart-container">
            <Bar
              data={chartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                  legend: {
                    display: true,
                    position: 'top'
                  },
                  tooltip: {
                    callbacks: {
                      label: function(context) {
                        return 'Score: ' + context.parsed.x + ' points';
                      }
                    }
                  }
                },
                scales: {
                  x: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                      font: {
                        size: 12
                      }
                    }
                  },
                  y: {
                    ticks: {
                      font: {
                        size: 12
                      }
                    }
                  }
                }
              }}
            />
          </div>
        ) : (
          <p className="placeholder-text">Bar chart will appear here after analysis</p>
        )}
      </div>
    </div>
  );
}

export default BarGraph;
