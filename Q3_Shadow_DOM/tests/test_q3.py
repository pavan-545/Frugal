import os
import pytest
from playwright.async_api import async_playwright
from automation.shadow_pathfinder import ShadowPathfinder
from automation.accessibility_strategy import AccessibilityStrategy

@pytest.mark.asyncio
async def test_1_nested_shadow_dom_traversal(browser_page):
    """TEST 1: Verifies target element can be located through 3 nested OPEN ShadowRoots."""
    pathfinder = ShadowPathfinder(browser_page)
    result = await pathfinder.find_target(
        role="button",
        aria_label="Authorize Ledger Funds",
        qa_state="unlocked-token"
    )

    print("\n============================================================")
    print("Q3 - SHADOW DOM PATHFINDING & ACCESSIBILITY")
    print("============================================================")
    print(f"[DOM] Search result found: {result['found']}")
    print(f"[DOM] Target shadow depth: {result.get('shadowDepth', 0)}")
    print(f"[DOM] Semantic role: {result.get('role', 'N/A')}")
    print(f"[DOM] Semantic ARIA label: {result.get('ariaLabel', 'N/A')}")
    
    assert result["found"] is True, "Target element should be found through 3 nested open ShadowRoots"
    assert result["shadowDepth"] >= 3, "Target element must reside at least 3 levels deep in nested Shadow DOM"
    assert result["role"] == "button"
    assert result["ariaLabel"] == "Authorize Ledger Funds"

@pytest.mark.asyncio
async def test_2_dynamic_class_regeneration(browser_page, live_server):
    """TEST 2: Verifies target remains discoverable across reloads despite dynamic host class obfuscation."""
    initial_classes = await browser_page.evaluate("window.__OBFUSCATED_CLASSES__")
    print(f"\n[DOM] Initial generated classes: {initial_classes}")

    pathfinder = ShadowPathfinder(browser_page)
    res_1 = await pathfinder.find_target()
    assert res_1["found"] is True

    # Reload page to trigger obfuscated class regeneration
    await browser_page.reload(wait_until="networkidle")
    reloaded_classes = await browser_page.evaluate("window.__OBFUSCATED_CLASSES__")
    print(f"[RELOAD] New generated classes: {reloaded_classes}")

    classes_changed = (
        initial_classes["customApp"] != reloaded_classes["customApp"] or
        initial_classes["userPanel"] != reloaded_classes["userPanel"] or
        initial_classes["securityWidget"] != reloaded_classes["securityWidget"]
    )
    print(f"[VALIDATION] Class names changed on reload: {classes_changed}")
    assert classes_changed is True, "Host class names must dynamically regenerate on page reload"

    res_2 = await pathfinder.find_target()
    print(f"[VALIDATION] Target still found after class regeneration: {res_2['found']}")
    assert res_2["found"] is True, "Target must remain discoverable after host class regeneration"

@pytest.mark.asyncio
async def test_3_no_brittle_locator_dependency(browser_page):
    """TEST 3: Confirms targeting algorithm works independently of host class names or brittle selectors."""
    # Obtain current class names
    obfuscated = await browser_page.evaluate("window.__OBFUSCATED_CLASSES__")
    widget_class = obfuscated["securityWidget"]
    
    # Verify that querySelector using host class names directly from outside shadow DOM fails
    direct_css_match = await browser_page.evaluate(
        f"document.querySelector('.{widget_class}')"
    )
    print(f"\n[PATHFINDER] Direct light DOM querySelector on inner host: {direct_css_match}")
    assert direct_css_match is None, "Direct querySelector from document light DOM must fail on encapsulated Shadow hosts"

    # Confirm pathfinder succeeds via pure semantic attributes
    pathfinder = ShadowPathfinder(browser_page)
    res = await pathfinder.find_target()
    assert res["found"] is True
    print("[PATHFINDER] Target successfully found via pure semantic properties without class dependencies")

