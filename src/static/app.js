const statusEl = document.getElementById('status');
const tableBody = document.querySelector('#results-table tbody');
const exportJsonBtn = document.getElementById('export-json');
const exportCsvBtn = document.getElementById('export-csv');
const form = document.getElementById('screen-form');

let currentResults = window.__RESULTS__ || [];
let currentSort = { key: 'score', direction: 'desc' };

function setStatus(message) {
  if (statusEl) {
    statusEl.textContent = message;
  }
}

function normalize(value) {
  if (value === null || value === undefined) {
    return '';
  }
  return value;
}

function compareValues(a, b, direction = 'asc') {
  const order = direction === 'asc' ? 1 : -1;
  if (typeof a === 'number' && typeof b === 'number') {
    return (a - b) * order;
  }
  return String(a).localeCompare(String(b)) * order;
}

function sortResults(results) {
  const { key, direction } = currentSort;
  return [...results].sort((left, right) => {
    const leftValue = key in left ? left[key] : left.metrics?.[key];
    const rightValue = key in right ? right[key] : right.metrics?.[key];
    return compareValues(leftValue ?? '', rightValue ?? '', direction);
  });
}

function renderReasons(reasons) {
  if (!reasons?.length) {
    return '<span class="reason-badge warning">No reasons</span>';
  }
  return reasons
    .map((reason) => {
      const value = reason.value !== null && reason.value !== undefined ? ` <span class="reason-meta">value=${reason.value}</span>` : '';
      const threshold = reason.threshold !== null && reason.threshold !== undefined ? ` <span class="reason-meta">threshold=${reason.threshold}</span>` : '';
      return `
        <span class="reason-badge ${reason.level}">
          <strong>${reason.code}</strong>
          ${reason.message}
          ${value}${threshold}
        </span>
      `;
    })
    .join('');
}

function renderRows(results) {
  if (!tableBody) {
    return;
  }

  tableBody.innerHTML = results
    .map((result) => {
      const metrics = result.metrics || {};
      return `
        <tr>
          <td>
            <strong>${result.ticker}</strong><br />
            ${result.name}
          </td>
          <td>
            <span class="badge ${String(result.rating || '').toLowerCase()}">${result.rating}</span>
            <div class="score">Score ${result.score}</div>
          </td>
          <td>${result.category}</td>
          <td class="metrics">
            <div>P/E: ${normalize(metrics.pe_ratio) || 'n/a'}</div>
            <div>PEG: ${normalize(metrics.peg_ratio) || 'n/a'}</div>
            <div>Rev CAGR 5y: ${normalize(metrics.revenue_cagr_5y) || 'n/a'}%</div>
            <div>EPS Growth 5y: ${normalize(metrics.eps_growth_5y) || 'n/a'}%</div>
            <div>Debt/Equity: ${normalize(metrics.debt_to_equity) || 'n/a'}</div>
            <div>Net Debt/EBITDA: ${normalize(metrics.net_debt_to_ebitda) || 'n/a'}</div>
            <div>Interest Coverage: ${normalize(metrics.interest_coverage) || 'n/a'}x</div>
            <div>Current Ratio: ${normalize(metrics.current_ratio) || 'n/a'}</div>
          </td>
          <td>
            <details class="reason-details" open>
              <summary>Reason codes</summary>
              <div class="reason-list">${renderReasons(result.reasons)}</div>
            </details>
          </td>
        </tr>
      `;
    })
    .join('');
}

function render() {
  if (!currentResults.length) {
    setStatus('No results yet.');
  } else {
    setStatus(`Returned ${currentResults.length} results.`);
  }
  const sorted = sortResults(currentResults);
  renderRows(sorted);
}

async function runScreen(payload) {
  setStatus('Running screen...');

  const response = await fetch('/api/screen', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    setStatus('Failed to run screen.');
    return;
  }

  const data = await response.json();
  currentResults = data.results || [];
  render();
}

function exportJson() {
  const dataStr = JSON.stringify(currentResults, null, 2);
  downloadFile(dataStr, 'lynch-results.json', 'application/json');
}

function exportCsv() {
  if (!currentResults.length) {
    return;
  }
  const headers = [
    'ticker',
    'name',
    'score',
    'rating',
    'category',
    'pe_ratio',
    'peg_ratio',
    'revenue_cagr_5y',
    'eps_growth_5y',
    'debt_to_equity',
    'net_debt_to_ebitda',
    'interest_coverage',
    'current_ratio',
    'reasons',
  ];
  const rows = currentResults.map((result) => {
    const metrics = result.metrics || {};
    const reasons = (result.reasons || []).map((reason) => `${reason.code}:${reason.message}`).join(' | ');
    return [
      result.ticker,
      result.name,
      result.score,
      result.rating,
      result.category,
      metrics.pe_ratio,
      metrics.peg_ratio,
      metrics.revenue_cagr_5y,
      metrics.eps_growth_5y,
      metrics.debt_to_equity,
      metrics.net_debt_to_ebitda,
      metrics.interest_coverage,
      metrics.current_ratio,
      reasons,
    ];
  });

  const csv = [headers.join(','), ...rows.map((row) => row.map(escapeCsv).join(','))].join('\n');
  downloadFile(csv, 'lynch-results.csv', 'text/csv');
}

function escapeCsv(value) {
  if (value === null || value === undefined) {
    return '';
  }
  const str = String(value);
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

function downloadFile(content, filename, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function bindSorting() {
  document.querySelectorAll('#results-table th[data-sort]').forEach((header) => {
    header.addEventListener('click', () => {
      const key = header.getAttribute('data-sort');
      if (!key) {
        return;
      }
      currentSort = {
        key,
        direction: currentSort.key === key && currentSort.direction === 'asc' ? 'desc' : 'asc',
      };
      render();
    });
  });
}

function bindForm() {
  if (!form) {
    return;
  }
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const tickersRaw = document.getElementById('tickers').value.trim();
    const tickers = tickersRaw ? tickersRaw.split(',').map((t) => t.trim()).filter(Boolean) : [];
    const risk = document.getElementById('risk').value;
    const provider = document.getElementById('provider').value;

    runScreen({ tickers, risk_tolerance: risk, universe: provider });
  });
}

function bindExports() {
  if (exportJsonBtn) {
    exportJsonBtn.addEventListener('click', exportJson);
  }
  if (exportCsvBtn) {
    exportCsvBtn.addEventListener('click', exportCsv);
  }
}

bindSorting();
bindForm();
bindExports();
render();
