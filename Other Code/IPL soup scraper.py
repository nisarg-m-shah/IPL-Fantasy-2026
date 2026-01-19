from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

start = time.time()

URL = "https://www.iplt20.com/match/2025/1872"

# -------------------- DRIVER SETUP --------------------
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument(
    "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

wait = WebDriverWait(driver, 30)

# -------------------- OPEN PAGE --------------------
driver.get(URL)

# -------------------- CLICK SCORECARD --------------------
scorecard_tab = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-id='scoreCard']"))
)
driver.execute_script("arguments[0].click();", scorecard_tab)

# -------------------- WAIT FOR SCORECARD ROOT --------------------
wait.until(
    EC.presence_of_element_located(
        (By.CSS_SELECTOR, "div.scoreCardContentWrap")
    )
)

# -------------------- FIND INNINGS TABS (LEFT → RIGHT) --------------------
innings_tabs = wait.until(
    EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "a.ap-inner-tb-click")
    )
)

tabs = []
seen = set()
for tab in innings_tabs:
    label = tab.text.strip()
    if label and label not in seen:
        seen.add(label)
        tabs.append(tab)

tabs = tabs[:2]

print("Detected innings:", [t.text.strip() for t in tabs])

# -------------------- SCRAPE EACH INNINGS ONCE --------------------
scraped = []

for idx, tab in enumerate(tabs, start=1):
    label = tab.text.strip()

    # click only if not already active
    if "ap-active-team" not in tab.get_attribute("class"):
        driver.execute_script("arguments[0].click();", tab)

        # wait until THIS tab becomes active
        wait.until(
            lambda d: "ap-active-team" in tab.get_attribute("class")
        )

        # wait until tables exist (real data)
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.scoreCardContentWrap table")
            )
        )

    # extract ONLY the scorecard subtree
    scorecard_root = driver.find_element(
        By.CSS_SELECTOR, "div.scoreCardContentWrap"
    )
    soup = BeautifulSoup(
        scorecard_root.get_attribute("outerHTML"),
        "html.parser"
    )

    if not soup.select_one("table"):
        raise RuntimeError(f"Failed to load tables for {label}")

    filename = f"innings_{idx}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    scraped.append(label)
    print(f"Saved {filename} → {label}")

# -------------------- CLEANUP --------------------
driver.quit()
print("Done. Scraped innings:", scraped)

end = time.time()

print(end-start)