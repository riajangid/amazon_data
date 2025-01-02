from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import traceback
import csv
from datetime import date
import re
from apscheduler.schedulers.blocking import BlockingScheduler
import pandas as pd


# Initialize Selenium WebDriver
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(r"C:\Users\Asus\Downloads\chromedriver\chromedriver-win64\chromedriver.exe"), options=options)
driver.maximize_window()


def extract_asin(product_url):
    """Extract the ASIN from the product URL."""
    try:
        path_parts = urlparse(product_url).path.split('/')
        if 'dp' in path_parts:
            asin_index = path_parts.index('dp') + 1
            return path_parts[asin_index]
    except Exception as e:
        print(f"Error extracting ASIN: {e}")
    return "ASIN not available"


def extract_category(url):
    """Extract the category from the given URL."""
    try:
        # Parse the URL and extract the path segments
        path_parts = urlparse(url).path.split('/')
        if 'bestsellers' in path_parts:
            category_index = path_parts.index('bestsellers') + 1
            return path_parts[category_index]
    except Exception as e:
        print(f"Error extracting category: {e}")
    return "Category not available"    



def get_product_details_from_category_page(category_url,cat):
    """Scrape product details from a category page without images."""
    driver.get(category_url)
    
    WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/dp/')]"))
    )


    try:
        product_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/dp/')]"))
        )
        print(f"Found {len(product_links)} products on the category page.")
    except Exception as e:
        print(f"Error locating product links: {e}")
        return []

    product_details_list = []
    visited_urls = set()

    for rank, product_link in enumerate(product_links, start=1):
        try:
            product_url = product_link.get_attribute("href")
            if product_url in visited_urls:
                continue

            asin = extract_asin(product_url)
            visited_urls.add(product_url)
            driver.execute_script(f"window.open('{product_url}', '_blank');")
            driver.switch_to.window(driver.window_handles[1])
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "productTitle"))
            )
            product_details = {                
                "Product Name": "Name not available",
                "Product Price": "Price not available",
                "Product URL": driver.current_url,
                "Best Seller Rank": rank,
                "ASIN": asin,
                "REVIEWS": "REVIEWS not available",
                "Availability": "Availability not available",
                "Product Description": "Description not available",
                "Discount":"Discount not available",
                "MRP":"MRP not available",
                "ITEM MODEL NUMBER":"ITEM MODEL NUMBER not available",
                "MANUFACTURER":"MANUFACTURER not available",
                "PACKER":"PACKER not available",
                "WEIGHT":"WEIGHT not available",
                "DIMENSIONS":"DIMENSIONS not available",
                "BRAND NAME":"BRAND NAME not available",
                "RATING":"RATING not available",
                "MONTHLY PURCHASE":"MONTHLY PURCHASE not available",
                "Product URL": driver.current_url,
                "IMAGE URL":"IMAGE URL NOT AVAILABLE",
                "CATEGORY":cat,
                "Date First Available":"-",
                "SOLD BY":"-",
                "COMPETITOR":"-",
                "COUNTRY":"India",
                "FETCH_DATE":date.today(),
                "AMAZON URL":"amazon.in",
            }
            try:
                tables = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME,"prodDetTable")))
                try:
                    expandBtn = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "voyager-expand-all-btn")))
                    expandBtn.click()
                except Exception as e:
                    pass

                for table in tables:
                    rows = table.find_elements(By.XPATH,".//tr")
                    for row in rows:
                        th = row.find_element(By.TAG_NAME, "th").text.strip()
                        td = row.find_element(By.TAG_NAME, "td").text.strip()
                        if th.lower().replace(" ","") == 'DateFirstAvailable'.lower():
                            product_details["Date First Available"]=td
                        elif "weight" in th.lower().replace(" ",""):
                            product_details["WEIGHT"]=td
                        elif th.lower().replace(" ","") == "Itemmodelnumber".lower():
                            product_details["ITEM MODEL NUMBER"]=td
                        elif "dimension" in th.lower().replace(" ",""):
                            product_details["DIMENSIONS"]=td
            except Exception as e:
                pass

            try:
                competitor = driver.find_element(By.XPATH,'//*[@data-action="show-all-offers-display"]')
                match = re.search(r"\((\d+)\)", competitor.text)
                if match:
                    product_details["COMPETITOR"]=match.group(1)
                    print('Competitor = ',match.group(1))
            except NoSuchElementException:
                pass

            try:
                product_details["Product Name"] = driver.find_element(By.ID, "productTitle").text.strip()
            except NoSuchElementException:
                pass
            try:
                product_details["SOLD BY"] = driver.find_element(By.ID,"sellerProfileTriggerId").text.strip()
            except NoSuchElementException:
                pass
            try:
                product_details["Product Price"] = driver.find_element(By.XPATH, """//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[3]/span[2]/span[2]""").text.strip()
            except NoSuchElementException:
                product_details["Product Price"] = driver.find_element(By.CLASS_NAME, "a-price-whole").text.strip()
            try:
                product_details["REVIEWS"] = driver.find_element(By.ID, "acrPopover").get_attribute("title").strip()
            except NoSuchElementException:
                pass

            try:
                product_details["Availability"] = driver.find_element(By.ID, "availability").text.strip()
            except NoSuchElementException:
                pass

            try:
                html_content = driver.find_element(By.ID, "productDescription").get_attribute("innerHTML")
                soup = BeautifulSoup(html_content, "html.parser")
                product_details["Product Description"] = soup.get_text(strip=True)
            except NoSuchElementException:
                pass

            try:
                product_details["Discount"] = driver.find_element(By.CLASS_NAME, "savingPriceOverride").text.strip()
            except NoSuchElementException:
                pass

            try:
                html_content = driver.find_element(By.XPATH, """//*[@id="corePriceDisplay_desktop_feature_div"]/div[2]/span/span[1]/span[2]/span/span[1]""").get_attribute("innerHTML")
                soup = BeautifulSoup(html_content, "html.parser")
                product_details["MRP"] = soup.get_text(strip=True)
            except NoSuchElementException:
                pass    

           
            try:
                product_details["ITEM MODEL NUMBER"] = driver.find_element(By.XPATH, """//*[@id="detailBullets_feature_div"]/ul/li[4]/span/span[2]""").text.strip()
            except NoSuchElementException:
                pass

            try:
                product_details["MANUFACTURER"] = driver.find_element(By.XPATH, """//*[@id="detailBullets_feature_div"]/ul/li[5]/span/span[2]""").text.strip()
            except NoSuchElementException:
                pass

            try:
                product_details["PACKER"] = driver.find_element(By.XPATH, """//*[@id="detailBullets_feature_div"]/ul/li[6]/span/span[2]""").text.strip()
            except NoSuchElementException:
                pass

            try:
                product_details["WEIGHT"] = driver.find_element(By.XPATH, """//*[@id="detailBullets_feature_div"]/ul/li[7]/span/span[2]""").text.strip()
            except NoSuchElementException:
                pass

            try:
                product_details["DIMENSIONS"] = driver.find_element(By.XPATH, """//*[@id="detailBullets_feature_div"]/ul/li[8]/span/span[2]""").text.strip()
            except NoSuchElementException:
                pass

            try:
                product_details["BRAND NAME"] = driver.find_element(By.XPATH, """//*[@id="detailBullets_feature_div"]/ul/li[12]/span/span[2]""").text.strip()
            except NoSuchElementException:
                product_details["BRAND NAME"] = driver.find_element(By.ID, "productTitle").text.strip().split(" ")[0]
                pass

            try:
                product_details["RATING"] = driver.find_element(By.ID, "acrCustomerReviewText").text.strip()
            except NoSuchElementException:
                pass    

            try:
                product_details["MONTHLY PURCHASE"] = driver.find_element(By.ID, "social-proofing-faceout-title-tk_bought").text.strip()
            except NoSuchElementException:
                pass  

            try:
                img_element = driver.find_element(By.ID, "imgTagWrapperId")
                product_details["IMAGE URL"] = img_element.find_element(By.TAG_NAME, "img").get_attribute("src")
            except NoSuchElementException:
                pass

            try:
                product_details["CATEGORY"] = driver.find_element(By.XPATH, """//*[@id="CardInstanceo0zSTwG29wAaqvQf3wbkUg"]/div[2]/div[11]/a""").text.strip()
            except NoSuchElementException:
                pass
            
            product_details_list.append(product_details)
            print(f"Scraped product {rank}: {product_details}")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        except Exception as e:
            print(f"Error scraping product at rank {rank}: {e}")
            driver.save_screenshot(f"product_rank_{rank}_error.png")
            driver.close()
            driver.switch_to.window(driver.window_handles[0]) 

    return product_details_list