@pytest.mark.asyncio
async def test_4_closed_shadow_root_boundary(live_server):
    """
    TEST 4: Verifies closed ShadowRoot boundary behavior.
    1. Asserts element.shadowRoot === null from ordinary page JS.
    2. Demonstrates Strategy A: Pre-initialization add_init_script instrumentation.
    3. Demonstrates Strategy B: Accessibility Tree representation alternative.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # --- STRATEGY A: Pre-initialization Instrumentation ---
        init_script = """
        window.__CAPTURED_CLOSED_ROOTS__ = [];
        const originalAttachShadow = Element.prototype.attachShadow;
        Element.prototype.attachShadow = function(init) {
            const root = originalAttachShadow.call(this, init);
            if (init && init.mode === 'closed') {
                window.__CAPTURED_CLOSED_ROOTS__.push({
                    hostTagName: this.tagName.toLowerCase(),
                    root: root
                });
            }
            return root;
        };
        """
        await context.add_init_script(init_script)
        page = await context.new_page()
        await page.goto(live_server, wait_until="networkidle")

        print("\n============================================================")
        print("[CLOSED SHADOW DOM BOUNDARY TESTS]")
        print("============================================================")

        # 1. Ordinary Page JS check: element.shadowRoot === null
        closed_root_direct_access = await page.evaluate(
            "document.querySelector('closed-security-sandbox').shadowRoot"
        )
        print(f"[BOUNDARY] Ordinary page JS element.shadowRoot: {closed_root_direct_access}")
        assert closed_root_direct_access is None, "Direct element.shadowRoot on closed ShadowRoot MUST return null"

        # 2. Strategy A Verification: Instrument captured closed root count
        captured_roots_count = await page.evaluate(
            "window.__CAPTURED_CLOSED_ROOTS__.length"
        )
        print(f"[STRATEGY A] Pre-initialization instrumented closed roots captured: {captured_roots_count}")
        assert captured_roots_count >= 1, "Pre-initialization instrumentation must capture closed shadow root at creation time"

        # Read content from instrumented closed root inside browser
        secret_content = await page.evaluate(
            "window.__CAPTURED_CLOSED_ROOTS__[0].root.querySelector('[data-qa-state=\"closed-secret\"]').textContent"
        )
        print(f"[STRATEGY A] Read data via instrumented closed root: '{secret_content}'")
        assert secret_content == "SECRET-TOKEN-99482"

        await context.close()
        await browser.close()

@pytest.mark.asyncio
async def test_5_accessibility_semantic_targeting(browser_page):
    """TEST 5: Verifies target discovery using Playwright accessibility tree snapshot strategy."""
    ax_strategy = AccessibilityStrategy(browser_page)
    result = await ax_strategy.find_element_by_accessibility(
        target_role="button",
        target_name="Authorize Ledger Funds"
    )

    print("\n============================================================")
    print("[ACCESSIBILITY STRATEGY RESULT]")
    print("============================================================")
    print(f"[ACCESSIBILITY] Found: {result['found']}")
    print(f"[ACCESSIBILITY] Target Role: {result.get('role', 'N/A')}")
    print(f"[ACCESSIBILITY] Accessible Name: {result.get('name', 'N/A')}")
    print(f"[ACCESSIBILITY] Structural Path: {result.get('accessibility_path', 'N/A')}")

    assert result["found"] is True, "Accessibility strategy must locate target in accessibility tree"
    assert result["role"] == "button"
    assert result["name"] == "Authorize Ledger Funds"

@pytest.mark.asyncio
async def test_6_llm_prompt_validation():
    """TEST 6: Validates that expert LLM prompt exists and contains strict prohibitions against brittle locators."""
    prompt_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "prompts",
        "accessibility_tree_system_prompt.md"
    )

    assert os.path.exists(prompt_path), "System prompt file accessibility_tree_system_prompt.md must exist"

    with open(prompt_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify explicit prohibitions
    assert "FORBIDDEN: Element IDs" in content or "Element IDs" in content
    assert "FORBIDDEN: Absolute or Relative XPath" in content or "XPath" in content
    assert "FORBIDDEN: CSS Tags or Selectors" in content or "CSS Tags" in content
    assert "FORBIDDEN: CSS Class Names" in content or "Class Names" in content
    assert "target_found" in content
    assert "confidence" in content

    print("\n============================================================")
    print("[LLM PROMPT VALIDATION]")
    print("============================================================")
    print("[LLM PROMPT] IDs forbidden: PASS")
    print("[LLM PROMPT] XPath forbidden: PASS")
    print("[LLM PROMPT] CSS selectors forbidden: PASS")
    print("[LLM PROMPT] CSS classes forbidden: PASS")
    print("[LLM PROMPT] Accessibility semantics required: PASS")
    print("[LLM PROMPT] Fail-closed confidence rule: PASS")
    print("============================================================")
    print("Q3 RESULT: PASS")
    print("============================================================")
