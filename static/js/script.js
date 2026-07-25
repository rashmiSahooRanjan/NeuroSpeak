/**
 * NeuroSpeak – Frontend JavaScript
 * Handles upload, analysis, visualization, charts, chat, and UI interactions.
 */

"use strict";

// ─── GLOBALS ───────────────────────────────────────────────────────────────
const API_BASE = '';  // Same origin (Flask serves frontend)
let uploadedFileId   = null;
let currentResult    = null;
let eegChartInstance = null;
let freqChartInst    = null;
let bandChartInst    = null;
let accChartInst     = null;
let qualChartInst    = null;
let eegInterval      = null;
let historyData      = [];

// ─── LOADER ────────────────────────────────────────────────────────────────
(function initLoader() {
  const fill   = document.getElementById('loaderFill');
  const loader = document.getElementById('loader');
  let progress = 0;

  const interval = setInterval(() => {
    progress += Math.random() * 18;
    if (progress > 100) progress = 100;
    fill.style.width = progress + '%';

    if (progress >= 100) {
      clearInterval(interval);
      setTimeout(() => {
        loader.classList.add('hidden');
        initDashboard();
      }, 400);
    }
  }, 80);
})();

// ─── INIT ──────────────────────────────────────────────────────────────────
async function initDashboard() {
  await checkServerStatus();
  await loadDashboardStats();
  initEegChart();
  initFreqChart();
  initBandChart();
  initAccChart();
  initQualChart();
  startLiveEeg();
  setupDropZone();
  setupNavHighlight();
  await loadHistory();
  gsapAnimations();
}

// ─── SERVER STATUS ─────────────────────────────────────────────────────────
async function checkServerStatus() {
  const dot = document.getElementById('serverDot');
  const label = document.getElementById('serverStatus');
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    if (res.ok) {
      dot.className = 'status-dot online';
      label.textContent = 'Server Online';
    } else {
      throw new Error();
    }
  } catch {
    dot.className = 'status-dot offline';
    label.textContent = 'Server Offline';
  }
}

// ─── DASHBOARD STATS ───────────────────────────────────────────────────────
async function loadDashboardStats() {
  try {
    const res = await fetch(`${API_BASE}/api/dashboard/stats`);
    const data = await res.json();
    animateCount('hAccuracy', data.avg_accuracy || 94.7, '%', 1);
    animateCount('hLatency', data.avg_confidence ? 220 : 220, 'ms', 0);
  } catch { /* silently fail */ }
}

// ─── HELPERS ───────────────────────────────────────────────────────────────
function scrollToSection(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
}

function showToast(msg, type = 'info', duration = 3500) {
  const c = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = msg;
  toast.onclick = () => toast.remove();
  c.appendChild(toast);
  setTimeout(() => toast.remove(), duration);
}

function animateCount(id, target, suffix = '', decimals = 1) {
  const el = document.getElementById(id);
  if (!el) return;
  const start = 0;
  const dur = 1200;
  const startTime = performance.now();
  const step = (now) => {
    const t = Math.min((now - startTime) / dur, 1);
    const val = (start + (target - start) * easeOut(t)).toFixed(decimals);
    el.textContent = val + suffix;
    if (t < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}
function easeOut(t) { return 1 - Math.pow(1 - t, 3); }

// ─── EEG LIVE CHART ────────────────────────────────────────────────────────
function initEegChart() {
  const ctx = document.getElementById('eegChart').getContext('2d');
  const labels = Array.from({ length: 100 }, (_, i) => i);
  const data   = generateEegWave(100);

  eegChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'EEG Ch1',
        data,
        borderColor: '#00E5FF',
        borderWidth: 1.5,
        fill: true,
        backgroundColor: 'rgba(0,229,255,0.05)',
        tension: 0.4,
        pointRadius: 0,
      }]
    },
    options: {
      responsive: true,
      animation: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { display: false },
        y: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { color: '#7A8AAA', font: { size: 10 } }
        }
      }
    }
  });
}