def save_to_csv(data, filename):
    """Save product data to a CSV file."""
    try:
        # Open the CSV file in write mode
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            # Write column headers (use keys from the first product)
            if data:
                headers = data[0].keys()
                writer.writerow(headers)

                # Write each product's details
                for product in data:
                    writer.writerow(product.values())

        print(f"Data saved to {filename}.")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")


def clean_data(file_path):
    try:
        data = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        data = pd.read_csv(file_path, encoding='ISO-8859-1')

    columns_needed = [
        "name", "price", "bsr", "asin", "review", "availability",
        "discount", "mrp", "rating", "monthlyPurchase", "category", "inventory",
        "competitor", "fetch date"
    ]

    # Select only the columns that exist in the data
    available_columns = [col for col in columns_needed if col in data.columns]
    data_filtered = data[available_columns]

    # Create 'subcategory' column by splitting the 'category' column at '~'
    if "category" in data_filtered.columns:
        data_filtered['category'] = data_filtered['category'].str.split('~', n=1).str[0]

    # Clean the 'reviews' column
    if "reviews" in data_filtered.columns:
        data_filtered["reviews"] = (data_filtered["reviews"]
            .str.replace("-", "0", regex=False)
            .str.replace(" out of 5 stars", "", regex=False)
            .str.strip()
        )

    # Clean the 'monthly_purchase' column
    if "monthly_purchase" in data_filtered.columns:
        data_filtered["monthly_purchase"] = (
            data_filtered["monthly_purchase"]
            .str.replace("-", "0", regex=False)
            .str.replace("+ bought in past month", "", regex=False)
            .str.replace("K", "000", regex=False)
            .str.strip()
        )

    # Clean the 'mrp' column to remove currency and keep only the numeric value
    if "mrp" in data_filtered.columns:
        data_filtered["mrp"] = data_filtered["mrp"].apply(
            lambda x: re.search(r"\d+(\.\d+)?", str(x)).group() if pd.notnull(x) and re.search(r"\d+(\.\d+)?", str(x)) else None
        )

    # Remove "%" from the 'discount' column
    if "discount" in data_filtered.columns:
        data_filtered["discount"] = data_filtered["discount"].str.replace("%", "", regex=False).str.strip()

    # Remove "-" from the 'rating' column
    if "rating" in data_filtered.columns:
        data_filtered["rating"] = data_filtered["rating"].str.replace("-", "0", regex=False).str.strip()

    # Ensure 'reviews' is present and handle missing column
    if "reviews" not in data_filtered.columns:
        data_filtered["reviews"] = None  

    # Save the cleaned data
    data_filtered.to_csv(file_path, index=False)
    print(f"Cleaned data saved to {file_path}")

def main():
    category_urls = {
        "https://www.amazon.in/gp/bestsellers/books/1318052031/ref=zg_bs_nav_books_1",
    }

    all_products = []
    index=0
    for key, value in category_urls.items():
        products = get_product_details_from_category_page(key,value)
        all_products.extend(products)
        index+=1
    save_to_csv(all_products, "amazon_category_products.csv")

    data_file = "amazon_category_products.csv"
    clean_data(data_file)

    driver.quit()


if __name__ == "__main__":
    main()

