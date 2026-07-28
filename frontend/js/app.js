/**
 * Distributed Rate Limiter API Gateway - Web Dashboard Application Engine
 */

let config = {
  baseUrl: localStorage.getItem("api_base_url") || "https://distributed-rate-limiter-mbk0.onrender.com",
  adminKey: localStorage.getItem("admin_key") || "admin-secret-key-12345",
  jwtToken: localStorage.getItem("jwt_token") || "",
  apiKey: localStorage.getItem("api_key") || ""
};

let state = {
  activeClient: "demo_user",
  currentLimit: 10,
  usedRequests: 0,
  endpointChart: null,
  statusChart: null,
  simulationRunning: false
};

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
  initUI();
  setupEventListeners();
  checkGatewayHealth();
  initCharts();
  loadMetrics();
  
  // Auto Refresh Metrics Every 5 Seconds
  setInterval(() => {
    loadMetrics();
  }, 5000);
});

function initUI() {
  document.getElementById("api-base-url").value = config.baseUrl;
  document.getElementById("admin-key-input").value = config.adminKey;
}

function setupEventListeners() {
  // Navigation Tabs
  document.querySelectorAll(".nav-item button").forEach(btn => {
    btn.addEventListener("click", (e) => {
      document.querySelectorAll(".nav-item button").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".view-section").forEach(v => v.classList.remove("active"));
      
      const targetView = btn.getAttribute("data-view");
      btn.classList.add("active");
      document.getElementById(targetView).classList.add("active");
    });
  });

  // Base URL Change
  document.getElementById("api-base-url").addEventListener("change", (e) => {
    config.baseUrl = e.target.value.trim().replace(/\/$/, "");
    localStorage.setItem("api_base_url", config.baseUrl);
    showToast("API Base URL updated: " + config.baseUrl, "success");
    checkGatewayHealth();
  });

  // Admin Key Change
  document.getElementById("admin-key-input").addEventListener("change", (e) => {
    config.adminKey = e.target.value.trim();
    localStorage.setItem("admin_key", config.adminKey);
    showToast("Admin Secret Key updated", "success");
    loadMetrics();
  });

  // Auth Login Form
  document.getElementById("login-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;
    
    try {
      const res = await fetch(`${config.baseUrl}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });
      
      if (!res.ok) throw new Error("Login failed");
      const data = await res.json();
      
      config.jwtToken = data.access_token;
      localStorage.setItem("jwt_token", config.jwtToken);
      document.getElementById("auth-status-badge").textContent = "Logged In (" + username + ")";
      document.getElementById("auth-status-badge").className = "badge badge-emerald";
      showToast("Successfully authenticated via JWT Bearer Token!", "success");
    } catch (err) {
      showToast("Authentication Failed: " + err.message, "error");
    }
  });

  // Generate API Key Form
  document.getElementById("generate-key-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const clientName = document.getElementById("key-client-name").value.trim();
    
    try {
      const res = await fetch(`${config.baseUrl}/admin/api-key/${clientName}`, {
        method: "POST",
        headers: { "X-Admin-Key": config.adminKey }
      });
      
      if (!res.ok) throw new Error("Failed to generate key (Check X-Admin-Key)");
      const data = await res.json();
      
      config.apiKey = data.api_key;
      state.activeClient = clientName;
      localStorage.setItem("api_key", config.apiKey);
      
      document.getElementById("generated-key-display").value = data.api_key;
      showToast(`Generated new API Key for client '${clientName}'!`, "success");
    } catch (err) {
      showToast("Error generating API Key: " + err.message, "error");
    }
  });

  // Simulator Burst Button
  document.getElementById("run-simulator-btn")?.addEventListener("click", runRateLimitSimulator);
}

// Gateway Health Check
async function checkGatewayHealth() {
  const dot = document.getElementById("gateway-health-dot");
  const label = document.getElementById("gateway-health-label");
  
  try {
    const res = await fetch(`${config.baseUrl}/health`);
    if (res.ok) {
      dot.style.background = "#10b981";
      dot.style.boxShadow = "0 0 10px #10b981";
      label.textContent = "Gateway Online";
    } else {
      throw new Error();
    }
  } catch (err) {
    dot.style.background = "#f43f5e";
    dot.style.boxShadow = "0 0 10px #f43f5e";
    label.textContent = "Gateway Unreachable";
  }
}

// Chart.js Initialization
function initCharts() {
  const ctxEndpoint = document.getElementById("endpointChart")?.getContext("2d");
  const ctxStatus = document.getElementById("statusChart")?.getContext("2d");

  if (ctxEndpoint) {
    state.endpointChart = new Chart(ctxEndpoint, {
      type: "bar",
      data: {
        labels: [],
        datasets: [{
          label: "Hits",
          data: [],
          backgroundColor: "rgba(0, 242, 254, 0.6)",
          borderColor: "#00f2fe",
          borderWidth: 1,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: "#94a3b8" }, grid: { display: false } },
          y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } }
        }
      }
    });
  }

  if (ctxStatus) {
    state.statusChart = new Chart(ctxStatus, {
      type: "doughnut",
      data: {
        labels: ["Success (2xx)", "Rate Limited (429)", "Failed (4xx/5xx)"],
        datasets: [{
          data: [0, 0, 0],
          backgroundColor: ["#10b981", "#f43f5e", "#f59e0b"],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom", labels: { color: "#94a3b8" } } }
      }
    });
  }
}

// Load Real-time Metrics from Gateway
async function loadMetrics() {
  try {
    const res = await fetch(`${config.baseUrl}/admin/metrics`, {
      headers: { "X-Admin-Key": config.adminKey }
    });
    
    if (!res.ok) return;
    const data = await res.json();
    const summary = data.summary || {};
    
    document.getElementById("metric-total-reqs").textContent = summary.total_requests || 0;
    document.getElementById("metric-success-reqs").textContent = summary.success_requests || 0;
    document.getElementById("metric-rate-limited").textContent = summary.rate_limited_requests || 0;
    document.getElementById("metric-avg-latency").textContent = (summary.average_latency_ms || 0) + " ms";
    
    // Update Endpoint Bar Chart
    if (state.endpointChart && data.endpoints) {
      state.endpointChart.data.labels = Object.keys(data.endpoints);
      state.endpointChart.data.datasets[0].data = Object.values(data.endpoints);
      state.endpointChart.update();
    }
    
    // Update Status Doughnut Chart
    if (state.statusChart) {
      state.statusChart.data.datasets[0].data = [
        summary.success_requests || 0,
        summary.rate_limited_requests || 0,
        summary.failed_requests || 0
      ];
      state.statusChart.update();
    }
    
    // Update Redis Info Stats
    if (data.redis_statistics) {
      document.getElementById("redis-memory-val").textContent = data.redis_statistics.used_memory_human || "N/A";
      document.getElementById("redis-version-val").textContent = data.redis_statistics.redis_version || "Active";
    }
  } catch (err) {
    // Silent fail if admin key is invalid
  }
}

// Rate Limit Simulator (Fires 12 rapid requests to verify HTTP 429)
async function runRateLimitSimulator() {
  if (state.simulationRunning) return;
  state.simulationRunning = true;
  
  const btn = document.getElementById("run-simulator-btn");
  btn.disabled = true;
  btn.textContent = "Firing 12 Rapid Requests...";
  
  const logContainer = document.getElementById("simulator-log-box");
  logContainer.innerHTML = "";
  
  const headers = {};
  if (config.apiKey) headers["X-API-Key"] = config.apiKey;
  else if (config.jwtToken) headers["Authorization"] = `Bearer ${config.jwtToken}`;
  
  let successCount = 0;
  let blockedCount = 0;
  
  for (let i = 1; i <= 12; i++) {
    const startTime = performance.now();
    try {
      const res = await fetch(`${config.baseUrl}/users`, { headers });
      const duration = Math.round(performance.now() - startTime);
      const reqId = res.headers.get("X-Request-ID") || "N/A";
      
      const logLine = document.createElement("div");
      logLine.style.margin = "4px 0";
      logLine.style.fontSize = "13px";
      logLine.style.fontFamily = "monospace";
      
      if (res.status === 200) {
        successCount++;
        logLine.style.color = "#10b981";
        logLine.textContent = `[Req #${i}] HTTP 200 OK (${duration}ms) | TraceID: ${reqId.slice(0,8)}...`;
      } else if (res.status === 429) {
        blockedCount++;
        logLine.style.color = "#f43f5e";
        logLine.style.fontWeight = "bold";
        logLine.textContent = `[Req #${i}] HTTP 429 RATE LIMITED! (Retry-After: 60s) | TraceID: ${reqId.slice(0,8)}...`;
      } else {
        logLine.style.color = "#f59e0b";
        logLine.textContent = `[Req #${i}] HTTP ${res.status} (${duration}ms)`;
      }
      
      logContainer.appendChild(logLine);
      logContainer.scrollTop = logContainer.scrollHeight;
      
      // Update Rate Limiter Meter Visuals
      updateMeter(i, 10);
      
    } catch (err) {
      showToast("Simulator error: " + err.message, "error");
    }
    
    // Micro delay between requests
    await new Promise(r => setTimeout(r, 80));
  }
  
  if (blockedCount > 0) {
    showToast(`🛑 Rate Limiter Enforced! Blocked ${blockedCount} request(s) with HTTP 429!`, "error");
  } else {
    showToast(`All ${successCount} requests succeeded cleanly!`, "success");
  }
  
  btn.disabled = false;
  btn.textContent = "🚀 Run Rate Limit Burst Test (12 Reqs)";
  state.simulationRunning = false;
  loadMetrics();
}

