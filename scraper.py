from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# Amazon login credentials
USERNAME = "your_email@example.com"
PASSWORD = "your_password"

# Best Seller URLs for 10 Categories
category_urls = [
    "https://www.amazon.in/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0",
    "https://www.amazon.in/gp/bestsellers/shoes/ref=zg_bs_nav_shoes_0",
    "https://www.amazon.in/gp/bestsellers/computers/ref=zg_bs_nav_computers_0",
    "https://www.amazon.in/gp/bestsellers/electronics/ref=zg_bs_nav_electronics_0",
]

# Initialize the Selenium WebDriver
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def amazon_login():
    # Open Amazon login page
    driver.get("https://www.amazon.in/ap/signin")
    
    # Enter email/phone
    email_input = driver.find_element(By.ID, "ap_email")
    email_input.send_keys(USERNAME)
    
    # Click continue
    driver.find_element(By.ID, "continue").click()
    
    # Enter password
    password_input = driver.find_element(By.ID, "ap_password")
    password_input.send_keys(PASSWORD)
    
    # Click login
    driver.find_element(By.ID, "signInSubmit").click()

    # Wait for the homepage to load after login
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "nav-logo"))
    )
    print("Logged in to Amazon successfully.")

def scrape_category(category_url):
    driver.get(category_url)
    time.sleep(3)  # Let the page load
    
    product_list = []
    try:
        # Loop through up to 1500 best-selling products
        for i in range(1, 1501):
            try:
                product_name = driver.find_element(By.XPATH, f"(//div[@class='p13n-sc-truncate-desktop-type2 p13n-sc-truncated'])[position()={i}]").text
                product_price = driver.find_element(By.XPATH, f"(//span[@class='p13n-sc-price'])[position()={i}]").text
                best_seller_rating = driver.find_element(By.XPATH, f"(//span[@class='a-icon-alt'])[position()={i}]").text
                # Check for a discount of more than 50%
                discount = driver.find_element(By.XPATH, f"(//span[contains(text(), '% off')])[position()={i}]").text
                discount_percent = int(discount.replace('% off', '').strip())
                
                if discount_percent > 50:
                    product_info = {
                        "Product Name": product_name,
                        "Product Price": product_price,
                        "Best Seller Rating": best_seller_rating,
                        "Discount": discount_percent,
                        "Category URL": category_url
                    }
                    product_list.append(product_info)
            except Exception as e:
                # Handle exceptions if an element is not found (skip to next product)
                print(f"Error scraping product {i} in {category_url}: {e}")
    except Exception as e:
        print(f"Error in scraping category: {category_url}. Exception: {e}")
    return product_list

def save_data_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def main():
    amazon_login()  # Login to Amazon
    
    all_products = []
    
    for category_url in category_urls:
        print(f"Scraping category: {category_url}")
        category_products = scrape_category(category_url)
        all_products.extend(category_products)
        time.sleep(2)  # Avoid too many requests in a short time
    
    # Save data to CSV
    save_data_to_csv(all_products, "amazon_best_sellers.csv")

    driver.quit()

if __name__ == "__main__":
    main()
