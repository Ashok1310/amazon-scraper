import time
import requests
from bs4 import BeautifulSoup
from pprint import pprint

def get_pagination_urls(keywords):
    url = f"https://www.amazon.in/s?k={keywords}"
    headers = {
    'Cookie': 'i18n-prefs=INR; session-id=257-7878759-1326968; session-id-time=2082787201l'
    }

    response = requests.request("GET", url, headers=headers)
    soup =  BeautifulSoup(response.content, "html.parser")

    # Find the <span> tag with class "s-pagination-strip"
    span_tag = soup.find("span", class_="s-pagination-strip")
    last_page_number = span_tag.find('span',class_="s-pagination-item s-pagination-disabled").text
    return [f"{url}&page={str(i)}" for i in range(1,int(last_page_number)+1)]


def get_item_urls(pagination_urls):
    headers = {
        'Cookie': 'i18n-prefs=INR; session-id=257-7878759-1326968; session-id-time=2082787201l'
    }

    page_itms = {}
    for i,url in enumerate(pagination_urls,start=1):
        item_urls = []
        print(f"{i}. Scrapping href of items form {url}")
        response = requests.request("GET", url, headers=headers)
        time.sleep(5)
        soup =  BeautifulSoup(response.content, "html.parser")


        # Find all <h2> tags on the page
        h2_tags = soup.find_all("h2")
        # Loop through each <h2> tag and extract its associated <a> tag's href attribute
        for h2 in h2_tags:
            if a_tag := h2.find("a"):
                href = a_tag.get("href")
                item_urls.append(f"https://www.amazon.in{href}")
        
        page_itms[f"page_{i}"]=item_urls

    pprint(page_itms)




if __name__=="__main__":
    pagination_urls =  get_pagination_urls(keywords='laptop')
    print(f"Total pages found: {len(pagination_urls)}")
    get_item_urls(pagination_urls)