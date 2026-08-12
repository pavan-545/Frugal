# Q3 — Sealed Closed-Boundary Shadow DOM Pathfinding & Accessibility Tree Refactoring

## 1. Q3 Objective

This project implements a complete, self-contained local testbed and automation framework for **Question 3** of the Frugal Testing / BuildNexTech AI-Native Software Engineer Intern Assessment. 

The primary objective is to reliably locate elements inside deeply nested Shadow DOM structures without relying on brittle locators (such as element IDs, absolute XPaths, CSS tags, or obfuscated host classes), while addressing the technical boundaries of genuinely closed ShadowRoots.

---

## 2. Requirement-to-Code Mapping Matrix

| Q3 Acceptance Requirement | Implementation Component | Test Case Verification |
| :--- | :--- | :--- |
| **Deep Nested Shadow DOM (3+ levels)** | `testbed/app.js` (`<custom-app>` $\rightarrow$ `<user-panel>` $\rightarrow$ `<security-widget>`) | `tests/test_q3.py::test_1_nested_shadow_dom_traversal` |
| **Dynamic Obfuscated Host Classes** | `testbed/app.js` (`getRandomClass()`) | `tests/test_q3.py::test_2_dynamic_class_regeneration` |
| **Resilient Semantic Pathfinder** | `automation/scripts/shadow_pathfinder.js` & `automation/shadow_pathfinder.py` | `tests/test_q3.py::test_3_no_brittle_locator_dependency` |
| **Closed ShadowRoot Boundary** | `testbed/app.js` (`<closed-security-sandbox>`) & Strategy A (`add_init_script`) | `tests/test_q3.py::test_4_closed_shadow_root_boundary` |
| **Accessibility Tree Strategy** | `automation/accessibility_strategy.py` (`page.accessibility.snapshot()`) | `tests/test_q3.py::test_5_accessibility_semantic_targeting` |
| **Expert LLM System Prompt** | `prompts/accessibility_tree_system_prompt.md` | `tests/test_q3.py::test_6_llm_prompt_validation` |

---

## 3. Nested Shadow DOM Architecture & Dynamic Class Generation

The testbed application (`testbed/app.js`) builds a 3-level nested Web Component hierarchy:

```text
document (Light DOM)
  └── <custom-app class="obfuscated_host_app_x89a">
        └── #shadow-root (open) [Level 1]
              └── <user-panel class="obfuscated_host_panel_k91z">
                    └── #shadow-root (open) [Level 2]
                          └── <security-widget class="obfuscated_host_widget_m4p8">
                                └── #shadow-root (open) [Level 3]
                                      └── <button role="button" aria-label="Authorize Ledger Funds" data-qa-state="unlocked-token">
```

### Why Traditional Selectors Fail
Modern web applications frequently employ CSS module obfuscation, shadow DOM encapsulation, and dynamic class regeneration. On every page reload, host class names regenerate (e.g., `obfuscated_host_app_x89a` becomes `obfuscated_host_app_z721`). Traditional CSS selectors and absolute XPaths break instantly upon page reloads.

---

## 4. Recursive Shadow DOM Pathfinder

The JavaScript pathfinder (`automation/scripts/shadow_pathfinder.js`) implements a recursive algorithm that traverses open `shadowRoot` trees to arbitrary depths:

```javascript
function searchRecursive(node, currentDepth) {
  if (isTargetSemanticMatch(node)) return node;
  
  for (const child of node.children) {
    if (child.shadowRoot) {
      const match = searchRecursive(child.shadowRoot, currentDepth + 1);
      if (match) return match;
    }
    const match = searchRecursive(child, currentDepth);
    if (match) return match;
  }
}
```

The algorithm evaluates target nodes using stable semantic attributes (`role`, `aria-label`, `data-qa-state`) without hardcoding CSS host class strings or fixed nesting hierarchies.

---

## 5. Closed ShadowRoot Technical Boundaries

A genuinely closed Shadow DOM is attached via `element.attachShadow({ mode: 'closed' })`. From ordinary page JavaScript, accessing `element.shadowRoot` evaluates strictly to `null`.

### Valid Technical Mitigation Strategies

1. **Strategy A: Pre-Initialization Instrumentation (`page.add_init_script`)**  
   If the test runner controls page initialization, it can instrument `Element.prototype.attachShadow` before application scripts run, capturing references to closed shadow roots at creation time:
   ```javascript
   const originalAttachShadow = Element.prototype.attachShadow;
   Element.prototype.attachShadow = function(init) {
     const root = originalAttachShadow.call(this, init);
     if (init && init.mode === 'closed') {
       window.__CAPTURED_CLOSED_ROOTS__.push({ host: this, root: root });
     }
     return root;
   };
   ```

2. **Strategy B: Browser Accessibility Tree Abstraction**  
   When direct DOM inspection is blocked by closed encapsulation, automation tools leverage the browser's OS Accessibility Tree abstraction, which exposes interactive controls based on their ARIA roles and accessible names rather than internal DOM nodes.

---

## 6. Expert LLM System Prompt Architecture

The system prompt (`prompts/accessibility_tree_system_prompt.md`) trains Large Language Models (LLMs) to reason about user interfaces strictly through Accessibility Tree representations.

### Core Rules & Constraints:
- **Prohibitions:** Strictly forbids using element IDs, absolute XPaths, CSS tags, or CSS class names.
- **Allowed Primitives:** Reasons exclusively using ARIA roles, accessible names, control states (`expanded`, `disabled`), and parent-child structural hierarchy.
- **Structured JSON Output:** Requires responses conforming to a strict JSON schema containing `target_found`, `role`, `accessible_name`, `confidence`, and `evidence`.
- **Fail-Closed Threshold:** If matching confidence is below `0.85`, the prompt mandates returning `target_found: false`.

---

## 7. Installation & Test Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Execute Automated Test Suite
```bash
pytest -s -v tests/test_q3.py
```