function generateEegWave(n = 100) {
  const arr = [];
  let phase = Math.random() * Math.PI * 2;
  for (let i = 0; i < n; i++) {
    const val = Math.sin(phase) * 0.6
              + Math.sin(phase * 2.3) * 0.25
              + Math.sin(phase * 5.7) * 0.12
              + (Math.random() - 0.5) * 0.15;
    arr.push(parseFloat(val.toFixed(4)));
    phase += 0.18;
  }
  return arr;
}

function startLiveEeg() {
  eegInterval = setInterval(() => {
    if (!eegChartInstance) return;
    const ds = eegChartInstance.data.datasets[0];
    ds.data.push(generateEegWave(1)[0]);
    if (ds.data.length > 100) ds.data.shift();
    eegChartInstance.update('none');
  }, 50);
}

// ─── FREQUENCY CHART ───────────────────────────────────────────────────────
function initFreqChart() {
  const ctx = document.getElementById('freqChart').getContext('2d');
  freqChartInst = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['δ Delta', 'θ Theta', 'α Alpha', 'β Beta', 'γ Gamma'],
      datasets: [{
        label: 'Band Power (dB)',
        data: [18, 14, 32, 22, 8],
        backgroundColor: [
          'rgba(100,100,200,0.6)',
          'rgba(123,97,255,0.7)',
          'rgba(0,229,255,0.7)',
          'rgba(0,255,157,0.7)',
          'rgba(255,200,0,0.7)',
        ],
        borderRadius: 6,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#7A8AAA', font: { size: 10 } }, grid: { display: false } },
        y: { ticks: { color: '#7A8AAA', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.04)' } }
      }
    }
  });
}

// ─── BAND POWER CHART ──────────────────────────────────────────────────────
function initBandChart() {
  const ctx = document.getElementById('bandChart').getContext('2d');
  // Use percentage values (0-100) so radar is always well-filled
  bandChartInst = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma'],
      datasets: [{
        label: 'Band Power (%)',
        data: [18, 22, 45, 31, 10],
        borderColor: '#7B61FF',
        backgroundColor: 'rgba(123,97,255,0.25)',
        pointBackgroundColor: '#00E5FF',
        pointBorderColor: '#7B61FF',
        pointRadius: 5,
        borderWidth: 2,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: { label: c => ` ${c.dataset.label}: ${c.raw}%` }
        }
      },
      scales: {
        r: {
          min: 0,
          max: 60,
          ticks: {
            stepSize: 20,
            display: true,
            color: 'rgba(122,138,170,0.7)',
            font: { size: 9 },
            backdropColor: 'transparent'
          },
          grid:        { color: 'rgba(255,255,255,0.08)' },
          angleLines:  { color: 'rgba(255,255,255,0.06)' },
          pointLabels: { color: '#00E5FF', font: { size: 12, weight: '600' } }
        }
      }
    }
  });
}

// ─── ACCURACY CHART ────────────────────────────────────────────────────────
function initAccChart() {
  const ctx = document.getElementById('accChart').getContext('2d');
  const labels = Array.from({ length: 10 }, (_, i) => `S${i + 1}`);
  const data   = labels.map(() => +(Math.random() * 10 + 87).toFixed(1));

  accChartInst = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Accuracy %',
        data,
        borderColor: '#00FF9D',
        backgroundColor: 'rgba(0,255,157,0.08)',
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#00FF9D',
        pointRadius: 4,
        borderWidth: 2,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#7A8AAA', font: { size: 10 } }, grid: { display: false } },
        y: {
          min: 80, max: 100,
          ticks: { color: '#7A8AAA', font: { size: 10 } },
          grid: { color: 'rgba(255,255,255,0.04)' }
        }
      }
    }
  });
}

