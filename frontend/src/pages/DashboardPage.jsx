import React, { useMemo, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import BarGraph from '../components/BarGraph';
import Heatmap from '../components/Heatmap';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend);

const DEFAULT_ASPECTS = [
  'Economic Stability',
  'Defense & Strategic Security',
  'Healthcare & Biological Readiness',
  'Cyber Resilience & Digital Infrastructure',
  'Demographic & Social Stability',
  'Energy Security',
  'Debt & Fiscal Sustainability'
];

const ASPECT_LABELS = {
  'Economic Stability': 'Economic',
  'Defense & Strategic Security': 'Defense',
  'Healthcare & Biological Readiness': 'Healthcare',
  'Cyber Resilience & Digital Infrastructure': 'Cyber',
  'Demographic & Social Stability': 'Social',
  'Energy Security': 'Energy',
  'Debt & Fiscal Sustainability': 'Debt'
};

const PALETTE = [
  '#2563eb',
  '#16a34a',
  '#f97316',
  '#7c3aed',
  '#dc2626',
  '#0891b2',
  '#d97706',
  '#0f766e',
  '#9333ea',
  '#64748b'
];

const buildRankMap = (scores) => {
  return Object.entries(scores)
    .sort((a, b) => b[1] - a[1])
    .reduce((acc, [country], index) => {
      acc[country] = index + 1;
      return acc;
    }, {});
};

const getDeltaColor = (delta) => {
  if (delta >= 8) return '#15803d';
  if (delta >= 3) return '#16a34a';
  if (delta <= -8) return '#b91c1c';
  if (delta <= -3) return '#ef4444';
  return '#f59e0b';
};

