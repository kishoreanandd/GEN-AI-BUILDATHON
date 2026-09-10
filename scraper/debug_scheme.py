from playwright.sync_api import sync_playwright


URL = "https://www.tn.gov.in/scheme_details.php?id=MTU2Ng=="


with sync_playwright() as playwright:

    browser = playwright.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    page.goto(
        URL,
        wait_until="networkidle",
        timeout=60_000
    )

    page.wait_for_timeout(2000)

    print("\nPAGE TITLE:")
    print(page.title())

    print("\nPAGE TEXT:")
    print("=" * 80)

    print(
        page.locator("body").inner_text()
    )

    browser.close()