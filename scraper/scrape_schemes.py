from pathlib import Path
import json
import time
import re

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://www.tn.gov.in"
SCHEMES_URL = f"{BASE_URL}/schemes.php"

OUTPUT_FILE = Path("data/raw/schemes.json")

PAGE_TIMEOUT = 60_000
DELAY_BETWEEN_PAGES = 0.5


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(text):
    """
    Clean unnecessary whitespace.
    """

    if not text:
        return ""

    lines = []

    for line in text.splitlines():

        line = " ".join(line.split())

        if line:
            lines.append(line)

    return "\n".join(lines)


def get_absolute_url(href):
    """
    Convert relative URL into complete URL.
    """

    if not href:
        return None

    if href.startswith("http"):
        return href

    if href.startswith("/"):
        return BASE_URL + href

    return f"{BASE_URL}/{href}"


def normalize_label(text):
    """
    Normalize field labels so they can be compared reliably.
    """

    text = clean_text(text).lower()

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# EXTRACT DEPARTMENT LINKS
# ============================================================

def get_department_links(page):

    print("\nFinding department pages...")

    try:

        page.goto(
            SCHEMES_URL,
            wait_until="networkidle",
            timeout=PAGE_TIMEOUT
        )

        page.wait_for_timeout(2000)

    except PlaywrightTimeoutError:

        print("Timeout while opening schemes page.")

        return []

    department_links = []

    links = page.locator("a").all()

    for link in links:

        try:

            text = clean_text(
                link.inner_text()
            )

            href = link.get_attribute("href")

            if not text or not href:
                continue

            if "scheme_list.php" in href:

                full_url = get_absolute_url(href)

                department_links.append({
                    "department": text,
                    "url": full_url
                })

        except Exception:
            continue

    # Remove duplicates
    unique_links = {}

    for item in department_links:

        unique_links[item["url"]] = item

    department_links = list(
        unique_links.values()
    )

    print(
        f"Found {len(department_links)} department pages."
    )

    return department_links


# ============================================================
# EXTRACT SCHEME LINKS
# ============================================================

def get_scheme_links(page, department):

    print(
        f"\nOpening department: "
        f"{department['department']}"
    )

    try:

        page.goto(
            department["url"],
            wait_until="networkidle",
            timeout=PAGE_TIMEOUT
        )

        page.wait_for_timeout(1500)

    except PlaywrightTimeoutError:

        print(
            f"Timeout: {department['url']}"
        )

        return []

    scheme_links = []

    links = page.locator("a").all()

    for link in links:

        try:

            text = clean_text(
                link.inner_text()
            )

            href = link.get_attribute("href")

            if not text or not href:
                continue

            if "scheme_details.php" in href:

                full_url = get_absolute_url(href)

                scheme_links.append({
                    "scheme_name": text,
                    "url": full_url,
                    "department": department["department"]
                })

        except Exception:
            continue

    # Remove duplicates
    unique_links = {}

    for item in scheme_links:

        unique_links[item["url"]] = item

    scheme_links = list(
        unique_links.values()
    )

    print(
        f"Found {len(scheme_links)} schemes."
    )

    return scheme_links


# ============================================================
# EXTRACT FIELD FROM PAGE
# ============================================================

def extract_field(lines, possible_labels):

    """
    Search page text for a field label.

    Example:

    Funding Pattern:
    Rs.300 per farmer for 2 days.

    Returns:

    Rs.300 per farmer for 2 days.
    """

    normalized_labels = [
        normalize_label(label)
        for label in possible_labels
    ]

    for index, line in enumerate(lines):

        normalized_line = normalize_label(line)

        # ----------------------------------------------------
        # Case 1:
        # Label and value are on same line
        # ----------------------------------------------------

        for label in normalized_labels:

            if normalized_line.startswith(label):

                remaining = line[len(label):].strip()

                remaining = remaining.lstrip(":").strip()

                if remaining:
                    return remaining

        # ----------------------------------------------------
        # Case 2:
        # Label and value are separate lines
        # ----------------------------------------------------

        if normalized_line in normalized_labels:

            if index + 1 < len(lines):

                return lines[index + 1].strip()

    return ""


# ============================================================
# EXTRACT SCHEME DETAILS
# ============================================================