function updateMeter(current, max) {
  const percentage = Math.min(Math.round((current / max) * 100), 100);
  const bar = document.getElementById("meter-bar-fill");
  const label = document.getElementById("meter-label");
  
  bar.style.width = percentage + "%";
  label.textContent = `${current} / ${max} Requests Window`;
  
  if (percentage >= 100) {
    bar.className = "meter-bar-inner danger";
  } else if (percentage >= 70) {
    bar.className = "meter-bar-inner warning";
  } else {
    bar.className = "meter-bar-inner";
  }
}

// Microservice Explorer Data Loader
async function loadMicroserviceData(service) {
  const tableBody = document.getElementById(`${service}-table-body`);
  if (!tableBody) return;
  
  tableBody.innerHTML = `<tr><td colspan="5" style="text-align:center; color: var(--text-muted);">Loading live ${service} microservice data...</td></tr>`;
  
  const headers = {};
  if (config.apiKey) headers["X-API-Key"] = config.apiKey;
  else if (config.jwtToken) headers["Authorization"] = `Bearer ${config.jwtToken}`;
  
  try {
    const res = await fetch(`${config.baseUrl}/${service}`, { headers });
    const reqId = res.headers.get("X-Request-ID") || "N/A";
    
    if (!res.ok) {
      if (res.status === 401) {
        tableBody.innerHTML = `<tr><td colspan="5" style="text-align:center; color: var(--accent-rose);">HTTP 401 Unauthorized. Please authenticate via JWT or API Key first.</td></tr>`;
        return;
      }
      throw new Error(`HTTP ${res.status}`);
    }
    
    const data = await res.json();
    tableBody.innerHTML = "";
    
    if (service === "users" && data.users) {
      data.users.forEach(u => {
        tableBody.innerHTML += `
          <tr>
            <td><strong>#${u.id}</strong></td>
            <td><span class="badge badge-cyan">${u.username}</span></td>
            <td>${u.email}</td>
            <td><span class="badge badge-purple">${u.role}</span></td>
            <td style="font-family: monospace; font-size:12px; color: var(--text-muted);">${reqId.slice(0,12)}...</td>
          </tr>
        `;
      });
    } else if (service === "products" && data.products) {
      data.products.forEach(p => {
        tableBody.innerHTML += `
          <tr>
            <td><strong>#${p.id}</strong></td>
            <td><strong>${p.name}</strong></td>
            <td><span class="badge badge-emerald">$${p.price}</span></td>
            <td><span class="badge badge-cyan">${p.category}</span></td>
            <td style="font-family: monospace; font-size:12px; color: var(--text-muted);">${reqId.slice(0,12)}...</td>
          </tr>
        `;
      });
    }
  } catch (err) {
    tableBody.innerHTML = `<tr><td colspan="5" style="text-align:center; color: var(--accent-rose);">Error fetching ${service}: ${err.message}</td></tr>`;
  }
}

// Toast System
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;
  
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <div style="flex:1;">
      <strong style="display:block; font-size:13px; margin-bottom:2px;">${type === 'error' ? '🛑 Alert' : '✨ Notification'}</strong>
      <span style="font-size:13px; color: var(--text-main);">${message}</span>
    </div>
  `;
  
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    setTimeout(() => toast.remove(), 300);
  }, 4500);
}
