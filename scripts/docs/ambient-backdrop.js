/**
 * Seeded static ambient illustration for the documentation portal.
 *
 * A lightweight visual homage, NOT a verified port of the original
 * Parallax Distortion app (its source was not located in the available repos).
 * Draws ONE transparent snapshot per page load. No animation loop, WebGL,
 * remote assets, telemetry, or changes to the semantic document tree.
 */

const STORAGE_KEY = 'it-lab-ambient-artwork';

export function seededRandom(initialSeed) {
  let seed = initialSeed >>> 0;
  return () => {
    seed = (seed + 0x6d2b79f5) >>> 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t ^= t + Math.imul(t ^ (t >>> 7), 61 | t);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** The same (seed, dimensions) pair always yields the same drawing commands. */
export function drawSnapshot(canvas, seed, width, height) {
  const ctx = canvas.getContext('2d');
  if (!ctx) return false;

  canvas.width = Math.max(160, Math.min(1400, Math.trunc(width)));
  canvas.height = Math.max(160, Math.min(900, Math.trunc(height)));
  const w = canvas.width, h = canvas.height;
  const rand = seededRandom(seed);
  const phase = rand() * Math.PI * 2;
  const centerX = w * (0.35 + rand() * 0.3);
  const centerY = h * (0.36 + rand() * 0.25);

  ctx.clearRect(0, 0, w, h);

  // Atmospheric points: decorative only, no letters or meaning encoded.
  for (let i = 0; i < 130; i++) {
    const x = rand() * w, y = rand() * h;
    const r = 0.25 + rand() * 1.1;
    ctx.fillStyle = `rgba(152,217,248,${(0.10 + rand() * 0.28).toFixed(3)})`;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  }

  // Offset contour families suggest depth and lens distortion, without motion.
  for (let family = 0; family < 2; family++) {
    for (let line = 0; line < 26; line++) {
      const base = (line / 25) * h;
      const alpha = (0.08 + (1 - Math.abs(line - 12.5) / 13) * 0.16).toFixed(3);
      ctx.strokeStyle = family
        ? `rgba(171,136,255,${alpha})`
        : `rgba(75,224,230,${alpha})`;
      ctx.lineWidth = line % 7 === 0 ? 1.2 : 0.65;
      ctx.beginPath();
      for (let step = 0; step <= 82; step++) {
        const x = step / 82 * w;
        const dx = (x - centerX) / w;
        const dy = (base - centerY) / h;
        const radial = Math.exp(-((dx * dx) * 8 + (dy * dy) * 15));
        const ripple = Math.sin((x / w) * 16 + phase + family * 1.8 + line * 0.21);
        const perspective = Math.sin((x / w) * 5 + line * 0.31 + phase);
        const y = base
          + ripple * radial * (family ? 48 : 70)
          + perspective * (family ? 13 : 7)
          + (family ? -1 : 1) * radial * 15;
        if (step === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();
    }
  }

  // Restrained vanishing-point rays reinforce the parallax reference.
  for (let i = -6; i <= 6; i++) {
    ctx.beginPath();
    ctx.strokeStyle = 'rgba(86,184,220,0.095)';
    ctx.lineWidth = 0.7;
    ctx.moveTo(centerX + i * 5, centerY);
    ctx.lineTo(w * (0.5 + i * 0.13), h);
    ctx.stroke();
  }
  return true;
}

function randomSeed() {
  if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
    const number = new Uint32Array(1);
    crypto.getRandomValues(number);
    return number[0];
  }
  return Math.floor(Math.random() * 4294967296) >>> 0;
}

function allowedByPreferences() {
  return ![
    '(forced-colors: active)',
    '(prefers-contrast: more)',
    '(prefers-reduced-transparency: reduce)'
  ].some(query => typeof matchMedia === 'function' && matchMedia(query).matches);
}

function savedDisabled() {
  try { return localStorage.getItem(STORAGE_KEY) === 'off'; }
  catch { return false; }
}

function setDisabled(disabled) {
  try { localStorage.setItem(STORAGE_KEY, disabled ? 'off' : 'on'); }
  catch { /* Local storage may be unavailable; session toggle still works. */ }
}

function applySnapshot() {
  if (!allowedByPreferences()) return false;
  const canvas = document.createElement('canvas');
  const width = Math.min(innerWidth || 1200, 1400);
  const height = Math.min(innerHeight || 800, 900);
  try {
    if (!drawSnapshot(canvas, randomSeed(), width, height)) return false;
    const url = canvas.toDataURL('image/png');
    if (!url.startsWith('data:image/png;base64,')) return false;
    document.body.style.setProperty('--ambient-image', `url("${url}")`);
    return true;
  } catch { return false; } // Never impair documentation.
}

function initialize() {
  if (!document.body || !allowedByPreferences()) return;
  const nav = document.querySelector('nav[aria-label="Primary"]');
  if (!nav) return;
  const toggle = document.createElement('button');
  toggle.className = 'ambient-toggle';
  toggle.type = 'button';
  toggle.setAttribute('aria-label', 'Show background artwork');
  const refresh = (disabled) => {
    toggle.setAttribute('aria-pressed', String(!disabled));
    toggle.textContent = disabled ? 'Artwork: Off' : 'Artwork: On';
    toggle.setAttribute('aria-label', disabled ? 'Show background artwork' : 'Hide background artwork');
    if (disabled) document.body.style.removeProperty('--ambient-image');
    else if (!applySnapshot()) {
      toggle.remove(); // graceful no-op on unsupported canvas
    }
  };
  const disabled = savedDisabled();
  nav.append(toggle);
  refresh(disabled);
  toggle.addEventListener('click', () => {
    const nextDisabled = toggle.getAttribute('aria-pressed') === 'true';
    setDisabled(nextDisabled);
    refresh(nextDisabled);
  });
}

// No interval, animation frame, resize redraw, or event-driven repaint.
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize, {once:true});
  else initialize();
}
