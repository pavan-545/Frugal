import os
from playwright.async_api import Page

class ShadowPathfinder:
    """
    Python wrapper executing the recursive Shadow DOM pathfinder script in Playwright.
    """
    def __init__(self, page: Page):
        self.page = page
        self.script_path = os.path.join(
            os.path.dirname(__file__), "scripts", "shadow_pathfinder.js"
        )

    async def inject_script(self):
        """Injects shadow_pathfinder.js into the browser runtime."""
        with open(self.script_path, "r", encoding="utf-8") as f:
            script_content = f.read()
        await self.page.evaluate(script_content)

    async def find_target(self, role: str = "button", aria_label: str = "Authorize Ledger Funds", qa_state: str = "unlocked-token") -> dict:
        """
        Executes recursive Shadow DOM search targeting element with stable semantic properties.
        """
        await self.inject_script()
        target_semantics = {
            "role": role,
            "ariaLabel": aria_label,
            "qaState": qa_state
        }
        result = await self.page.evaluate(
            "semantics => window.findTargetInShadowDOM(semantics)",
            target_semantics
        )
        return result
