import asyncio
import pytest
from aiqatester.browser.controller import BrowserController
from aiqatester.browser.actions import BrowserActions

@pytest.mark.asyncio
async def test_manual_quick_verification():
    """
    MANUAL TEST: Quick verification of robust selector/click logic on https://pikepass.com
    This test is for manual/temporary use and should be deleted after verification.
    """
    browser = BrowserController(headless=True)
    await browser.start()
    actions = BrowserActions(browser)
    try:
        await browser.navigate("https://amazon.com")
        # Extract interactive elements
        elements = await browser.extract_interactive_elements()
        results = {}
        # Try first button
        if elements["buttons"]:
            button = elements["buttons"][0]
            button["tag"] = "button"
            result = await browser.click_element_by_data(button)
            results["button_click"] = result
        else:
            results["button_click"] = "No button found"
        # Try first checkbox
        if elements["checkboxes"]:
            checkbox = elements["checkboxes"][0]
            checkbox["tag"] = "input"
            checkbox["type"] = "checkbox"
            result = await browser.click_element_by_data(checkbox)
            results["checkbox_click"] = result
        else:
            results["checkbox_click"] = "No checkbox found"
        # Try first dropdown
        if elements["selects"]:
            select = elements["selects"][0]
            select["tag"] = "select"
            # Try to select the first option if possible
            result = await browser.select_option(
                f"#{select['id']}" if select.get('id') else f"[name='{select['name']}']"
            )
            results["dropdown_select"] = result
        else:
            results["dropdown_select"] = "No dropdown found"
        print("Manual quick verification results:", results)
    finally:
        await browser.stop() 