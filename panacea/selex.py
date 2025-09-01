from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
import time
import os
from tqdm import tqdm  # For progress bar (install with `pip install tqdm`)

def extract_grok_log():
    share_link = input("Please enter the Grok share link (e.g., https://grok.x.ai/share/xxx): ").strip()
    if not share_link:
        print("No link provided. Exiting.")
        return
    
    default_path = os.path.join(os.getcwd(), "grok_log.md")
    save_path = input(f"Enter save path (press Enter for default: {default_path}): ").strip()
    if not save_path:
        save_path = default_path
    output_file = os.path.abspath(save_path)
    
    driver = None
    try:
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=chrome_options)
        print(f"Opening link: {share_link}")
        driver.get(share_link)
        
        print("Waiting for page to load...")
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        
        print("Scrolling to load full conversation...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 20  # Increased for huge records
        with tqdm(total=max_scrolls, desc="Scrolling Progress") as pbar:
            while scroll_attempts < max_scrolls:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(4)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_attempts += 1
                pbar.update(1)
        
        print("Extracting messages in chunks...")
        messages = driver.find_elements(By.CSS_SELECTOR, '.message, .chat-message, [data-message], [class*="message-"], p, div:not([class])')
        log_content = "# Grok Session Log\n\n"
        chunk_size = 100  # Increased for efficiency
        total_messages = len(messages)
        with tqdm(total=total_messages, desc="Extracting Messages") as pbar:
            for i in range(0, total_messages, chunk_size):
                chunk = messages[i:i + chunk_size]
                for msg in chunk:
                    try:
                        sender = msg.find_element(By.CSS_SELECTOR, '.sender, .user-label, [data-role="user"], [data-role="assistant"]').text if msg.find_element(By.CSS_SELECTOR, '.sender, .user-label, [data-role="user"], [data-role="assistant"]') else "Unknown"
                    except:
                        sender = "Unknown"
                    try:
                        text = msg.find_element(By.CSS_SELECTOR, '.text, .content, p').text if msg.find_element(By.CSS_SELECTOR, '.text, .content, p') else msg.text
                    except:
                        text = msg.text
                    try:
                        timestamp = msg.find_element(By.CSS_SELECTOR, '.timestamp, .time').text if msg.find_element(By.CSS_SELECTOR, '.timestamp, .time') else ""
                    except:
                        timestamp = ""
                    log_content += f"## {sender} ({timestamp})\n{text}\n\n"
                
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write(log_content)
                log_content = ""  # Reset for next chunk
                pbar.update(len(chunk))
        
        if log_content:  # Save any remainder
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(log_content)
        
        print(f"Log saved to {output_file}")
        print("Extraction complete. Press Enter to close.")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Causes: ChromeDriver mismatch, invalid link, or page load timeout.")
        if driver:
            print("Debug: " + (driver.page_source[:500] + "..." if len(driver.page_source) > 500 else driver.page_source))
    
    finally:
        if driver:
            input("Press Enter to close...")
            driver.quit()

if __name__ == "__main__":
    extract_grok_log()