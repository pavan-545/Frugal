# Q23 Video CV — Talking Points & Cue Sheet

Use this cue sheet as a quick visual reference on camera while recording your Video CV.

---

### 1. Introduction (0:00–0:15)
- State name, B.Tech CS background, and target role (AI-Native Software Engineer Intern).
- Express enthusiasm for backend infrastructure, system design, and AI-native automation.

### 2. AI-Native Software Engineering (0:15–0:50)
- **Key Message:** AI-Native engineering $\neq$ just generating code with LLMs.
- **Workflow Pipeline:**
  $$\text{Problem} \rightarrow \text{Architecture} \rightarrow \text{AI Implementation} \rightarrow \text{Verification} \rightarrow \text{Testing} \rightarrow \text{Security} \rightarrow \text{Reliability}$$
- Highlight that human engineering judgment owns security, architecture, and correctness.

### 3. Complex Technical Project Challenge (0:50–1:30)
- **Project:** Dynamic HTML5 Canvas Automation Framework (Q1).
- **Challenge:** Dynamic coordinate drift, frame lag, and WebSocket latency where DOM locators fail.
- **Solution:** Injected JS `requestAnimationFrame` pixel detector (`getImageData()`) + 7-stage Circuit-Breaker state machine to recalculate coordinates pre-execution.
- **Result:** Sub-100ms Hover $\rightarrow$ Drag 15px $\rightarrow$ Click execution with zero static sleeps.

### 4. Responsible Generative AI Usage (1:30–2:05)
- Never blindly paste generated code without line-by-line inspection.
- Never pass `.env` secrets, credentials, or private keys into prompt context windows.
- Validate all AI outputs using automated pytest suites and schema validators.
- Maintain source control and unit tests as the ultimate authority.

### 5. Solving Technical Problems Without AI (2:05–2:40)
- **10-Step Deterministic Process:**
  $$\text{Deconstruct Requirements} \rightarrow \text{Read Specs/Logs} \rightarrow \text{Form Hypotheses} \rightarrow \text{Minimal Reproduction} \rightarrow \text{Fix & Test}$$
- Emphasize deep debugging instincts using logs, trace dumps, and source documentation.

### 6. Closing (2:40–3:00)
- Express strong interest in Frugal Testing and BuildNexTech.
- Reiterate commitment to engineering rigor, continuous learning, and system reliability.
