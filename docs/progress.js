/**
 * Progress Tracker — persists to localStorage
 *
 * Data shape:
 *   { "ch1-01": "not-started", "ch1-02": "in-progress", ... }
 *
 * Status values: "not-started" | "in-progress" | "completed"
 */

const STORAGE_KEY = 'langgraph-progress';

function loadProgress() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
  } catch { return {}; }
}

function saveProgress(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

function getTopicStatus(topicId) {
  return loadProgress()[topicId] || 'not-started';
}

function setTopicStatus(topicId, status) {
  const data = loadProgress();
  data[topicId] = status;
  saveProgress(data);
}

/**
 * Calculate chapter completion percentage
 * @param {string} chapterPrefix e.g. "ch1"
 * @param {number} totalTopics total topics in this chapter
 */
function getChapterPercent(chapterPrefix, totalTopics) {
  const data = loadProgress();
  let completed = 0;
  let inProgress = 0;
  for (const [key, val] of Object.entries(data)) {
    if (key.startsWith(chapterPrefix + '-')) {
      if (val === 'completed') completed++;
      else if (val === 'in-progress') inProgress += 0.5;
    }
  }
  if (totalTopics === 0) return 0;
  return Math.round(((completed + inProgress) / totalTopics) * 100);
}

/* ---- STATUS BADGE CYCLING ---- */
const STATUS_CYCLE = ['not-started', 'in-progress', 'completed'];
const STATUS_LABELS = {
  'not-started': 'Not Started',
  'in-progress': 'In Progress',
  'completed': 'Completed'
};
const STATUS_ICONS = {
  'not-started': `<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.5" stroke-dasharray="3 3"/></svg>`,
  'in-progress': `<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.5"/><path d="M8 4v4l2.5 1.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>`,
  'completed': `<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.5"/><path d="M5.5 8l1.75 1.75L10.5 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`
};

function cycleStatus(topicId) {
  const current = getTopicStatus(topicId);
  const idx = STATUS_CYCLE.indexOf(current);
  const next = STATUS_CYCLE[(idx + 1) % STATUS_CYCLE.length];
  setTopicStatus(topicId, next);
  return next;
}

/* ---- RENDER HELPERS ---- */

function renderStatusBadge(topicId) {
  const status = getTopicStatus(topicId);
  return `<button class="status-badge status-${status}" data-topic="${topicId}" onclick="handleStatusClick(this)" title="Click to change status">
    ${STATUS_ICONS[status]}
    <span>${STATUS_LABELS[status]}</span>
  </button>`;
}

function handleStatusClick(el) {
  const topicId = el.dataset.topic;
  const next = cycleStatus(topicId);

  // Update badge
  el.className = `status-badge status-${next}`;
  el.querySelector('span').textContent = STATUS_LABELS[next];
  el.innerHTML = STATUS_ICONS[next] + `<span>${STATUS_LABELS[next]}</span>`;

  // Update row highlight
  const row = el.closest('.topic-row');
  if (row) {
    row.className = `topic-row topic-${next}`;
  }

  // Update chapter ring
  updateChapterRing();

  // Dispatch event for homepage to listen
  window.dispatchEvent(new Event('progress-updated'));
}

function updateChapterRing() {
  const ring = document.getElementById('chapterRing');
  const pctEl = document.getElementById('chapterPct');
  if (!ring || !pctEl) return;

  const prefix = ring.dataset.chapter;
  const total = parseInt(ring.dataset.total, 10);
  const pct = getChapterPercent(prefix, total);

  pctEl.textContent = pct + '%';

  // Update SVG ring
  const circle = ring.querySelector('.ring-progress');
  if (circle) {
    const circumference = 2 * Math.PI * 54;
    circle.style.strokeDashoffset = circumference - (pct / 100) * circumference;
  }
}

/* ---- HOMEPAGE: render chapter progress rings ---- */
function renderHomepageProgress() {
  document.querySelectorAll('[data-chapter-ring]').forEach(el => {
    const prefix = el.dataset.chapterRing;
    const total = parseInt(el.dataset.total, 10);
    const pct = getChapterPercent(prefix, total);
    const circumference = 2 * Math.PI * 18;
    const offset = circumference - (pct / 100) * circumference;

    el.innerHTML = `
      <div class="mini-ring" title="${pct}% complete">
        <svg width="44" height="44" viewBox="0 0 44 44">
          <circle cx="22" cy="22" r="18" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="3"/>
          <circle cx="22" cy="22" r="18" fill="none" stroke="${el.dataset.color || 'var(--accent-cyan)'}"
            stroke-width="3" stroke-linecap="round"
            stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"
            transform="rotate(-90 22 22)"
            style="transition: stroke-dashoffset 0.6s ease"/>
        </svg>
        <span class="mini-ring-pct">${pct}%</span>
      </div>
    `;
  });
}

/* ---- SHARED: scroll animations + nav ---- */
function initShared() {
  // Scroll animations
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => entry.target.classList.add('visible'), i * 60);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });
  document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));

  // Nav scroll
  window.addEventListener('scroll', () => {
    const nav = document.getElementById('nav');
    if (nav) nav.classList.toggle('scrolled', window.scrollY > 40);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initShared();
  renderHomepageProgress();
  updateChapterRing();
});
