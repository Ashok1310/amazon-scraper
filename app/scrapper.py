import time
import requests
from pprint import pprint
from bs4 import BeautifulSoup
from selenium import webdriver



# First, create a new instance of the Chrome driver in headless mode
options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(options=options)

def get_page_urls(keywords,max_urls=None) -> list:
    try:
        url = f"https://www.amazon.in/s?k={keywords}"
        driver.get(url)
        soup =  BeautifulSoup(driver.page_source, "html.parser")

        span_tag = soup.find("span", class_="s-pagination-strip")
        if last_page_number := int(
            span_tag.find(
                'span', class_="s-pagination-item s-pagination-disabled"
            ).text
        ):
            if max_urls and last_page_number > max_urls:
                return [f"{url}&page={str(i)}" for i in range(1,int(max_urls)+1)]
            return [f"{url}&page={str(i)}" for i in range(1,last_page_number+1)]
        return []
    except Exception as e:
        print(f"Exception:{e}")
        return []
        


def get_product_page_urls(page_urls,max_urls=None,max_product=None) -> list:
    product_urls = []

    try:  
        for url in page_urls:
            driver.get(url)

            soup =  BeautifulSoup(driver.page_source, "html.parser")
            if h2_tags :=  soup.find_all("h2",class_="a-size-mini a-spacing-none a-color-base s-line-clamp-2"):
                if max_urls:
                    for i,h2 in enumerate(h2_tags):
                        if max_urls == i:
                            break
                        if a_tag := h2.find("a"):
                            href = a_tag.get("href")
                            product_urls.append(f"https://www.amazon.in{href}")
                else:
                    for h2 in h2_tags:
                        if a_tag := h2.find("a"):
                            href = a_tag.get("href")
                            product_urls.append(f"https://www.amazon.in{href}")
                if max_product is not None and max_product == len(product_urls):
                    return product_urls
            else:
                print("Product(s) urls didn't found.")
        return product_urls
    except Exception as e:
        print(f"Exception:{e}")
        return product_urls






def get_product_info(url):
    product_info = {}
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        product_title = soup.find("span", class_="a-size-medium product-title-word-break product-title-resize")
        product_discount_price = soup.find("span", class_="a-price-whole")
        product_discount_percent = soup.find("span",class_="a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage")
        is_in_deal_of_day = soup.find("span",class_="a-size-base dealBadgeSupportingText a-text-bold")

        actual_price_span = soup.find("span",class_="a-price a-text-price")
        product_actual_price  = actual_price_span.find("span",class_="a-offscreen")
        product_about = soup.find("ul",class_="a-unordered-list a-vertical a-spacing-mini")

        if product_title:
            product_info["product_title"] = product_title.text.strip()
        else:
            product_info["product_title"] = None

        if product_discount_price:
            product_info["product_discount_price"]   = product_discount_price.text.strip()
        else:
            product_info["product_discount_price"]  = None
        
        if product_discount_percent:
            product_info["product_discount_percent"] = product_discount_percent.text.strip()
        else:
            product_info["product_discount_percent"] = None
        
        if is_in_deal_of_day:
            product_info["is_in_deal_of_day"] = 1
        else:
            product_info["is_in_deal_of_day"] = 0
        
        if product_actual_price:
            product_info["product_actual_price"] = product_actual_price.text.strip()
        else:
            product_info["product_actual_price"] = None
        
        if product_about:
            product_info["product_about"] = product_about.text.strip()
        else:
            product_info["product_about"] = None

        return product_info
    
    except Exception as e:
        print(f"Exception:{e}")
        return product_info



def amazon_scrapper(keywords,max_page=None,max_product=None) -> list:
    page_urls = get_page_urls(keywords=keywords,max_urls=max_page)
    print(f"\nPages: {page_urls}")
    product_page_urls = get_product_page_urls(page_urls,max_urls=max_product,max_product=max_product)
    print(f"\nProducts: {len(product_page_urls)}")
    product_info_list = []
    for url in product_page_urls:
        if product_info := get_product_info(url):
            product_info_list.append(product_info)
    print(f"\nProduct info: {len(product_info_list)}")
    return product_info_list


# if __name__=="__main__":
#     products = amazon_scrapper(keyword='laptop',max_page=1,max_product=3)
#     print(products)
#     print(len(products))
