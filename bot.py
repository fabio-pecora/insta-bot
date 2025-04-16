import time
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

USERNAME = "bebesitahavoglia"
PASSWORD = "HaVogLi41!_"
TARGET_PROFILE = "lafederica.nazionale"

def login_to_instagram(driver):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)
    
    # Accept cookies
    try:
        cookies_btn = driver.find_element(By.XPATH, "//button[text()='Only allow essential cookies']")
        cookies_btn.click()
        time.sleep(2)
    except:
        pass

    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")

    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)
    password_input.send_keys(Keys.ENTER)

    time.sleep(5)

def go_to_target_profile(driver, profile_username):
    driver.get(f"https://www.instagram.com/{profile_username}/")
    time.sleep(4)

def open_followers_list(driver):
    followers_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'/followers')]"))
    )
    followers_button.click()
    time.sleep(3)

def save_followed_user(username):
    with open('followed_users.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([username, datetime.now().strftime("%Y-%m-%d")])

def is_male_username(username):
    male_keywords = [
        "marco", "giovanni", "luca", "john", "mario", "andrea", "luigi",
        "guy", "boy", "man", "he", "him", "riccardo", "paolo", "francesco",
        "angelo", "alessandro", "davide", "samuele", "enrico", "domenico"
    ]
    return any(name in username.lower() for name in male_keywords)

def get_follower_usernames(driver, max_followers=100):
    print("📜 Scrolling followers and collecting usernames...")

    try:
        wait = WebDriverWait(driver, 15)
        modal = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//div[contains(@style, 'overflow')]")))

    except:
        print("❌ Could not find the followers list. Is the modal really open?")
        input("🔍 Press Enter to exit.")
        driver.quit()
        return []

    last_height = 0
    usernames = set()

    while len(usernames) < max_followers:
        links = modal.find_elements(By.TAG_NAME, "a")
        for link in links:
            href = link.get_attribute("href")
            if href and "/" in href:
                username = href.split("/")[-2]
                if username and username not in usernames:
                    usernames.add(username)
                    print(f"✅ Found: {username}")
                    if len(usernames) >= max_followers:
                        break
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
        time.sleep(1.5)

    print(f"🎉 Collected {len(usernames)} usernames.")
    return list(usernames)

def follow_user_from_modal(driver, username):
    try:
        user_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href, '/{username}/')]/../../../..//button[text()='Follow']"))
        )
        user_button.click()
        save_followed_user(username)
        print(f"✅ Followed: {username}")
        time.sleep(2)
    except:
        print(f"⚠️ Could not follow: {username}")

def main():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)

    try:
        login_to_instagram(driver)
        go_to_target_profile(driver, TARGET_PROFILE)
        open_followers_list(driver)

        input("🛑 Check if followers modal is open, then press Enter to continue...")

        usernames = get_follower_usernames(driver, max_followers=100)

        followed = 0
        for username in usernames:
            if is_male_username(username):
                follow_user_from_modal(driver, username)
                followed += 1
                if followed >= 20:
                    break
            else:
                print(f"❌ Skipped (not male-ish): {username}")

        input("✅ Done! Press Enter to close the bot.")

    except Exception as e:
        print(f"🚨 Error: {e}")

    finally:
        try:
            driver.quit()
        except:
            pass  # Ignore WinError 6

if __name__ == "__main__":
    main()
