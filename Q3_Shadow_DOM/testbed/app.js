// Helper function to generate obfuscated class strings on every page load
function getRandomClass(prefix) {
  return `${prefix}_${Math.random().toString(36).substring(2, 9)}`;
}

// Global registry of generated host class names for testing/verification
window.__OBFUSCATED_CLASSES__ = {
  customApp: getRandomClass('obfuscated_host_app'),
  userPanel: getRandomClass('obfuscated_host_panel'),
  securityWidget: getRandomClass('obfuscated_host_widget'),
  closedSandbox: getRandomClass('obfuscated_host_closed')
};

// 1. Level 3 Inner Security Widget Custom Element
class SecurityWidget extends HTMLElement {
  constructor() {
    super();
    this._shadow = this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.className = window.__OBFUSCATED_CLASSES__.securityWidget;
    this._shadow.innerHTML = `
      <style>
        :host { display: block; padding: 10px; border: 1px dashed #38bdf8; margin-top: 5px; }
      </style>
      <div class="widget-inner shadow-host-box">
        <h4>Level 3: Security Widget (Open ShadowRoot)</h4>
        <button role="button" aria-label="Authorize Ledger Funds" data-qa-state="unlocked-token">
          Authorize Ledger Funds
        </button>
      </div>
    `;
  }
}
customElements.define('security-widget', SecurityWidget);

// 2. Level 2 User Panel Custom Element
class UserPanel extends HTMLElement {
  constructor() {
    super();
    this._shadow = this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.className = window.__OBFUSCATED_CLASSES__.userPanel;
    this._shadow.innerHTML = `
      <style>
        :host { display: block; padding: 10px; border: 1px dashed #818cf8; margin-top: 5px; }
      </style>
      <div class="panel-inner shadow-host-box">
        <h3>Level 2: User Panel (Open ShadowRoot)</h3>
        <security-widget></security-widget>
      </div>
    `;
  }
}
customElements.define('user-panel', UserPanel);

// 3. Level 1 Custom App Custom Element
class CustomApp extends HTMLElement {
  constructor() {
    super();
    this._shadow = this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.className = window.__OBFUSCATED_CLASSES__.customApp;
    this._shadow.innerHTML = `
      <style>
        :host { display: block; padding: 10px; border: 1px dashed #34d399; margin-top: 5px; }
      </style>
      <div class="app-inner shadow-host-box">
        <h2>Level 1: Custom App (Open ShadowRoot)</h2>
        <user-panel></user-panel>
      </div>
    `;
  }
}
customElements.define('custom-app', CustomApp);

// 4. Closed Shadow DOM Boundary Component
class ClosedSecuritySandbox extends HTMLElement {
  constructor() {
    super();
    this._shadow = this.attachShadow({ mode: 'closed' });
  }

  connectedCallback() {
    this.className = window.__OBFUSCATED_CLASSES__.closedSandbox;
    this._shadow.innerHTML = `
      <style>
        :host { display: block; padding: 10px; border: 1px solid #f43f5e; margin-top: 15px; }
      </style>
      <div class="closed-inner shadow-host-box" role="region" aria-label="Closed Vault Region">
        <h3 style="color: #f43f5e;">Closed Boundary Sandbox (Closed ShadowRoot)</h3>
        <p>Private Vault Token: <span data-qa-state="closed-secret">SECRET-TOKEN-99482</span></p>
        <button role="button" aria-label="Closed Vault Action">Closed Action</button>
      </div>
    `;
  }
}
customElements.define('closed-security-sandbox', ClosedSecuritySandbox);

// Render application components into DOM container
function initApp() {
  const openContainer = document.getElementById('open-tree-container');
  const closedContainer = document.getElementById('closed-tree-container');

  if (openContainer && !openContainer.hasChildNodes()) {
    const appElem = document.createElement('custom-app');
    openContainer.appendChild(appElem);
  }

  if (closedContainer && !closedContainer.hasChildNodes()) {
    const closedElem = document.createElement('closed-security-sandbox');
    closedContainer.appendChild(closedElem);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}
