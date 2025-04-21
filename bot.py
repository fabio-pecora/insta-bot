import time
import csv
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
import pyautogui
import os
import random

USERNAME = "george_jordan123456"
PASSWORD = "ciaociaociaO1.."
TARGET_PROFILE = "lafederica.nazionale"
FOLLOWED_USERS_FILE = 'followed_users.csv'


import json

def load_instagram_session(driver):
    driver.get("https://www.instagram.com/")
    time.sleep(3)

    # Load cookies from file
    if os.path.exists("instagram_cookies.json"):
        with open("instagram_cookies.json", "r") as file:
            cookies = json.load(file)

        for cookie in cookies:
            cookie_dict = {
                "name": cookie.get("name"),
                "value": cookie.get("value"),
                "domain": cookie.get("domain"),
                "path": cookie.get("path", "/"),
                "secure": cookie.get("secure", False),
                "httpOnly": cookie.get("httpOnly", False),
            }
            if "expiry" in cookie:
                cookie_dict["expiry"] = cookie["expiry"]
            try:
                driver.add_cookie(cookie_dict)
            except Exception as e:
                print(f"⚠️ Skipped one cookie: {e}")

        driver.get("https://www.instagram.com/")
        time.sleep(3)
        print("✅ Session cookies loaded successfully!")
    else:
        print("❌ Cookie file not found. Please export your cookies to 'instagram_cookies.json'")
        input("⏸️ Press Enter to quit.")
        driver.quit()

def human_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.08, 0.22))


def login_to_instagram(driver):
    driver.get("https://www.instagram.com/accounts/login/")
    
    # Wait until username input is ready
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    time.sleep(random.uniform(1, 2))

    try:
        cookies_btn = driver.find_element(By.XPATH, "//button[text()='Only allow essential cookies']")
        cookies_btn.click()
        time.sleep(1)
    except:
        pass

    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")

    human_typing(username_input, USERNAME)
    time.sleep(random.uniform(1, 1.5))
    human_typing(password_input, PASSWORD)
    time.sleep(random.uniform(0.5, 1))

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
        writer.writerow([username, datetime.now().strftime("%m/%d/%Y")])

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
                try:
                    follow_date = datetime.strptime(date_str, "%m/%d/%Y")
                except ValueError:
                    print(f"⚠️ Invalid date format for {username}: {date_str}")
                    rows.append(row)
                    continue

                if datetime.now() - follow_date >= timedelta(days=2):
                    try:
                        driver.get(f"https://www.instagram.com/{username}/")
                        time.sleep(4)

                        # Step 1: Click the "Following" button
                        buttons = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.TAG_NAME, "button"))
                        )
                        following_btn = next((btn for btn in buttons if "following" in btn.text.strip().lower()), None)

                        if not following_btn:
                            raise Exception("No 'Following' button found")

                        driver.execute_script("arguments[0].scrollIntoView(true);", following_btn)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", following_btn)
                        time.sleep(1.5)

                        # testing what buttons we have
                        # time.sleep(2)
                        # buttons = driver.find_elements(By.TAG_NAME, "button")
                        # print(f"🧩 Found {len(buttons)} buttons on screen after clicking 'Following':")
                        # for idx, btn in enumerate(buttons):
                        #     try:
                        #         print(f"{idx+1}. '{btn.text}' - displayed: {btn.is_displayed()}")
                        #     except:
                        #         print(f"{idx+1}. [Could not read text]")

                        # Try to find the Unfollow button in the dropdown menu
                        try:
                            time.sleep(2)  # Let the dropdown render
                            possible_unfollow_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Unfollow')]")

                            clicked = False
                            for el in possible_unfollow_elements:
                                if el.is_displayed():
                                    print(f"✅ Found unfollow element: '{el.text.strip()}'")
                                    driver.execute_script("arguments[0].click();", el)
                                    clicked = True
                                    print(f"❌ Unfollowed: {username}")
                                    break
                            if not clicked:
                                raise Exception("Unfollow button not found or not visible.")
                        except Exception as e:
                            print(f"⚠️ Could not click 'Unfollow' button for {username} — {e}")
                            rows.append(row)
                            print(f"❌ Unfollowed: {username}")
                            continue   
                        except Exception as e:
                            print(f"⚠️ Could not click 'Unfollow' button for {username} — {e}")
                            rows.append(row)
                            continue
                    except Exception as e:
                        print(f"⚠️ Could not unfollow {username} — {e}")
                        rows.append(row)
                        continue
            else:
                rows.append(row)
    # Rewrite CSV only for users still followed
    with open(FOLLOWED_USERS_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

def follow_male_usernames(driver, usernames, max_to_follow=20):
    male_usernames = []
    followed_this_round = []

    for username in usernames:
        if is_male_username(username):
            male_usernames.append(username)
            print(f"✅ Queued male username: {username}")
        if len(male_usernames) >= max_to_follow:
            break

    print(f"🚀 Visiting {len(male_usernames)} male profiles and following them...")

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
                    followed_this_round.append(username)
                    print(f"✅ Followed: {username}")
                    time.sleep(random.uniform(3.5, 6))
                    found = True
                    break

            if not found:
                print(f"⚠️ No clickable follow button found: {username}")

        except Exception as e:
            print(f"⚠️ Could not follow {username} — {e}")

    return followed_this_round

def like_recent_posts(driver, num_posts=2):
    try:
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(2)

        post_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
        if not post_links:
            raise Exception("No post links found on profile")

        liked = 0
        for post in post_links:
            if liked >= num_posts:
                break

            try:
                post_url = post.get_attribute("href")
                if not post_url:
                    continue

                driver.get(post_url)
                time.sleep(3)

                # Wait for image and double-click to like
                try:
                    image = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//article//img"))
                    )

                    actions = ActionChains(driver)
                    actions.move_to_element(image).pause(0.5).double_click(image).perform()

                    print("❤️ Double-clicked image to like")
                    liked += 1

                except Exception as e:
                    print(f"⚠️ Failed to double-click and like: {e}")
                    continue

                time.sleep(random.uniform(2, 4))

            except Exception as e:
                print(f"⚠️ Failed to process post: {e}")
                continue

    except Exception as e:
        print(f"⚠️ Could not find recent posts — {e}")


