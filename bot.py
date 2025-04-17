import time
import csv
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import pyautogui
import os
import random

USERNAME = "bebesitahavoglia"
PASSWORD = "HaVogLi41!_"
TARGET_PROFILE = "lafederica.nazionale"
FOLLOWED_USERS_FILE = 'followed_users.csv'

def login_to_instagram(driver):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)
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
    with open(FOLLOWED_USERS_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([username, datetime.now().strftime("%Y-%m-%d")])

def is_male_username(username):
    male_keywords = [
        "marco", "giovanni", "luca", "mario", "andrea", "luigi", "paolo", "francesco",
        "angelo", "alessandro", "davide", "samuele", "enrico", "domenico", "salvatore",
        "giuseppe", "fabio", "riccardo", "gabriele", "lorenzo", "emanuele", "carlo",
        "claudio", "roberto", "antonio", "vincenzo", "matteo", "stefano", "federico",
        "michele", "massimo", "giacomo", "franco", "alberto", "ugo", "raffaele", "renato",
        "pietro", "tommaso", "cesare", "nestore", "elio", "ernesto", "aldo", "tullio",
        "teodoro", "armando", "corrado", "silvio", "oscar", "edoardo", "ettore", "rino",
        "agostino", "arturo", "gino", "luigino", "gianni", "maurizio", "nicolò",
        "valerio", "ivan", "sebastiano", "giordano", "mirko", "leonardo", "daniele",
        "pierluigi", "pierpaolo", "gianluca", "gianmarco", "gianfranco", "gianpiero",
        "christian", "cristian", "pasquale", "rosario", "cosimo", "nunzio",
        "sergio", "ludovico", "ruggiero", "gualtiero", "albino", "fabrizio", "damiano",
        "eugenio", "eliseo", "giulio", "orazio", "adolfo", "ferruccio", "nello",
        "donato", "alessio", "teo", "guido", "matias", "rocco", "battista", "remo"
    ]
    return any(name in username.lower() for name in male_keywords)

def get_follower_usernames(driver, max_followers=200):
    print("📜 Scrolling followers and collecting usernames...")
    try:
        wait = WebDriverWait(driver, 15)
        modal = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@role='dialog']//div[contains(@style, 'overflow')]")
        ))
    except:
        print("❌ Could not find the followers list. Is the modal really open?")
        input("🔍 Press Enter to exit.")
        driver.quit()
        return []

    usernames = set()
    scrolls = 0
    max_scrolls = 50

    while len(usernames) < max_followers and scrolls < max_scrolls:
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
        screen_width, screen_height = pyautogui.size()
        pyautogui.moveTo(screen_width / 2, screen_height / 2)
        pyautogui.scroll(-300)
        scrolls += 1
        time.sleep(1.5)

    print(f"🎉 Collected {len(usernames)} usernames.")
    return list(usernames)

def unfollow_old_users(driver):
    print("🧹 Checking for users to unfollow...")
    if not os.path.exists(FOLLOWED_USERS_FILE):
        return
    rows = []
    with open(FOLLOWED_USERS_FILE, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:
                username, date_str = row
                follow_date = datetime.strptime(date_str, "%Y-%m-%d")
                if datetime.now() - follow_date >= timedelta(days=2):
                    try:
                        driver.get(f"https://www.instagram.com/{username}/")
                        time.sleep(3)
                        unfollow_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[text()='Following']"))
                        )
                        unfollow_btn.click()
                        confirm_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[text()='Unfollow']"))
                        )
                        confirm_btn.click()
                        print(f"❌ Unfollowed: {username}")
                        continue
                    except:
                        print(f"⚠️ Could not unfollow: {username}")
            rows.append(row)
    with open(FOLLOWED_USERS_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)
    
def follow_male_usernames(driver, usernames, max_to_follow=20):
    male_usernames = []
    for username in usernames:
        if is_male_username(username):
            male_usernames.append(username)
            print(f"✅ Queued male username: {username}")
        if len(male_usernames) >= max_to_follow:
            break

    print(f"🚀 Visiting {max_to_follow} male profiles and following them...")

    for username in male_usernames:
        try:
            driver.get(f"https://www.instagram.com/{username}/")
            time.sleep(3)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            buttons = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "button"))
            )
            found = False
            for btn in buttons:
                if btn.text.strip().lower() == "follow":
                    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", btn)
                    save_followed_user(username)
                    print(f"✅ Followed: {username}")
                    time.sleep(random.uniform(3.5, 6))
                    found = True
                    break
            if not found:
                print(f"⚠️ No clickable follow button found: {username}")
        except Exception as e:
            print(f"⚠️ Could not follow: {username} — {e}")


def main():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)

    try:
        login_to_instagram(driver)
        unfollow_old_users(driver)
        go_to_target_profile(driver, TARGET_PROFILE)
        open_followers_list(driver)

        usernames = get_follower_usernames(driver, max_followers=200)
        follow_male_usernames(driver, usernames)

        input("✅ Done! Press Enter to close the bot.")
    except Exception as e:
        print(f"🚨 Error: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass
if __name__ == "__main__":
    main()
