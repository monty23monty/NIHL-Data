import time
from urllib.parse import urljoin
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

base_url = "https://hockey.instatscout.com"
driver = webdriver.Chrome()

# Log in
driver.get("https://hockey.instatscout.com")
driver.maximize_window()
time.sleep(2)

username_input = driver.find_element(By.ID, "username")
username_input.click()
username_input.send_keys("tom@mk-lightning.co.uk")
time.sleep(2)

send_button = driver.find_element(
    By.CSS_SELECTOR,
    "body > code > div > main > section > div > div > div > div.cb3221fbd.c36ab57df > div > form > div.c4d5413ce > button"
)
send_button.click()
time.sleep(2)

password_input = driver.find_element(By.ID, "password")
password_input.click()
password_input.send_keys("MKLInstat2024!")
submit_button = driver.find_element(
    By.CSS_SELECTOR,
    "body > code > div > main > section > div > div > div > form > div.c4d5413ce > button"
)
submit_button.click()
time.sleep(5)

# Go to the tournament page
driver.get("https://hockey.instatscout.com/tournaments/5150")

# Create output folder if it doesn't exist
output_folder = "games_html"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

processed_games = set()
target_game_found = False
game_counter = 1

while not target_game_found:
    # Wait until game elements are present
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.MatchRow-sc-ibjx1d-0.iEmfdu a[href]"))
    )
    game_elements = driver.find_elements(By.CSS_SELECTOR, "div.MatchRow-sc-ibjx1d-0.iEmfdu a[href]")

    # Process each game that hasn't been handled yet
    for element in game_elements:
        href = element.get_attribute("href")
        full_url = urljoin(base_url, href)  # Ensure absolute URL

        if full_url in processed_games:
            continue
        processed_games.add(full_url)

        print(f"Processing game URL: {full_url}")

        # Open the game URL in a new tab
        original_window = driver.current_window_handle
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(full_url)

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "#root > div > div.pageLayout__container > div.PageCardUI__CardWrapper-sc-2y0onb-0.hpUDFW > div > div.styled__DateWrapper-sc-17e25jw-0.kmsYLH"
                ))
            )
            time.sleep(1)  # Extra delay to ensure the page is fully loaded
        except Exception as e:
            print(f"Warning: Timeout waiting for element on {full_url}. Error: {e}")

        # Save the game page HTML
        filename = f"game_{game_counter}.html"
        file_path = os.path.join(output_folder, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"Saved game page to {file_path}")
        game_counter += 1

        # Check if this is the target game
        if "/matches/1887151" in full_url:
            print("Target game processed. Exiting loop.")
            target_game_found = True

        # Close the game tab and switch back to the tournament page
        driver.close()
        driver.switch_to.window(original_window)

        if target_game_found:
            break

    if target_game_found:
        break

    # Click the "Show More" button to load additional games
    try:
        show_more_button = driver.find_element(
            By.CSS_SELECTOR,
            "#root > div > div.pageLayout__container > div.ContentWrapper-sc-1b862a8-0.PageLayout__PageContent-sc-dxbwcu-0.bGpgEm > div > div > div.Container__Content-sc-1gqbs7h-1.iVcETQ > button"
        )
        print("Clicking 'Show More' button to load additional games...")
        show_more_button.click()
        time.sleep(2)  # Wait for new games to load
    except Exception as e:
        print("No 'Show More' button found or error clicking it:", e)
        break

print("Script completed.")
driver.quit()