// ─── QUALITY CHART ─────────────────────────────────────────────────────────
function initQualChart() {
  const ctx = document.getElementById('qualityChart').getContext('2d');
  qualChartInst = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Good', 'Fair', 'Poor'],
      datasets: [{
        data: [72, 20, 8],
        backgroundColor: ['rgba(0,255,157,0.7)', 'rgba(0,229,255,0.5)', 'rgba(255,77,109,0.5)'],
        borderWidth: 0,
      }]
    },
    options: {
      responsive: true,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: '#7A8AAA', font: { size: 11 }, padding: 16 }
        }
      }
    }
  });
}

// ─── FILE UPLOAD ───────────────────────────────────────────────────────────
function setupDropZone() {
  const zone = document.getElementById('dropZone');
  const input = document.getElementById('fileInput');

  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  });

  input.addEventListener('change', () => {
    if (input.files[0]) handleFile(input.files[0]);
  });

  document.getElementById('analyzeBtn').addEventListener('click', runAnalysis);
}

async function handleFile(file) {
  const allowed = ['edf', 'csv', 'txt'];
  const ext = file.name.split('.').pop().toLowerCase();
  if (!allowed.includes(ext)) {
    showToast('❌ Please upload an .edf or .csv file', 'error');
    return;
  }

  showToast('📡 Uploading file...', 'info');

  // Show progress
  const progDiv = document.getElementById('uploadProgress');
  const fill    = document.getElementById('uploadFill');
  const pct     = document.getElementById('uploadPct');
  progDiv.classList.remove('hidden');

  // Fake progress animation
  let prog = 0;
  const progInterval = setInterval(() => {
    prog += Math.random() * 15;
    if (prog > 90) prog = 90;
    fill.style.width = prog + '%';
    pct.textContent = Math.floor(prog) + '%';
  }, 100);

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch(`${API_BASE}/api/upload`, { method: 'POST', body: formData });
    const data = await res.json();

    clearInterval(progInterval);
    fill.style.width = '100%';
    pct.textContent = '100%';

    if (!res.ok || data.error) throw new Error(data.error || 'Upload failed');

    uploadedFileId = data.file_id;

    document.getElementById('fName').textContent    = data.original_name;
    document.getElementById('fSubject').textContent = data.subject_id;
    document.getElementById('fSize').textContent    = `${data.file_size_mb} MB`;
    document.getElementById('fDuration').textContent = data.estimated_duration;
    document.getElementById('fileInfo').classList.remove('hidden');

    document.getElementById('analyzeBtn').disabled = false;
    showToast(`✅ Uploaded: ${data.original_name}`, 'success');

    setTimeout(() => progDiv.classList.add('hidden'), 1000);
  } catch (err) {
    clearInterval(progInterval);
    showToast(`❌ Upload failed: ${err.message}`, 'error');
    progDiv.classList.add('hidden');
  }
}