def extract_scheme_details(page, scheme):

    print(
        f"  Scraping: {scheme['scheme_name']}"
    )

    try:

        page.goto(
            scheme["url"],
            wait_until="networkidle",
            timeout=PAGE_TIMEOUT
        )

        page.wait_for_timeout(1000)

    except PlaywrightTimeoutError:

        print(
            f"  TIMEOUT: {scheme['url']}"
        )

        return None

    except Exception as error:

        print(
            f"  ERROR: {error}"
        )

        return None

    try:

        # ----------------------------------------------------
        # Get body text
        # ----------------------------------------------------

        body_text = page.locator(
            "body"
        ).inner_text()

        body_text = clean_text(
            body_text
        )

        if not body_text:

            print(
                "  WARNING: Empty page"
            )

            return None

        lines = body_text.splitlines()

        # ----------------------------------------------------
        # Extract important fields
        # ----------------------------------------------------

        scheme_title = extract_field(
            lines,
            [
                "Scheme Title/Name",
                "Scheme Title",
                "Scheme Name"
            ]
        )

        concerned_department = extract_field(
            lines,
            [
                "Concerned Department",
                "Department"
            ]
        )

        concerned_district = extract_field(
            lines,
            [
                "Concerned District",
                "District"
            ]
        )

        organisation_name = extract_field(
            lines,
            [
                "Organisation Name",
                "Organization Name"
            ]
        )

        associated_scheme = extract_field(
            lines,
            [
                "Associated Scheme"
            ]
        )

        sponsored_by = extract_field(
            lines,
            [
                "Sponsered By",
                "Sponsored By"
            ]
        )

        funding_pattern = extract_field(
            lines,
            [
                "Funding Pattern"
            ]
        )

        beneficiaries = extract_field(
            lines,
            [
                "Beneficiaries"
            ]
        )

        benefit_type = extract_field(
            lines,
            [
                "Types of Benefits",
                "Type of Benefits"
            ]
        )

        eligibility = extract_field(
            lines,
            [
                "Eligibility criteria",
                "Eligibility Criteria",
                "Eligibility"
            ]
        )

        income = extract_field(
            lines,
            [
                "Income"
            ]
        )

        age_from = extract_field(
            lines,
            [
                "Age From"
            ]
        )

        age_to = extract_field(
            lines,
            [
                "Age To"
            ]
        )

        community = extract_field(
            lines,
            [
                "Community"
            ]
        )

        how_to_avail = extract_field(
            lines,
            [
                "How To avail",
                "How To Avail",
                "How to avail"
            ]
        )

        validity = extract_field(
            lines,
            [
                "Validity of Scheme"
            ]
        )

        introduced_on = extract_field(
            lines,
            [
                "Introduced On"
            ]
        )

        description = extract_field(
            lines,
            [
                "Description"
            ]
        )

        scheme_type = extract_field(
            lines,
            [
                "Scheme Type"
            ]
        )

        # ----------------------------------------------------
        # Build clean searchable content
        # ----------------------------------------------------

        content_parts = [

            f"Scheme Name: "
            f"{scheme['scheme_name']}",

            f"Department: "
            f"{scheme['department']}",

            f"Concerned Department: "
            f"{concerned_department}",

            f"Concerned District: "
            f"{concerned_district}",

            f"Organisation Name: "
            f"{organisation_name}",

            f"Scheme Title: "
            f"{scheme_title}",

            f"Associated Scheme: "
            f"{associated_scheme}",

            f"Sponsored By: "
            f"{sponsored_by}",

            f"Funding Pattern: "
            f"{funding_pattern}",

            f"Beneficiaries: "
            f"{beneficiaries}",

            f"Types of Benefits: "
            f"{benefit_type}",

            f"Eligibility Criteria: "
            f"{eligibility}",

            f"Income: "
            f"{income}",

            f"Age From: "
            f"{age_from}",

            f"Age To: "
            f"{age_to}",

            f"Community: "
            f"{community}",

            f"How To Avail: "
            f"{how_to_avail}",

            f"Validity of Scheme: "
            f"{validity}",

            f"Introduced On: "
            f"{introduced_on}",

            f"Description: "
            f"{description}",

            f"Scheme Type: "
            f"{scheme_type}"
        ]

        # ----------------------------------------------------
        # Remove empty fields
        # ----------------------------------------------------

        cleaned_parts = []

        for part in content_parts:

            value = part.split(":", 1)[1].strip()

            if value:

                cleaned_parts.append(part)

        clean_content = "\n".join(
            cleaned_parts
        )

        # ----------------------------------------------------
        # Final structured record
        # ----------------------------------------------------

        data = {

            "scheme_name": scheme["scheme_name"],

            "department": scheme["department"],

            "source_url": scheme["url"],

            "page_title": page.title(),

            "funding_pattern": funding_pattern,

            "beneficiaries": beneficiaries,

            "benefit_type": benefit_type,

            "eligibility": eligibility,

            "income": income,

            "age_from": age_from,

            "age_to": age_to,

            "community": community,

            "how_to_avail": how_to_avail,

            "description": description,

            "content": clean_content
        }

        return data

    except Exception as error:

        print(
            f"  ERROR extracting content: "
            f"{error}"
        )

        return None