# test sendin msg to myself
def send_dm(driver, username="fabio.pecora01", message_text="Hey! This is a test message from my bot 😄"):
    try:
        print(f"✉️ Sending DM to @{username}...")
        driver.get(f"https://www.instagram.com/{username}/")
        time.sleep(4)

        # Click the Message div
        message_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Message']"))
        )
        driver.execute_script("arguments[0].click();", message_button)
        print("💬 Clicked the Message button")
        time.sleep(3)

        # Handle the popup
        try:
            not_now_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Not Now']"))
            )
            not_now_button.click()
            print("🔕 Dismissed notification popup.")
            time.sleep(1)
        except:
            print("ℹ️ No notification popup appeared.")

        # Find textarea and send message
        textarea = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "textarea"))
        )
        textarea.send_keys(message_text)
        time.sleep(1)
        textarea.send_keys(Keys.ENTER)
        print(f"✅ DM sent to @{username}!")

    except Exception as e:
        print(f"⚠️ Failed to send DM to @{username} — {e}")




def main():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    

    driver = uc.Chrome(options=options)  # ✅ Only create it once here

    try:
        # login_to_instagram(driver)  # ← this is for actual access
        load_instagram_session(driver)  # ← Use this for testing
        # unfollow_old_users(driver)
        # go_to_target_profile(driver, TARGET_PROFILE)
        # open_followers_list(driver)
        # usernames = get_follower_usernames(driver, max_followers=200)
        # recently_followed = follow_male_usernames(driver, usernames)
        
        #  # ✅ Like 2 posts for each person just followed
        # for username in recently_followed:
        #     test_like_specific_user(driver, username=username, num_posts=2)

        

        send_dm(driver)

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

