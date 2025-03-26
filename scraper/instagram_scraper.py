import time
import random
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import config

class InstagramScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        # Instagram login credentials (you should set these in your .env file)
        self.username = os.getenv('INSTAGRAM_USERNAME', '')
        self.password = os.getenv('INSTAGRAM_PASSWORD', '')
        
    def delay_between_requests(self):
        """Introduce a random delay between requests to mimic human behavior."""
        delay = random.uniform(config.SCRAPER_DELAY_MIN, config.SCRAPER_DELAY_MAX)
        time.sleep(delay)
    
    def login_to_instagram(self, driver):
        """Log in to Instagram using provided credentials."""
        try:
            # Check if credentials are available
            if not self.username or not self.password:
                print("Instagram credentials not found. Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in .env file.")
                return False
                
            # Navigate to Instagram login page
            print("Navigating to Instagram login page...")
            driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(3)  # Wait for page to load
            
            # Handle cookie consent if present
            try:
                cookie_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Allow')]")
                if cookie_buttons:
                    cookie_buttons[0].click()
                    time.sleep(1)
            except:
                pass
                
            # Enter username
            try:
                username_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                username_input.clear()
                username_input.send_keys(self.username)
                print("Username entered")
            except Exception as e:
                print(f"Could not enter username: {str(e)}")
                return False
                
            # Enter password
            try:
                password_input = driver.find_element(By.NAME, "password")
                password_input.clear()
                password_input.send_keys(self.password)
                print("Password entered")
            except Exception as e:
                print(f"Could not enter password: {str(e)}")
                return False
                
            # Click login button
            try:
                login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
                login_button.click()
                print("Login button clicked")
            except Exception as e:
                print(f"Could not click login button: {str(e)}")
                return False
                
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            if "challenge" in driver.current_url or "login" in driver.current_url:
                print("Login failed or additional verification required.")
                return False
                
            # Handle "Save Login Info" dialog if it appears
            try:
                not_now_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                )
                not_now_button.click()
                time.sleep(1)
            except:
                print("No 'Save Login Info' dialog appeared or it was handled automatically.")
            
            # Handle notifications dialog if it appears
            try:
                not_now_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                )
                not_now_button.click()
                time.sleep(1)
            except:
                print("No notifications dialog appeared or it was handled automatically.")
                
            print("Successfully logged in to Instagram")
            return True
            
        except Exception as e:
            print(f"Error during login: {str(e)}")
            return False
    
    def get_profile_posts(self, profile_name, keywords=None):
        """Scrape posts from a public Instagram profile using Selenium with login."""
        if keywords and not isinstance(keywords, list):
            keywords = [keywords]
        
        matching_posts = []
        driver = None
        
        try:
            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={config.USER_AGENT}")
            
            # Initialize the Chrome driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Log in to Instagram first
            login_success = self.login_to_instagram(driver)
            if not login_success:
                print("Couldn't log in to Instagram. Cannot proceed with scraping.")
                return []
            
            # Go to the profile page
            profile_url = f"https://www.instagram.com/{profile_name}/"
            print(f"Navigating to {profile_url}")
            driver.get(profile_url)
            time.sleep(3)  # Wait for the page to load
            
            # Check if profile exists or is accessible
            if "Page Not Found" in driver.title or "Add your birthday" in driver.page_source:
                print(f"Profile {profile_name} not found or not accessible")
                return []
            
            # Get post links - looking for links that contain "/p/" which is Instagram's post URL format
            print("Looking for post links...")
            wait = WebDriverWait(driver, 5)
            try:
                # Wait for posts to appear
                wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/p/')]")))
            except TimeoutException:
                print("Couldn't find any posts")
                return []
            
            # Get all post links
            post_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
            post_urls = [link.get_attribute('href') for link in post_links]
            
            print(f"Found {len(post_urls)} post links")
            
            # Visit each post page to get details (limited to first 10 posts for reasonable performance)
            for i, post_url in enumerate(post_urls[:10]):
                self.delay_between_requests()  # Add delay between post visits
                
                print(f"Visiting post {i+1}: {post_url}")
                driver.get(post_url)
                time.sleep(2)  # Wait for post page to load
                
                try:
                    # Try to get the caption using the h1 element you found
                    caption = ""
                    
                    # Try different selectors for captions, STARTING WITH THE ONE YOU FOUND
                    selectors = [
                        "//h1[contains(@class, '_ap3a')]",  # This should match the h1 you found
                        "//h1[contains(@class, 'aad7')]",   # Another variation of the class
                        "//h1[contains(@dir, 'auto')]",     # h1 with dir attribute
                        "//div[contains(@class, 'C4VMK')]/span",  # Older Instagram
                        "//h1/following-sibling::span",  # Another potential location
                        "//span[@role='link']/following-sibling::span", # Common pattern
                        "//div[contains(@class, '_a9zs')]/span",  # New Instagram pattern
                        "//div[contains(@class, '_a9zr')]/span",  # Another new pattern
                        "//div[contains(@class, 'caption')]/span", # Generic caption class
                        "//article//span[string-length(text()) > 15]", # Any longer text in the article
                        "//article//h1",  # Any h1 in article
                    ]
                    
                    # Save page source for debugging
                    with open(f"instagram_post_{i}.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    print(f"Saved page source to instagram_post_{i}.html")
                    
                    for selector in selectors:
                        try:
                            caption_elems = driver.find_elements(By.XPATH, selector)
                            if caption_elems:
                                caption = caption_elems[0].text
                                if len(caption) > 5:  # If we found something substantial
                                    print(f"Found caption using selector: {selector}")
                                    break
                        except Exception as e:
                            print(f"Error with selector {selector}: {e}")
                            continue
                    
                    # If all selectors failed, try a more generic approach
                    if not caption:
                        print("All selectors failed. Trying a more generic approach.")
                        try:
                            # Dump all text elements with substantial content
                            all_text_elements = driver.find_elements(By.XPATH, "//*[string-length(text()) > 20]")
                            print(f"Found {len(all_text_elements)} text elements with substantial content")
                            for element in all_text_elements[:5]:  # Print first 5 for debugging
                                print(f"Text element: {element.text[:50]}...")
                                
                            # Use the first substantial text element as our caption
                            if all_text_elements:
                                caption = all_text_elements[0].text
                        except Exception as e:
                            print(f"Error with generic approach: {e}")
                            caption = ""
                    
                    print(f"Final caption: {caption[:100]}...")
                    
                    # Extract post ID from URL
                    post_id = post_url.split("/p/")[1].split("/")[0]
                    
                    # Check if the caption contains any of the keywords
                    if keywords:
                        caption_lower = caption.lower()
                        matched_keywords = []
                        
                        for keyword in keywords:
                            if keyword.lower() in caption_lower:
                                matched_keywords.append(keyword)
                        
                        # Only include posts that match keywords
                        if not matched_keywords:
                            print(f"Post {post_id} doesn't contain any of the keywords {keywords}")
                            continue
                    else:
                        matched_keywords = []
                    
                    # Try to get the post date
                    post_date = int(time.time()) - (i * 86400)  # Default: fallback to current time minus offset
                    try:
                        # Try to find a time element
                        time_elem = driver.find_element(By.XPATH, "//time")
                        datetime_str = time_elem.get_attribute("datetime")
                        if datetime_str:
                            # Convert to timestamp (datetime strings are in format like 2023-01-01T12:00:00.000Z)
                            from datetime import datetime
                            post_date = int(datetime.strptime(datetime_str.split('.')[0], "%Y-%m-%dT%H:%M:%S").timestamp())
                    except:
                        pass  # Keep using the fallback date
                    
                    # Create post object
                    post_data = {
                        'id': post_id,
                        'caption': caption,
                        'postDate': post_date,
                        'postLink': post_url,
                        'profileName': profile_name,
                        'matchedKeywords': matched_keywords
                    }
                    
                    matching_posts.append(post_data)
                    print(f"Added post with caption: {caption[:50]}...")
                    
                except Exception as e:
                    print(f"Error processing post {post_url}: {str(e)}")
            
            # Return what we found, even if empty
            return matching_posts
            
        except Exception as e:
            print(f"Scraping error: {str(e)}")
            return []
            
        finally:
            # Always close the driver
            if driver:
                driver.quit()
                print("Selenium driver closed")