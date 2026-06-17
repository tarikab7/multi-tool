import asyncio
from playwright.async_api import async_playwright

async def run_ui_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        print("Navigating to UI...")
        await page.goto("http://localhost:8000/static/index.html")

        print("Waiting for page to load...")
        await page.wait_for_selector(".tool-panel")

        print("Selecting Duplicate Finder tool...")
        # Since it's a dynamic sidebar, we might need to click the nav item first
        nav_item = page.locator('.nav-item[data-tool="duplicate_finder"]')
        if await nav_item.count() > 0:
            await page.evaluate('() => { document.querySelector(\'.nav-item[data-tool="duplicate_finder"]\').click(); }')
            await asyncio.sleep(1)

        print("Locating #dup-action dropdown...")
        action_dropdown = page.locator("#dup-action")
        await action_dropdown.wait_for(state="attached")

        print("Selecting 'backup_delete'...")
        await action_dropdown.select_option("backup_delete")
        await asyncio.sleep(0.5)
        await page.screenshot(path="scratch/ui_dup_action_backup_delete.png")

        print("Selecting 'restore'...")
        await action_dropdown.select_option("restore")
        await asyncio.sleep(0.5)
        await page.screenshot(path="scratch/ui_dup_action_restore.png")

        print("Test complete. Saved screenshots to scratch/")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_ui_test())