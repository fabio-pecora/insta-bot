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



SEXY_POST_LINK = "https://www.instagram.com/reel/DIMUVkdMQsb/?igsh=dDYzeTEybzRpdDBl"

import json

# def load_instagram_session(driver):
#     driver.get("https://www.instagram.com/")
#     time.sleep(3)

#     # Load cookies from file
#     if os.path.exists("instagram_cookies.json"):
#         with open("instagram_cookies.json", "r") as file:
#             cookies = json.load(file)

#         for cookie in cookies:
#             cookie_dict = {
#                 "name": cookie.get("name"),
#                 "value": cookie.get("value"),
#                 "domain": cookie.get("domain"),
#                 "path": cookie.get("path", "/"),
#                 "secure": cookie.get("secure", False),
#                 "httpOnly": cookie.get("httpOnly", False),
#             }
#             if "expiry" in cookie:
#                 cookie_dict["expiry"] = cookie["expiry"]
#             try:
#                 driver.add_cookie(cookie_dict)
#             except Exception as e:
#                 print(f"⚠️ Skipped one cookie: {e}")

#         driver.get("https://www.instagram.com/")
#         time.sleep(3)
#         print("✅ Session cookies loaded successfully!")
#     else:
#         print("❌ Cookie file not found. Please export your cookies to 'instagram_cookies.json'")
#         input("⏸️ Press Enter to quit.")
#         driver.quit()

def human_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.08, 0.22))

def login_to_instagram(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    
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

    human_typing(username_input, username)
    time.sleep(random.uniform(1, 1.5))
    human_typing(password_input, password)
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

def save_followed_user(username, already_followed_file, followed_users_file):
    now = datetime.now().strftime("%m/%d/%Y")

    # Create all-time file if it doesn't exist
    if not os.path.exists(already_followed_file):
        open(already_followed_file, 'w').close()

    with open(already_followed_file, mode='r+', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        if any(row[0] == username for row in reader):
            print(f"⏭️ Skipping {username} — already in all-time list")
            return  # Already followed before

        f.seek(0, os.SEEK_END)
        writer = csv.writer(f)
        writer.writerow([username])
        print(f"📝 Added {username} to all-time list")

    # Add to current session's file
    with open(followed_users_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([username, now])
        print(f"📅 Added {username} to current follow tracking list")



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

def get_follower_usernames(driver, already_followed_file, max_targets=15):
    print("📜 Scrolling followers and collecting valid usernames...")
    try:
        wait = WebDriverWait(driver, 15)
        modal = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@role='dialog']//div[contains(@style, 'overflow')]")
        ))
    except:
        driver.quit()
        return []

    # helper function inside this one
    def is_already_followed(username):
        if not os.path.exists(already_followed_file):
            return False
        with open(already_followed_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            return any(row[0] == username for row in reader)

    usernames_seen = set()
    valid_targets = []
    scrolls = 0
    max_scrolls = 50

    while len(valid_targets) < max_targets and scrolls < max_scrolls:
        links = modal.find_elements(By.TAG_NAME, "a")
        for link in links:
            href = link.get_attribute("href")
            if href and "/" in href:
                username = href.split("/")[-2]
                if username and username not in usernames_seen:
                    usernames_seen.add(username)
                    print(f"✅ Found: {username}")
                    if is_male_username(username) and not is_already_followed(username):
                        valid_targets.append(username)
                        print(f"✅ Queued male username: {username}")
                        if len(valid_targets) >= max_targets:
                            break
        pyautogui.moveTo(pyautogui.size().width / 2, pyautogui.size().height / 2)
        pyautogui.scroll(-300)
        scrolls += 1
        time.sleep(1.5)

    print(f"🎯 Collected {len(valid_targets)} valid male usernames.")
    return valid_targets


def unfollow_old_users(driver, base_dir):
    print("🧹 Checking for users to unfollow...")

    followed_users_file = os.path.join(base_dir, "followed_users.csv")
    if not os.path.exists(followed_users_file):
        return

    rows = []
    with open(followed_users_file, mode='r', newline='', encoding='utf-8') as file:
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

                        try:
                            time.sleep(2)
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
                            continue
                    except Exception as e:
                        print(f"⚠️ Could not unfollow {username} — {e}")
                        rows.append(row)
                        continue
            else:
                rows.append(row)

    # Rewrite CSV with users still followed
    with open(followed_users_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def already_followed(username, base_dir):
    all_time_file = os.path.join(base_dir, "already_followed.csv")

    if not os.path.exists(all_time_file):
        return False

    with open(all_time_file, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        return any(row[0] == username for row in reader)


def warm_up_before_follow(driver):
    try:
        # Scroll profile page (simulate interest)
        scroll_depths = [500, 1000, 1500]
        for depth in scroll_depths:
            driver.execute_script(f"window.scrollTo(0, {depth});")
            time.sleep(random.uniform(2, 4))
        
        # Try clicking on the first story/highlight if available
        try:
            story = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "canvas[aria-label='User story ring']"))
            )
            driver.execute_script("arguments[0].click();", story)
            print("👁️ Viewed story")
            time.sleep(random.uniform(4, 6))  # let the story play briefly
            pyautogui.press('esc')  # close story
            time.sleep(1)
        except:
            print("ℹ️ No story/highlight found.")

    except Exception as e:
        print(f"⚠️ Failed to warm up before follow — {e}")

