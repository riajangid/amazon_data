from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time

# Initialize Selenium WebDriver
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(r"C:\Users\Asus\Downloads\chromedriver\chromedriver-win64\chromedriver.exe"), options=options)

# Amazon login credentials
USERNAME = "9358900219"
PASSWORD = "#Riya1234#"

def amazon_login():
    """Login to Amazon using the provided credentials."""
    driver.get("https://www.amazon.in/")
    try:
        # Click on 'Sign in'
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "nav-link-accountList"))
        )
        sign_in_button.click()

        # Enter email/phone
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_email"))
        )
        email_input.send_keys(USERNAME)
        driver.find_element(By.ID, "continue").click()

        # Enter password
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_password"))
        )
        password_input.send_keys(PASSWORD)
        driver.find_element(By.ID, "signInSubmit").click()

        # Confirm successful login
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "nav-logo"))
        )
        print("Login successful.")
    except Exception as e:
        print("Login failed:", e)
        driver.save_screenshot("login_error.png")

driver.maximize_window()        

def get_product_details_from_category_page(category_url):
    """Scrape product details for all products from their containers on the category page."""
    driver.get(category_url)

    # Ensure all products are loaded (handle lazy loading or infinite scroll, if necessary)
    time.sleep(5)

    # Find all product containers
    try:
        product_containers = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'zg-grid-general-faceout')]"))
        )
        print(f"Found {len(product_containers)} products on the category page.")
    except Exception as e:
        print(f"Error locating product containers: {e}")
        return []

    product_details_list = []

    # Loop through all product containers
    for index, container in enumerate(product_containers):
        try:
            # Scroll to the product container
            driver.execute_script("arguments[0].scrollIntoView(true);", container)

            # Extract product details from the container
            product_details = {
                "Product Name": "Name not available",
                "Product Price": "Price not available",
                "Rating": "Rating not available",
                "Product URL": "URL not available",
            }

            try:
                product_details["Product Name"] = container.find_element(By.CSS_SELECTOR, ".p13n-sc-truncate").text.strip()
            except NoSuchElementException:
                pass

            try:
                product_details["Product Price"] = container.find_element(By.CSS_SELECTOR, ".p13n-sc-price").text.strip()
            except NoSuchElementException:
                pass

            try:
                product_details["Rating"] = container.find_element(By.CSS_SELECTOR, ".a-icon-alt").get_attribute("textContent").strip()
            except NoSuchElementException:
                pass

            try:
                product_details["Product URL"] = container.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            except NoSuchElementException:
                pass

            # Add product details to the list
            product_details_list.append(product_details)
            print(f"Scraped product {index + 1}: {product_details}")

        except Exception as e:
            print(f"Error scraping product at index {index}: {e}")
            driver.save_screenshot(f"product_{index}_error.png")

    return product_details_list

def save_to_csv(data, filename):
    """Save scraped data to a CSV file."""
    if data:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    else:
        print("No data to save!")

def main():
    amazon_login()  # Perform login

    # Define the category URL
    category_url = "https://www.amazon.in/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0"

    # Step 1: Scrape all product details from the category page
    print(f"Scraping products from category: {category_url}")
    all_products = get_product_details_from_category_page(category_url)

    # Step 2: Save the scraped data to a CSV file
    save_to_csv(all_products, "amazon_category_products.csv")

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    main()