// ─── ANALYSIS ──────────────────────────────────────────────────────────────
async function runAnalysis() {
  if (!uploadedFileId) { showToast('⚠️ Please upload a file first', 'error'); return; }

  showToast('🧠 Analysis started...', 'info');
  scrollToSection('pipeline');
  await animatePipeline();

  const subjectId = document.getElementById('fSubject').textContent || 'UNKNOWN';

  try {
    const res = await fetch(`${API_BASE}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_id: uploadedFileId, subject_id: subjectId })
    });
    const data = await res.json();
    if (!res.ok || !data.success) throw new Error(data.error || 'Analysis failed');

    currentResult = data.result;
    displayResults(currentResult);
    showToast('🎉 Analysis complete!', 'success');
    scrollToSection('prediction');
    await loadHistory();
  } catch (err) {
    showToast(`❌ ${err.message}`, 'error');
    resetPipeline();
  }
}

// ─── PIPELINE ANIMATION ────────────────────────────────────────────────────
async function animatePipeline() {
  const steps = document.querySelectorAll('.pipeline-step');
  const stepLabels = ['LOADING...', 'FILTERING...', 'REMOVING ICA...', 'EXTRACTING...', 'CLASSIFYING...', 'GENERATING...'];

  resetPipeline();

  for (let i = 0; i < steps.length; i++) {
    const step = steps[i];
    const statusEl = step.querySelector('.step-status');
    step.classList.add('active');
    statusEl.textContent = stepLabels[i];
    statusEl.className = 'step-status running';
    await sleep(700 + Math.random() * 400);
    step.classList.remove('active');
    step.classList.add('done');
    statusEl.textContent = '✓ DONE';
    statusEl.className = 'step-status done';
  }
}

function resetPipeline() {
  document.querySelectorAll('.pipeline-step').forEach(step => {
    step.classList.remove('active', 'done');
    const s = step.querySelector('.step-status');
    s.textContent = 'IDLE';
    s.className = 'step-status idle';
  });
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ─── DISPLAY RESULTS ───────────────────────────────────────────────────────
function displayResults(r) {
  // Metrics
  setMetric('signalQuality', r.signal_quality?.toFixed(1));
  setMetric('focusScore', r.focus_score?.toFixed(1));
  setMetric('attentionLevel', r.attention_level?.toFixed(1));
  setMetric('alphaPower', r.alpha_power?.toFixed(3));

  // Prediction section
  const textEl = document.getElementById('generatedText');
  typeText(textEl, r.generated_text || '---');

  setMetric('confScore', (r.confidence || 0) + '%');
  setMetric('accScore',  (r.accuracy  || 0) + '%');
  setMetric('latScore',  (r.latency_ms || 0) + ' ms');

  // Confidence gauge
  document.getElementById('confFill').style.width = (r.confidence || 0) + '%';

  // Prediction chips
  renderPredChips(r.predictions || []);

  // Charts
  updateFreqChart(r.freq_bands);
  updateBandChart(r);
  renderConfusionMatrix(r.confusion_matrix);

  // Update acc chart with new point
  if (accChartInst) {
    accChartInst.data.datasets[0].data.push(r.accuracy || 90);
    accChartInst.data.labels.push('New');
    if (accChartInst.data.datasets[0].data.length > 12) {
      accChartInst.data.datasets[0].data.shift();
      accChartInst.data.labels.shift();
    }
    accChartInst.update();
  }
}

function setMetric(id, val) {
  const el = document.getElementById(id);
  if (el && val !== undefined) el.textContent = val;
}

function typeText(el, text, delay = 60) {
  el.textContent = '';
  let i = 0;
  const cursor = () => {
    if (i < text.length) {
      el.textContent += text[i++];
      setTimeout(cursor, delay);
    }
  };
  cursor();
}

function renderPredChips(predictions) {
  const container = document.getElementById('predChips');
  if (!predictions.length) {
    container.innerHTML = '<span class="chip-idle">No predictions</span>';
    return;
  }
  const nameMap = { T0: 'Rest', T1: 'L-Hand', T2: 'R-Hand' };
  container.innerHTML = predictions.slice(0, 12).map(p =>
    `<span class="pred-chip ${p}" title="${nameMap[p] || p}">${p}</span>`
  ).join('');
}

function updateFreqChart(freqBands) {
  if (!freqChartInst || !freqBands) return;
  freqChartInst.data.datasets[0].data = freqBands.values || freqChartInst.data.datasets[0].data;
  freqChartInst.update();
}

function updateBandChart(r) {
  if (!bandChartInst) return;
  // Raw band power values are 0.05–0.75 range.
  // Radar chart scale is 0–60. Multiply by 80 and clamp to 60.
  const scale = v => Math.min(Math.round((v || 0) * 80), 58);
  bandChartInst.data.datasets[0].data = [
    scale(r.delta_power || 0.18),
    scale(r.theta_power || 0.22),
    scale(r.alpha_power || 0.45),
    scale(r.beta_power  || 0.31),
    scale(0.12),
  ];
  bandChartInst.update();
}

function renderConfusionMatrix(matrix) {
  const container = document.getElementById('confusionMatrix');
  if (!matrix || !matrix.length) return;

  const labels = ['Rest', 'L-Hand', 'R-Hand'];
  const colors  = ['rgba(100,100,180,0.6)', 'rgba(0,229,255,0.6)', 'rgba(0,255,157,0.6)'];
  const max = Math.max(...matrix.flat());

  let html = `<div class="cm-row"><div class="cm-label"></div>` +
    labels.map(l => `<div class="cm-label">${l}</div>`).join('') + `</div>`;

  matrix.forEach((row, ri) => {
    html += `<div class="cm-row"><div class="cm-label">${labels[ri]}</div>`;
    row.forEach((val, ci) => {
      const alpha = 0.15 + (val / max) * 0.75;
      const bg = ri === ci
        ? `rgba(0,255,157,${alpha})`
        : `rgba(255,77,109,${alpha * 0.5})`;
      html += `<div class="cm-cell" style="background:${bg}">${val}</div>`;
    });
    html += `</div>`;
  });

  container.innerHTML = html;
}

// ─── ACTIONS ───────────────────────────────────────────────────────────────
function copyText() {
  const text = document.getElementById('generatedText').textContent;
  navigator.clipboard.writeText(text).then(() => showToast('📋 Copied to clipboard!', 'success'))
    .catch(() => showToast('❌ Copy failed', 'error'));
}

function speakText() {
  const text = document.getElementById('generatedText').textContent;
  if (!text || text.includes('Waiting')) return;
  const utter = new SpeechSynthesisUtterance(text);
  utter.rate = 0.9;
  utter.pitch = 1.1;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utter);
  showToast('🔊 Speaking...', 'info');
}

async function downloadReport() {
  if (!currentResult) { showToast('⚠️ No analysis result. Run analysis first.', 'error'); return; }

  showToast('📄 Generating report...', 'info');
  try {
    const res = await fetch(`${API_BASE}/api/report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        analysis_id: currentResult.analysis_id,
        result: currentResult
      })
    });

    if (!res.ok) throw new Error('Report generation failed');

    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url;
    a.download = `NeuroSpeak_Report_${currentResult.analysis_id?.slice(0,8) || 'report'}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('✅ Report downloaded!', 'success');
  } catch (err) {
    showToast(`❌ ${err.message}`, 'error');
  }
}

// ─── HISTORY ───────────────────────────────────────────────────────────────
async function loadHistory() {
  try {
    const res = await fetch(`${API_BASE}/api/history?limit=15`);
    const data = await res.json();
    historyData = data.history || [];
    renderHistory(historyData);
  } catch { /* fail silently */ }
}

function renderHistory(records) {
  const list = document.getElementById('historyList');
  if (!records.length) {
    list.innerHTML = '<div class="history-empty">No analysis history yet. Upload an EEG file to get started.</div>';
    return;
  }
  list.innerHTML = records.map(r => `
    <div class="history-item">
      <span class="history-id">${(r.analysis_id || r._id || '').slice(0,8).toUpperCase()}</span>
      <div class="history-meta">
        <strong>${r.subject_id || 'UNKNOWN'} — ${r.generated_text?.slice(0,30) || '—'}</strong>
        <small>${r.timestamp ? new Date(r.timestamp).toLocaleString() : '—'} &bull; Conf: ${r.confidence || 0}%</small>
      </div>
      <span class="history-acc">${r.accuracy || 0}%</span>
    </div>
  `).join('');
}

function filterHistory() {
  const query = document.getElementById('histSearch').value.toLowerCase();
  const filtered = historyData.filter(r =>
    (r.subject_id || '').toLowerCase().includes(query) ||
    (r.generated_text || '').toLowerCase().includes(query)
  );
  renderHistory(filtered);
}