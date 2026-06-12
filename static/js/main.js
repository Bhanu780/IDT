/**
 * Smart Health Risk Prediction System
 * Frontend JavaScript — Validation, Live BMI, Stats
 */

document.addEventListener('DOMContentLoaded', () => {
  loadStats();
  setupBMIPreview();
  setupFormValidation();
});

// ── Load dashboard stats on home page ──
function loadStats() {
  const statTotal = document.getElementById('statTotal');
  const statLow   = document.getElementById('statLow');
  const statHigh  = document.getElementById('statHigh');
  if (!statTotal) return;

  fetch('/api/stats')
    .then(r => r.json())
    .then(data => {
      animateCounter(statTotal, data.total || 0);
      animateCounter(statLow, data.risk_counts?.Low || 0);
      animateCounter(statHigh, data.risk_counts?.High || 0);
    })
    .catch(() => {
      statTotal.textContent = '0';
      statLow.textContent   = '0';
      statHigh.textContent  = '0';
    });
}

// ── Animate number counter ──
function animateCounter(el, target) {
  let current = 0;
  const duration = 600;
  const step = Math.max(1, Math.floor(target / (duration / 16)));
  const timer = setInterval(() => {
    current += step;
    if (current >= target) {
      current = target;
      clearInterval(timer);
    }
    el.textContent = current;
  }, 16);
}

// ── Live BMI Preview ──
function setupBMIPreview() {
  const heightEl    = document.getElementById('height');
  const weightEl    = document.getElementById('weight');
  const previewEl   = document.getElementById('bmiPreview');
  const bmiValueEl  = document.getElementById('bmiValue');
  const bmiCatEl    = document.getElementById('bmiCategory');
  if (!heightEl || !weightEl) return;

  const update = () => {
    const h = parseFloat(heightEl.value);
    const w = parseFloat(weightEl.value);
    if (h > 0 && w > 0) {
      const bmi = (w / Math.pow(h / 100, 2)).toFixed(2);
      bmiValueEl.textContent = bmi;
      let cat, color;
      if (bmi < 18.5)      { cat = 'Underweight'; color = '#d29922'; }
      else if (bmi < 25)   { cat = 'Normal';      color = '#3fb950'; }
      else if (bmi < 30)   { cat = 'Overweight';   color = '#d29922'; }
      else                 { cat = 'Obese';        color = '#f85149'; }
      bmiCatEl.textContent      = cat;
      bmiCatEl.style.background = color + '22';
      bmiCatEl.style.color      = color;
      previewEl.style.display   = 'block';
    } else {
      previewEl.style.display = 'none';
    }
  };
  heightEl.addEventListener('input', update);
  weightEl.addEventListener('input', update);
}

// ── Form Validation + Loading ──
function setupFormValidation() {
  const form    = document.getElementById('healthForm');
  const overlay = document.getElementById('loadingOverlay');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    // Clear previous custom errors
    form.querySelectorAll('.form-control').forEach(el => el.setCustomValidity(''));

    const age   = parseInt(document.getElementById('age').value);
    const hr    = parseInt(document.getElementById('heart_rate').value);
    const sugar = parseFloat(document.getElementById('blood_sugar').value);
    const h     = parseFloat(document.getElementById('height').value);
    const w     = parseFloat(document.getElementById('weight').value);

    let valid = true;
    if (isNaN(age) || age < 1 || age > 120) {
      document.getElementById('age').setCustomValidity('Age must be 1–120.');
      valid = false;
    }
    if (isNaN(h) || h < 50 || h > 250) {
      document.getElementById('height').setCustomValidity('Height must be 50–250 cm.');
      valid = false;
    }
    if (isNaN(w) || w < 10 || w > 500) {
      document.getElementById('weight').setCustomValidity('Weight must be 10–500 kg.');
      valid = false;
    }
    if (isNaN(hr) || hr < 30 || hr > 220) {
      document.getElementById('heart_rate').setCustomValidity('Heart rate must be 30–220 bpm.');
      valid = false;
    }
    if (isNaN(sugar) || sugar < 50 || sugar > 600) {
      document.getElementById('blood_sugar').setCustomValidity('Blood sugar must be 50–600 mg/dL.');
      valid = false;
    }

    if (!form.checkValidity()) {
      e.preventDefault();
      form.reportValidity();
      return;
    }

    // Show loading overlay
    if (overlay) overlay.classList.add('active');
  });
}
