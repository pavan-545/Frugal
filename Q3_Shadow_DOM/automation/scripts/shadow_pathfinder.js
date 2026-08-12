/**
 * Recursive Shadow DOM Pathfinder
 * Traverses open ShadowRoots to any depth to locate a target element using stable semantic properties.
 * 
 * Rules:
 * - NO element IDs
 * - NO absolute XPath
 * - NO CSS host classes/tags
 * - NO plain text matching
 * - Traverses OPEN shadow roots recursively
 */

(function () {
  window.findTargetInShadowDOM = function (targetSemantics) {
    const semantics = targetSemantics || {
      role: 'button',
      ariaLabel: 'Authorize Ledger Funds',
      qaState: 'unlocked-token'
    };

    let foundTarget = null;
    let maxDepthReached = 0;

    function searchRecursive(node, currentDepth) {
      if (!node) return false;

      if (currentDepth > maxDepthReached) {
        maxDepthReached = currentDepth;
      }

      // Check if current node matches target semantic criteria
      if (node.nodeType === 1) { // Node.ELEMENT_NODE
        const role = node.getAttribute('role');
        const ariaLabel = node.getAttribute('aria-label');
        const qaState = node.getAttribute('data-qa-state');

        const matchesRole = !semantics.role || role === semantics.role;
        const matchesAria = !semantics.ariaLabel || ariaLabel === semantics.ariaLabel;
        const matchesQaState = !semantics.qaState || qaState === semantics.qaState;

        if (matchesRole && matchesAria && matchesQaState) {
          foundTarget = {
            element: node,
            role: role,
            ariaLabel: ariaLabel,
            qaState: qaState,
            tagName: node.tagName.toLowerCase(),
            shadowDepth: currentDepth
          };
          return true; // Target found
        }
      }

      // 1. If node hosts an OPEN shadowRoot, traverse into shadowRoot first
      if (node.shadowRoot) {
        if (searchRecursive(node.shadowRoot, currentDepth + 1)) {
          return true;
        }
      }

      // 2. Traverse element children
      const children = Array.from(node.children || node.childNodes || []).filter(n => n.nodeType === 1);
      for (const child of children) {
        if (searchRecursive(child, currentDepth)) {
          return true;
        }
      }

      return false;
    }

    const startRoot = document.body || document.documentElement;
    const success = searchRecursive(startRoot, 0);

    if (success && foundTarget) {
      return {
        found: true,
        role: foundTarget.role,
        ariaLabel: foundTarget.ariaLabel,
        qaState: foundTarget.qaState,
        tagName: foundTarget.tagName,
        shadowDepth: foundTarget.shadowDepth,
        maxDepthReached: maxDepthReached
      };
    }

    return {
      found: false,
      shadowDepth: 0,
      maxDepthReached: maxDepthReached
    };
  };
})();
