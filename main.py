import time
from urllib.parse import urljoin
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

base_url = "https://hockey.instatscout.com"
driver = webdriver.Chrome()

driver.get("https://hockey.instatscout.com")
driver.maximize_window()
time.sleep(2)

username_input = driver.find_element(By.ID, "username")

username_input.click()
username_input.send_keys("tom@mk-lightning.co.uk")

time.sleep(2)

send_button = driver.find_element(By.CSS_SELECTOR,
                                  "body > code > div > main > section > div > div > div > div.cb3221fbd.c36ab57df > div > form > div.c4d5413ce > button")
send_button.click()
time.sleep(2)

password_input = driver.find_element(By.ID, "password")
password_input.click()
password_input.send_keys("MKLInstat2024!")

submit_button = driver.find_element(By.CSS_SELECTOR,
                                    "body > code > div > main > section > div > div > div > form > div.c4d5413ce > button")
submit_button.click()
time.sleep(5)
driver.get("https://hockey.instatscout.com/tournaments/5150")

# Wait until at least one game element is present
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".MatchRow-sc-ibjx1d-0.iEmfdu"))
)

# Create output folder if it doesn't exist
output_folder = "games_html"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Get game URLs by locating the div elements and their <a> tags
game_elements = driver.find_elements(By.CSS_SELECTOR, "div.MatchRow-sc-ibjx1d-0.iEmfdu a[href]")
game_urls = []

for element in game_elements:
    href = element.get_attribute("href")
    if href:
        # Ensure the URL is absolute
        full_url = urljoin(base_url, href)
        if full_url not in game_urls:  # avoid duplicates if any
            game_urls.append(full_url)

print("Found game URLs:")
for url in game_urls:
    print(url)

# Set up WebDriverWait to wait for the element before saving
wait = WebDriverWait(driver, 20)  # waits up to 20 seconds

# Loop through each game URL, visit the page, wait for the target element, then save the HTML
for idx, game_url in enumerate(game_urls, start=1):
    print(f"Visiting game URL: {game_url}")
    driver.get(game_url)

    try:
        # Wait for the specific element to appear before saving
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR,
             "#root > div > div.pageLayout__container > div.PageCardUI__CardWrapper-sc-2y0onb-0.hpUDFW > div > div.styled__DateWrapper-sc-17e25jw-0.kmsYLH")
        ))
        # Optionally, wait an extra second to ensure everything is loaded
        time.sleep(1)
    except Exception as e:
        print(f"Warning: Timeout waiting for element on {game_url}. Error: {e}")

    # Get the rendered HTML
    html_content = driver.page_source

    # Save the HTML to a file in the output folder
    filename = f"game_{idx}.html"
    file_path = os.path.join(output_folder, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Saved game page to {file_path}")