def follow_male_usernames(driver, usernames, already_followed_file, followed_users_file, max_to_follow=15):
    followed_this_round = []
    targets = []

    # Helper to check if someone is already followed (per account)
    def is_already_followed(username):
        if not os.path.exists(already_followed_file):
            return False
        with open(already_followed_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            return any(row[0] == username for row in reader)

    # ✅ Step 1: Filter just enough valid male usernames
    for username in usernames:
        if is_male_username(username) and not is_already_followed(username):
            targets.append(username)
            print(f"✅ Queued male username: {username}")
        if len(targets) >= max_to_follow:
            break

    print(f"🚀 Visiting {len(targets)} male profiles and following them...")

    # ✅ Step 2: Follow them
    for username in targets:
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
                    warm_up_before_follow(driver)
                    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", btn)
                    save_followed_user(username, already_followed_file, followed_users_file)
                    followed_this_round.append(username)
                    print(f"✅ Followed: {username}")
                    time.sleep(random.uniform(5, 10))  # safer delay
                    found = True
                    break

            if not found:
                print(f"⚠️ No clickable follow button found: {username}")

        except Exception as e:
            print(f"⚠️ Could not follow {username} — {e}")

    return followed_this_round



def like_recent_posts(driver,username, num_posts=2):
    try:
        driver.get(f"https://www.instagram.com/{username}/")
        time.sleep(4)
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


dm_messages = [
    f"Devi assolutamente vedere questo... {SEXY_POST_LINK}",
    f"Ho appena pubblicato qualcosa di piccante... {SEXY_POST_LINK}",
    f"Questo è per te, amore → {SEXY_POST_LINK}",
    f"Non è proprio da guardare al lavoro... {SEXY_POST_LINK}",
    f"Questo non te lo dimenticherai <3 {SEXY_POST_LINK}",
    f"Ti pensavo... guarda qui {SEXY_POST_LINK}",
    f"È il mio post preferito <3 {SEXY_POST_LINK}",
    f"Clicca solo se ti senti audace {SEXY_POST_LINK}",
    f"Contenuto esclusivo solo per i miei preferiti {SEXY_POST_LINK}",
    f"Scommetto che non riuscirai a smettere di guardarlo {SEXY_POST_LINK}"
]


def send_dm(driver, username="fabio.pecora01"):
    try:
        message_text = random.choice(dm_messages)
        print(f"✉️ Sending DM to @{username} — \"{message_text}\"")

        driver.get(f"https://www.instagram.com/{username}/")
        time.sleep(4)

        message_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Message']"))
        )
        driver.execute_script("arguments[0].click();", message_button)
        print("💬 Clicked the Message button")
        time.sleep(3)

        try:
            not_now_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Not Now']"))
            )
            not_now_button.click()
            print("🔕 Dismissed notification popup.")
            time.sleep(1)
        except:
            print("ℹ️ No notification popup appeared.")

        message_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='textbox']"))
        )
        message_input.click()
        human_typing(message_input, message_text)
        time.sleep(1)
        message_input.send_keys(Keys.ENTER)
        print(f"✅ DM sent to @{username}!")

        # 🛑 Wait for the message to visually appear in the chat box before continuing
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{message_text[:8]}')]"))
        )
        time.sleep(2.5)

    except Exception as e:
        print(f"⚠️ Failed to send DM to @{username} — {e}")




def run_bot_for_account(username, password, target_profile, max_to_follow):
    # Define file paths per account
    account_folder = f"accounts_data/{username}"
    os.makedirs(account_folder, exist_ok=True)

    followed_users_file = os.path.join(account_folder, "followed_users.csv")
    already_followed_file = os.path.join(account_folder, "already_followed.csv")

    # Chrome setup
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)

    try:
        # Use credentials to log in
        login_to_instagram(driver, username, password)

        # Perform unfollow using local file
        unfollow_old_users(driver, account_folder)

        # Main bot actions
        go_to_target_profile(driver, target_profile)
        open_followers_list(driver)
        usernames = get_follower_usernames(driver, already_followed_file, max_targets=max_to_follow)
        followed = follow_male_usernames(
            driver,
            usernames,
            already_followed_file,
            followed_users_file,
            max_to_follow=max_to_follow
        )

        for u in followed:
            send_dm(driver, u)
            time.sleep(random.uniform(3, 6))
            like_recent_posts(driver, u, num_posts=1)

    except Exception as e:
        print(f"❌ Error for {username}: {e}")
    finally:
        driver.quit()

def run_for_all_accounts():
    with open('accounts.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            username = row['username']
            password = row['password']
            target = row['target_profile']
            max_to_follow = int(row['max_to_follow'])

            print(f"\n🔄 Running bot for {username} targeting {target}")
            run_bot_for_account(username, password, target, max_to_follow)

if __name__ == "__main__":
    run_for_all_accounts()
