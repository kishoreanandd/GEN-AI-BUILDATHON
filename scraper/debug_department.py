from playwright.sync_api import sync_playwright


BASE_URL = "https://www.tn.gov.in/"

URL = (
    BASE_URL
    + "scheme_list.php?dep_id=Mg=="
)


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
    print(page.locator("body").inner_text())

    print("\n" + "=" * 80)
    print("LINKS")
    print("=" * 80)

    links = page.locator("a")

    print(
        f"Total links found: {links.count()}"
    )

    for i in range(links.count()):

        link = links.nth(i)

        text = link.inner_text().strip()

        href = link.get_attribute("href")

        if text or href:

            print(
                f"{i}: "
                f"TEXT={text!r} | "
                f"HREF={href!r}"
            )

    browser.close()