function DashboardPage({ analysisData }) {
  const countryScores = analysisData?.country_scores || {};
  const baselineScores = analysisData?.baseline_country_scores || {};
  const aspectDeltas = analysisData?.aspect_deltas || {};
  const impactSummary = analysisData?.impact_summary || null;
  const rankChanges = analysisData?.rank_changes || [];
  const interventions = analysisData?.interventions || {};
  const baselineAspects = analysisData?.baseline_aspect_scores || {};
  const scenarioAspects = analysisData?.aspect_scores || {};

  const hasData = Object.keys(countryScores).length > 0;

  const aspectOrder = useMemo(() => {
    if (analysisData?.model_metadata?.aspect_weights) {
      return Object.keys(analysisData.model_metadata.aspect_weights);
    }
    return DEFAULT_ASPECTS;
  }, [analysisData]);

  const aspectLabels = useMemo(() => {
    return aspectOrder.map((aspect) => ASPECT_LABELS[aspect] || aspect);
  }, [aspectOrder]);

  const sortedCountries = useMemo(() => {
    if (!hasData) return [];
    return Object.entries(countryScores)
      .sort((a, b) => b[1] - a[1])
      .map(([country]) => country);
  }, [countryScores, hasData]);

  const aspectDeltaMap = useMemo(() => {
    if (Object.keys(aspectDeltas).length) return aspectDeltas;

    const computed = {};
    sortedCountries.forEach((country) => {
      computed[country] = {};
      aspectOrder.forEach((aspect) => {
        const base = baselineAspects?.[country]?.[aspect] ?? 0;
        const scen = scenarioAspects?.[country]?.[aspect] ?? 0;
        computed[country][aspect] = scen - base;
      });
    });
    return computed;
  }, [aspectDeltas, sortedCountries, aspectOrder, baselineAspects, scenarioAspects]);

  const [selectedCountry, setSelectedCountry] = useState('');

  const scoreMovementData = useMemo(() => {
    if (!hasData) return null;
    const country = selectedCountry || sortedCountries[0];
    if (!country) return null;

    const series = aspectOrder.map((aspect) => scenarioAspects?.[country]?.[aspect] ?? 0);
    const deltaTotal = aspectOrder.reduce((sum, aspect) => {
      return sum + (aspectDeltaMap?.[country]?.[aspect] ?? 0);
    }, 0);

    return {
      labels: aspectLabels,
      datasets: [
        {
          label: country,
          data: series,
          borderColor: '#2563eb',
          backgroundColor: getDeltaColor(deltaTotal),
          pointRadius: 5,
          pointHoverRadius: 7,
          pointHitRadius: 10,
          pointBackgroundColor: '#ffffff',
          pointBorderColor: '#2563eb',
          pointBorderWidth: 2,
          tension: 0
        }
      ]
    };
  }, [hasData, sortedCountries, aspectOrder, aspectLabels, aspectDeltaMap, scenarioAspects, selectedCountry]);

  const compareBarData = useMemo(() => {
    if (!hasData) return null;
    const baselineValues = sortedCountries.map((country) => baselineScores[country] ?? 0);
    const scenarioValues = sortedCountries.map((country) => countryScores[country] ?? 0);

    return {
      labels: sortedCountries,
      datasets: [
        {
          label: 'Baseline',
          data: baselineValues,
          backgroundColor: 'rgba(148, 163, 184, 0.6)',
          borderColor: 'rgba(148, 163, 184, 1)',
          borderWidth: 1
        },
        {
          label: 'Scenario',
          data: scenarioValues,
          backgroundColor: 'rgba(37, 99, 235, 0.7)',
          borderColor: 'rgba(37, 99, 235, 1)',
          borderWidth: 1
        }
      ]
    };
  }, [hasData, sortedCountries, baselineScores, countryScores]);

  const topRisers = impactSummary?.top_risers?.map((entry) => entry.country).join(', ') || 'N/A';
  const topFallers = impactSummary?.top_fallers?.map((entry) => entry.country).join(', ') || 'N/A';
  const topAspects = impactSummary?.top_aspects?.map((entry) => entry.aspect).join(', ') || 'N/A';

  return (
    <div className="page dashboard-page">
      <div className="header">
        <h1>Dashboard</h1>
        <p>Stress-test overview with ranking shifts, aspect deltas, and impact drivers</p>
      </div>

      <div className="dashboard-grid">
        <div className="panel dashboard-section">
          <div className="panel-header">
            <h3>Impact Summary</h3>
          </div>
          <div className="panel-content">
            {hasData ? (
              <div className="kpi-grid">
                <div className="kpi-card">
                  <div className="kpi-label">Top risers</div>
                  <div className="kpi-value">{topRisers}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">Top fallers</div>
                  <div className="kpi-value">{topFallers}</div>
                </div>
                <div className="kpi-card">
                  <div className="kpi-label">Most affected aspects</div>
                  <div className="kpi-value">{topAspects}</div>
                </div>
              </div>
            ) : (
              <p className="placeholder-text">Run a scenario to populate the dashboard.</p>
            )}
          </div>
        </div>

        <div className="panel dashboard-section">
          <div className="panel-header">
            <h3>Aspect Scores by Country</h3>
          </div>
          <div className="panel-content">
            {hasData && (
              <div className="chart-filter">
                <label htmlFor="countrySelect">Country</label>
                <select
                  id="countrySelect"
                  value={selectedCountry || sortedCountries[0] || ''}
                  onChange={(event) => setSelectedCountry(event.target.value)}
                >
                  {sortedCountries.map((country) => (
                    <option key={country} value={country}>
                      {country}
                    </option>
                  ))}
                </select>
              </div>
            )}
            {scoreMovementData ? (
              <div className="dashboard-resize">
                <div className="chart-container">
                  <Line
                    data={scoreMovementData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      interaction: {
                        mode: 'nearest',
                        intersect: false
                      },
                      plugins: {
                        legend: { display: false },
                        tooltip: {
                          callbacks: {
                            title: (items) => {
                              const index = items?.[0]?.dataIndex ?? 0;
                              return aspectOrder[index] || '';
                            },
                            label: (context) => {
                              const label = context.dataset.label;
                              const value = context.parsed.y;
                              const aspect = aspectOrder[context.dataIndex];
                              const delta = aspectDeltaMap?.[label]?.[aspect] ?? 0;
                              const sign = value > 0 ? '+' : '';
                              const deltaSign = delta > 0 ? '+' : '';
                              return `${label}: ${sign}${value} (delta ${deltaSign}${delta})`;
                            }
                          }
                        }
                      },
                      scales: {
                        x: {
                          ticks: {
                            color: '#cbd5f5',
                            font: { size: 11 }
                          },
                          grid: {
                            color: 'rgba(148, 163, 184, 0.2)'
                          }
                        },
                        y: {
                          beginAtZero: false,
                          min: 0,
                          max: 100,
                          ticks: {
                            color: '#cbd5f5',
                            font: { size: 11 }
                          },
                          grid: {
                            color: 'rgba(148, 163, 184, 0.2)'
                          }
                        }
                      }
                    }}
                  />
                </div>
              </div>
            ) : (
              <p className="placeholder-text">Aspect deltas will appear after analysis.</p>
            )}
          </div>
        </div>

        <div className="panel dashboard-section dashboard-span interventions-panel">
          <div className="panel-header">
            <h3>Baseline vs Scenario Scores</h3>
          </div>
          <div className="panel-content">
            {compareBarData ? (
              <div
                className="dashboard-resize"
                style={{ height: '520px', minHeight: '480px' }}
              >
                <div className="chart-container">
                  <Bar
                    data={compareBarData}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      indexAxis: 'y',
                      scales: {
                        x: { beginAtZero: true, max: 100 }
                      },
                      plugins: {
                        legend: { position: 'top' }
                      }
                    }}
                  />
                </div>
              </div>
            ) : (
              <p className="placeholder-text">Score comparison will appear after analysis.</p>
            )}
          </div>
        </div>

        <div className="panel dashboard-section dashboard-span leaderboard-panel">
          <div className="panel-header">
            <h3>Recommended Interventions</h3>
          </div>
          <div className="panel-content">
            {hasData ? (
              <div className="intervention-list">
                {sortedCountries.map((country) => (
                  <div key={country} className="intervention-item">
                    <div className="intervention-country">{country}</div>
                    <ul>
                      {(interventions[country] || ['monitor conditions and prepare contingencies']).map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            ) : (
              <p className="placeholder-text">Interventions will appear after analysis.</p>
            )}
          </div>
        </div>

        <div className="panel dashboard-section dashboard-span aspect-heatmap-panel">
          <div className="panel-header">
            <h3>Aspect Delta Heatmap</h3>
          </div>
          <div className="panel-content">
            {hasData ? (
              <div className="delta-scroll">
                <table className="delta-table">
                  <thead>
                    <tr>
                      <th>Country</th>
                      {aspectOrder.map((aspect) => (
                        <th key={aspect}>{aspect}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {sortedCountries.map((country) => (
                      <tr key={country}>
                        <td className="delta-country">{country}</td>
                        {aspectOrder.map((aspect) => {
                          const delta = aspectDeltas?.[country]?.[aspect] ?? 0;
                          return (
                            <td
                              key={aspect}
                              className="delta-cell"
                              style={{ backgroundColor: getDeltaColor(delta) }}
                            >
                              {delta > 0 ? `+${delta}` : delta}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="placeholder-text">Aspect deltas will appear after analysis.</p>
            )}
          </div>
        </div>

        <div className="dashboard-span dashboard-block">
          <div
            className="dashboard-resize"
            style={{ height: '520px', minHeight: '480px' }}
          >
            <BarGraph data={analysisData} />
          </div>
        </div>

        <div className="dashboard-span dashboard-block">
          <div
            className="dashboard-resize"
            style={{ height: '520px', minHeight: '480px' }}
          >
            <Heatmap data={analysisData} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;
