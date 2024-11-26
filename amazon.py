from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time
import logging

# Initialize Selenium WebDriver
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(r"C:\Users\Asus\Downloads\chromedriver\chromedriver-win64\chromedriver.exe"), options=options)

# Amazon login credentials
USERNAME = "USERNAME"
PASSWORD = "PASSWORD"

# Define category URLs
category_urls = [
    "https://www.amazon.in/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0",
    # "https://www.amazon.in/gp/bestsellers/shoes/ref=zg_bs_nav_shoes_0",
    # "https://www.amazon.in/gp/bestsellers/electronics/ref=zg_bs_nav_electronics_0",
    # "https://www.amazon.in/gp/bestsellers/jewelry/ref=zg_bs_nav_jewelry_0",
    # "https://www.amazon.in/gp/bestsellers/sports/ref=zg_bs_nav_sports_0",
    # "https://www.amazon.in/gp/bestsellers/grocery/ref=zg_bs_nav_grocery_0",
    # "https://www.amazon.in/gp/bestsellers/pet-supplies/ref=zg_bs_nav_pet-supplies_0",
    # "https://www.amazon.in/gp/bestsellers/videogames/ref=zg_bs_nav_videogames_0",
    # "https://www.amazon.in/gp/bestsellers/watches/ref=zg_bs_nav_watches_0",
    # "https://www.amazon.in/gp/bestsellers/luggage/ref=zg_bs_nav_luggage_0"
]

def amazon_login():
    """Login to Amazon using the provided credentials."""
    driver.get("https://www.amazon.in/")
    
    try:
        # Debugging: Save screenshot
        driver.save_screenshot("homepage.png")
        
        # Click on 'Sign in'
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "nav-link-accountList"))
        )
        sign_in_button.click()
    except Exception as e:
        print("Error locating Sign-in button:", e)
        driver.save_screenshot("sign_in_error.png")
        return

    try:
        # Enter email/phone
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_email"))
        )
        email_input.send_keys(USERNAME)
        driver.find_element(By.ID, "continue").click()
    except Exception as e:
        print("Error entering email:", e)
        driver.save_screenshot("email_error.png")
        return

    try:
        # Enter password
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_password"))
        )
        password_input.send_keys(PASSWORD)
        driver.find_element(By.ID, "signInSubmit").click()
    except Exception as e:
        print("Error entering password:", e)
        driver.save_screenshot("password_error.png")
        return

    try:
        # Confirm successful login
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "nav-logo"))
        )
        print("Login successful.")
    except Exception as e:
        print("Error after login (possibly CAPTCHA):", e)
        driver.save_screenshot("login_failure.png")

driver.maximize_window()

def scroll_to_load_all():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Adjust the sleep time as needed
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scrape_category(category_url):
    """Scrape products from a single category."""
    driver.get(category_url)
    time.sleep(2)  # Allow page to load

    product_list = []
    scroll_to_load_all()  # Ensure all products are loaded

    try:
        product_containers = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@class='p13n-sc-uncoverable-faceout']"))
        )
        print(f"Found {len(product_containers)} products in {category_url}.")

        for container in product_containers:
            try:
                product_name = container.find_element(By.XPATH, """//*[@id="productTitle"]""").text
            except NoSuchElementException:
                product_name = "Name not available"

            try:
                product_price = container.find_element(By.XPATH, ".//span[contains(@class, 'p13n-sc-price')]").text
            except NoSuchElementException:
                product_price = "Price not available"

            try:
                rating = container.find_element(By.XPATH, ".//span[contains(@class, 'a-icon-alt')]").text
            except NoSuchElementException:
                rating = "Rating not available"

            product_info = {
                "Product Name": product_name,
                "Product Price": product_price,
                "Rating": rating,
                "Category URL": category_url,
            }
            product_list.append(product_info)

    except Exception as e:
        print(f"Error scraping category: {category_url}. Exception: {e}")
        driver.save_screenshot("category_error.png")

    return product_list

def save_to_csv(data, filename):
    """Save scraped data to a CSV file."""
    if data:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    else:
        print("No data to save!")

print("Hello")

def main():
    amazon_login()  # Perform login

    all_products = []
    for category_url in category_urls:
        print(f"Scraping category: {category_url}")
        products = scrape_category(category_url)
        all_products.extend(products)
        time.sleep(2)  # Prevent too many rapid requests

    # # Save data to CSV
    save_to_csv(all_products, "amazon_filtered_products.csv")
    driver.quit()

if __name__ == "__main__":
    main()