from playwright.async_api import Page

class AccessibilityStrategy:
    """
    Accessibility-driven targeting strategy using Chrome DevTools Protocol (CDP) accessibility tree sessions.
    Traverses the browser's OS Accessibility Tree representation to find target elements
    using semantic roles and structural ARIA attributes.
    """
    def __init__(self, page: Page):
        self.page = page

    async def get_accessibility_nodes(self) -> list:
        """Obtains full OS accessibility tree node list via Chrome DevTools Protocol (CDP) session."""
        cdp = await self.page.context.new_cdp_session(self.page)
        ax_tree = await cdp.send("Accessibility.getFullAXTree")
        return ax_tree.get("nodes", [])

    async def find_element_by_accessibility(self, target_role: str = "button", target_name: str = "Authorize Ledger Funds") -> dict:
        """
        Searches the CDP accessibility tree nodes for an element matching target role and accessible name.
        """
        nodes = await self.get_accessibility_nodes()
        
        for node in nodes:
            role_obj = node.get("role", {})
            role_val = role_obj.get("value", "") if isinstance(role_obj, dict) else str(role_obj)
            
            name_obj = node.get("name", {})
            name_val = name_obj.get("value", "") if isinstance(name_obj, dict) else str(name_obj)
            
            if role_val == target_role and target_name in name_val:
                node_id = node.get("nodeId", "unknown")
                return {
                    "found": True,
                    "role": role_val,
                    "name": name_val,
                    "accessibility_path": f"AXTree_Node({node_id}) > {role_val}({name_val})"
                }

        return {"found": False, "role": target_role, "name": target_name}
