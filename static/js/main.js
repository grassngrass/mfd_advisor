function formatCurrency(v) {
  v = parseFloat(v) || 0;
  if (v >= 10000000) return "₹" + (v / 10000000).toFixed(2) + "Cr";
  if (v >= 100000)   return "₹" + (v / 100000).toFixed(2)   + "L";
  if (v >= 1000)     return "₹" + (v / 1000).toFixed(1)     + "K";
  return "₹" + v.toFixed(0);
}

function formatNum(v) {
  v = parseFloat(v) || 0;
  if (v >= 10000000) return (v / 10000000).toFixed(2) + "Cr";
  if (v >= 100000)   return (v / 100000).toFixed(2)   + "L";
  if (v >= 1000)     return (v / 1000).toFixed(1)     + "K";
  return v.toFixed(0);
}

async function apiFetch(url, opts = {}) {
  const defaults = { headers: { "Content-Type": "application/json" } };
  const options  = { ...defaults, ...opts };
  if (opts.headers) options.headers = { ...defaults.headers, ...opts.headers };
  try {
    const res = await fetch(url, options);
    return await res.json();
  } catch (e) {
    console.error("API error:", e);
    showToast("Network error", "error");
    return {};
  }
}

function openModal(id) {
  document.getElementById(id).classList.add("open");
  document.getElementById("modalBackdrop").classList.add("open");
  document.body.style.overflow = "hidden";
}

function closeModal() {
  document.querySelectorAll(".modal.open").forEach(m => m.classList.remove("open"));
  document.getElementById("modalBackdrop").classList.remove("open");
  document.body.style.overflow = "";
}

document.addEventListener("keydown", e => { if (e.key === "Escape") closeModal(); });

function showToast(msg, type = "info") {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("open");
}

function updateDate() {
  const el = document.getElementById("topbarDate");
  if (!el) return;
  const now = new Date();
  el.textContent = now.toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "short", year: "numeric" });
}
updateDate();

if (typeof Chart !== "undefined") {
  Chart.defaults.font.family = "DM Sans";
  Chart.defaults.plugins.tooltip.backgroundColor = "#0f172a";
  Chart.defaults.plugins.tooltip.padding = 10;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
  Chart.defaults.plugins.tooltip.titleFont = { family: "DM Sans", weight: "600" };
  Chart.defaults.plugins.tooltip.bodyFont  = { family: "DM Mono" };
}