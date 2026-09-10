from playwright.sync_api import sync_playwright


URL = "https://www.tn.gov.in/schemes.php"


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

    page.wait_for_timeout(3000)

    links = page.locator("a")

    print(f"Total links found: {links.count()}")

    for i in range(links.count()):

        link = links.nth(i)

        text = link.inner_text().strip()

        href = link.get_attribute("href")

        if text or href:

            print(
                f"{i}: TEXT={text!r} | HREF={href!r}"
            )

    browser.close()