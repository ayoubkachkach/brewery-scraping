import requests

from selenium import webdriver
import pandas as pd
import re
import time
import os
import time
from pathlib import Path

import lxml

def extract_info(brewery):
    fst_or_none = lambda l: (l or ['N/A'])[0]
    m = re.search('Type:  ([a-zA-Z]+)', ' '.join(brewery.xpath('descendant-or-self::*//text()')))
    brewery_type = m.group(1).strip().upper() if m else 'N/A'
    return {
        'Name': fst_or_none(brewery.xpath('descendant-or-self::*[@itemprop="name"]/text()')).strip(),
        'Address': fst_or_none(brewery.xpath('descendant-or-self::*[@itemprop="streetAddress"]/text()')).strip(),
        'City': fst_or_none(brewery.xpath('descendant-or-self::*[@itemprop="addressLocality"]/text()')).strip(),
        'State': fst_or_none(brewery.xpath('descendant-or-self::*[@itemprop="addressRegion"]/text()')).strip(),
        'Zip_code': fst_or_none(brewery.xpath('descendant-or-self::*[@itemprop="address"]/p[2]/text()[2]')).strip(),
        'Type': brewery_type,
        'Website': fst_or_none(brewery.xpath('descendant-or-self::*[@itemprop="image"]/@href')).strip()
    }

    

if __name__ == '__main__':
    os.environ['PATH'] += f':{str(Path().resolve())}'
    browser = webdriver.Firefox('.')
    browser.set_window_size(1900,1800)

    browser.get('https://www.brewersassociation.org/directories/breweries/')
    time.sleep(5)
    # Click on "Only Independent Craft" button to get all breweries
    elem = browser.find_element_by_xpath('//*[@id="craft-toggle"]')
    browser.execute_script("arguments[0].click();", elem)

    time.sleep(5)
    info = 'company-content' 
    breweries = browser.find_elements_by_class_name(info)
    breweries_info = [extract_info(brewery) for brewery in breweries]
    print(len(breweries_info))

    # Exhaust scrolling
    past_height = 0
    while True:
        # Scroll
        browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(2)
        new_height = browser.execute_script("return document.body.scrollHeight;")
        if new_height == past_height:
            break
   
        past_height = new_height

    html = browser.page_source
    cleaner = lxml.html.clean.Cleaner(javascript=True, page_structure=False, style=False)
    html = cleaner.clean_html(html)

    page = lxml.html.fromstring(html)

    breweries = page.xpath('//*[@class="company-content"]')
    breweries_info = [extract_info(brewery) for brewery in breweries]

    df = pd.DataFrame(breweries_info)
    df.to_csv('breweries.csv')