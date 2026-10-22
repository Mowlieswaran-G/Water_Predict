/* app.js — Ward Water Quality Reporter */

// ── Sidebar toggle ──────────────────────────────────────────
const sidebar = document.getElementById('sidebar');
const toggleBtn = document.getElementById('sidebarToggle');
if (toggleBtn && sidebar) {
  toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('open');
  });
  // Close sidebar when clicking outside on mobile
  document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768 &&
        !sidebar.contains(e.target) &&
        !toggleBtn.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  });
}

// ── Live date in topbar ─────────────────────────────────────
const dateEl = document.getElementById('topbarDate');
if (dateEl) {
  function updateClock() {
    const now = new Date();
    dateEl.textContent = now.toLocaleDateString('en-IN', {
      weekday: 'short', day: 'numeric', month: 'short', year: 'numeric'
    }) + '  ' + now.toLocaleTimeString('en-IN', {
      hour: '2-digit', minute: '2-digit'
    });
  }
  updateClock();
  setInterval(updateClock, 60000);
}

// ── AJAX: Load stations when district changes ───────────────
const districtSel = document.getElementById('district');
const stationSel  = document.getElementById('station');
const stationHint = document.getElementById('stationHint');

if (districtSel && stationSel) {
  districtSel.addEventListener('change', async () => {
    const district = districtSel.value;
    if (!district) {
      stationSel.innerHTML = '<option value="">— select district first —</option>';
      return;
    }
    stationSel.innerHTML = '<option value="">⏳ Loading stations…</option>';
    stationSel.disabled = true;
    if (stationHint) stationHint.textContent = 'Fetching stations from dataset…';

    try {
      const resp = await fetch(`/stations?district=${encodeURIComponent(district)}`);
      const data = await resp.json();
      const stations = data.stations || [];

      stationSel.innerHTML = '<option value="">— select station —</option>';
      stations.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s;
        opt.textContent = s;
        stationSel.appendChild(opt);
      });
      stationSel.disabled = false;

      if (stationHint) {
        stationHint.textContent = stations.length
          ? `${stations.length} station(s) available in this district.`
          : 'No stations found for this district.';
      }
    } catch (err) {
      stationSel.innerHTML = '<option value="">⚠️ Failed to load — enter manually</option>';
      stationSel.disabled = false;
      console.error('Station load error:', err);
    }
  });
}

// ── Show/hide custom date range ─────────────────────────────
const periodSel     = document.getElementById('period');
const customDateRow = document.getElementById('customDateRow');

if (periodSel && customDateRow) {
  periodSel.addEventListener('change', () => {
    customDateRow.style.display = periodSel.value === 'Custom' ? 'grid' : 'none';
  });
}

// ── Parameter chips: All Parameters toggle ──────────────────
const chipAll     = document.getElementById('chipAll');
const paramChecks = document.querySelectorAll('.param-check');

if (chipAll) {
  chipAll.addEventListener('change', () => {
    if (chipAll.checked) {
      paramChecks.forEach(c => { c.checked = false; });
    }
  });
  paramChecks.forEach(c => {
    c.addEventListener('change', () => {
      if (c.checked) {
        chipAll.checked = false;
        chipAll.parentElement.classList.remove(':has(input:checked)');
      }
    });
  });
}

// ── Results table: row click → navigate to detail ───────────
// (handled via View buttons — no JS needed)

// ── Search form: prevent double-submit ─────────────────────
const searchForm = document.getElementById('searchForm');
const searchBtn  = document.getElementById('searchBtn');
if (searchForm && searchBtn) {
  searchForm.addEventListener('submit', () => {
    searchBtn.disabled = true;
    searchBtn.textContent = '⏳ Searching…';
  });
}

// ── Auto-dismiss flash messages after 6 s ──────────────────
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity .4s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 400);
  }, 6000);
});

// ── Animate metric cards on scroll ─────────────────────────
if ('IntersectionObserver' in window) {
  const cards = document.querySelectorAll('.metric-card, .card');
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.opacity = '1';
        e.target.style.transform = 'translateY(0)';
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });

  cards.forEach(c => {
    c.style.opacity = '0';
    c.style.transform = 'translateY(12px)';
    c.style.transition = 'opacity .35s ease, transform .35s ease';
    obs.observe(c);
  });
}