# ============================================================
# MAIN SCRAPER
# ============================================================

def scrape_schemes():

    print("=" * 80)

    print(
        "TAMIL NADU GOVERNMENT "
        "SCHEME SCRAPER"
    )

    print("=" * 80)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    all_schemes = []

    # --------------------------------------------------------
    # START PLAYWRIGHT
    # --------------------------------------------------------

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        # ----------------------------------------------------
        # STEP 1
        # Department pages
        # ----------------------------------------------------

        departments = get_department_links(
            page
        )

        print(
            "\n" + "=" * 80
        )

        print(
            "DEPARTMENT SUMMARY"
        )

        print(
            "=" * 80
        )

        for index, department in enumerate(
            departments,
            start=1
        ):

            print(
                f"{index}. "
                f"{department['department']} "
                f"-> "
                f"{department['url']}"
            )

        # ----------------------------------------------------
        # STEP 2
        # Scheme links
        # ----------------------------------------------------

        all_scheme_links = []

        for department in departments:

            schemes = get_scheme_links(
                page,
                department
            )

            all_scheme_links.extend(
                schemes
            )

            time.sleep(
                DELAY_BETWEEN_PAGES
            )

        # ----------------------------------------------------
        # Remove duplicate schemes
        # ----------------------------------------------------

        unique_scheme_links = {}

        for scheme in all_scheme_links:

            unique_scheme_links[
                scheme["url"]
            ] = scheme

        all_scheme_links = list(
            unique_scheme_links.values()
        )

        print(
            "\n" + "=" * 80
        )

        print(
            f"TOTAL UNIQUE SCHEMES FOUND: "
            f"{len(all_scheme_links)}"
        )

        print(
            "=" * 80
        )

        # ----------------------------------------------------
        # STEP 3
        # Scrape detail pages
        # ----------------------------------------------------

        for index, scheme in enumerate(
            all_scheme_links,
            start=1
        ):

            print(
                f"\n[{index}/"
                f"{len(all_scheme_links)}]"
            )

            scheme_data = (
                extract_scheme_details(
                    page,
                    scheme
                )
            )

            if scheme_data:

                all_schemes.append(
                    scheme_data
                )

            time.sleep(
                DELAY_BETWEEN_PAGES
            )

        browser.close()

    # --------------------------------------------------------
    # STEP 4
    # SAVE JSON
    # --------------------------------------------------------

    OUTPUT_FILE.write_text(

        json.dumps(
            all_schemes,
            ensure_ascii=False,
            indent=2
        ),

        encoding="utf-8"
    )

    # --------------------------------------------------------
    # FINAL REPORT
    # --------------------------------------------------------

    print(
        "\n" + "=" * 80
    )

    print(
        "SCRAPING COMPLETED"
    )

    print(
        "=" * 80
    )

    print(
        f"Departments found : "
        f"{len(departments)}"
    )

    print(
        f"Scheme links found: "
        f"{len(all_scheme_links)}"
    )

    print(
        f"Schemes scraped   : "
        f"{len(all_schemes)}"
    )

    print(
        f"Output file       : "
        f"{OUTPUT_FILE}"
    )

    print(
        "=" * 80
    )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    scrape_schemes()