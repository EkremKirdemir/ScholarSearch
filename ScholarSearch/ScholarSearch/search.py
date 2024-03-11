from spellchecker import SpellChecker
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from bs4 import BeautifulSoup
from pymongo import MongoClient
import random

client = MongoClient('mongodb+srv://admin:admin@search0.sof6xtt.mongodb.net/')
db = client['SearchScholar']
collection = db['Results']



url = 'https://www.semanticscholar.org/'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_argument("user-agent=whateverUserAgent")  
chrome_options.add_argument("--headless")
def getPublisherType():
    a = random.random()
    if a >=0.3:
        publisher_type = 'journal'
    elif 0.2<=a<0.3:
        publisher_type = 'conference'
    elif 0.1<=a<0.2:
        publisher_type = 'book'
    elif 0.05<=a<0.1:
        publisher_type = 'newspaper'
    else:
        publisher_type = 'web'
    return publisher_type

def getPublisherName(soup):
    url = soup.find('a', attrs={'class':'cl-paper-venue cl-paper-venue--paper-metadata'}).get('href')

    query_params = parse_qs(urlparse(url).query)

    return query_params.get('name', [None])[0]

def has_with_substring(tag, attr, text):
    if tag.has_attr(attr):
        attr_content = ' '.join(tag[attr]) if isinstance(tag[attr], list) else tag[attr]
        return text in attr_content
    return False

def writeSearchResults(soup,query,keywords_paper,expand,url):
    
    if soup.find(lambda tag: has_with_substring(tag, "data-test-id", "paper-detail-title")) is None:
        paper_name = 'unknown'
    else:
        paper_name = soup.find_all('h1', attrs={"data-test-id":"paper-detail-title"} )[0].text

    if soup.find(lambda tag: has_with_substring(tag, "class", "doi__link")) is None:
        paper_doi = 'unknown'
    else:
        paper_doi = soup.find_all('a', attrs={"class":"doi__link"} )[0].text

    if soup.find(lambda tag: has_with_substring(tag, "data-heap-nav", "citing-papers")) is None:
        paper_citations = 'unknown'
    else:
        paper_citations = soup.find_all('a', attrs={"data-heap-nav":"citing-papers"} )[0].text[:-10]

    if soup.find(lambda tag: has_with_substring(tag, "data-test-id", "reference")) is None:
        paper_references = 'unknown'
    else:            
        paper_references = []
        references = soup.find('div',attrs={'data-test-id':'reference'}).find_all('a', attrs={'data-heap-id':'citation_title'})
        for a in references:
            paper_references.append(a.text)

    if soup.find(lambda tag: has_with_substring(tag, "data-test-id", "paper-year")) is None:
        paper_date = 'unknown'
    else:
        paper_date = soup.find_all('span', attrs={"data-test-id":"paper-year"} )[0].text

    if soup.find(lambda tag: has_with_substring(tag, "class", "flex-paper-actions__item")) is None:
        paper_pdf = 'unknown'
    else:
        paper_pdf = soup.find(lambda tag: has_with_substring(tag, "class", "flex-paper-actions__item")).find('a').get('href')
        if paper_pdf.startswith("/reader"):
            paper_pdf = "https://www.semanticscholar.org" + paper_pdf
    
    if soup.find('ul', attrs={'class':'flex-row-vcenter paper-meta'}).find(lambda tag: has_with_substring(tag, "data-heap-id", "paper-meta-journal")) is None:
        paper_publisher_name = 'unknown'
    elif soup.find(lambda tag: has_with_substring(tag, "class", "flex-row-vcenter paper-meta")).find(lambda tag: has_with_substring(tag, "data-heap-id", "paper-meta-journal")):
        paper_publisher_name = soup.find('ul', attrs={'class':'flex-row-vcenter paper-meta'}).find('span', attrs={'data-heap-id':'paper-meta-journal'}).text
    else:
        paper_publisher_name = getPublisherName(soup)

    paper_publisher_type = getPublisherType()
    paper_authors = []

    if soup.find(lambda tag: has_with_substring(tag, "class", "author-list__link author-list__author-name")) is None:
        paper_authors = 'unknown'
    else:
        authors = soup.find_all('a', attrs={'class':'author-list__link author-list__author-name'})
        for a in authors:
            paper_authors.append(a.text)

    keywords_se = query
    keywords_paper = keywords_paper
    paper_url = url

    element = soup.find(lambda tag: has_with_substring(tag, 'class', 'paper-detail-page__tldr-abstract'))
    if element is None:
        paper_abstract = 'unknown'
    else:
            splitted = element.text.split('Abstract')[-1]
            if expand:
                paper_abstract = ' '.join(splitted.split()[:-1])
            else:
                paper_abstract = splitted  

    document = {
    "paper_name": paper_name,
    "doi": paper_doi,
    "paper_authors":paper_authors,
    "paper_publisher_type":paper_publisher_type,
    "paper_citations": paper_citations,
    "paper_references": paper_references,
    "paper_date":paper_date,
    "paper_pdf":paper_pdf,
    "paper_publisher_name":paper_publisher_name,
    "keywords_se":keywords_se,
    "keywords_paper":keywords_paper,
    "paper_url":paper_url,
    "paper_abstract":paper_abstract
}      
    collection.insert_one(document)
    print('done')


def search_and_parse(query):
    with webdriver.Chrome(options=chrome_options) as browser:
        browser.get(url)

        search_input = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )

        search_input.clear()
        search_input.send_keys(query)

        search_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test-id='search__form-submit']"))
        )

        search_button.click()
        browser.get(browser.current_url.replace('&sort=relevance','&sort=total-citations&pdf=true'))
        try:
            WebDriverWait(browser, 100).until(
            EC.presence_of_element_located((By.CLASS_NAME, "cl-paper-title"))
            )
        except:
            return

        html = browser.page_source
        
   
    page_soup = BeautifulSoup(html, 'html.parser')
    for i in range(len(page_soup.find_all('a', attrs={"data-test-id": "title-link"}))):
        a = page_soup.find_all('a', attrs={"data-test-id": "title-link"})[i]
        paper_url = a.get('href')
        with webdriver.Chrome(options=chrome_options) as browser2:
            browser2.get(url[:-1] + paper_url)
            WebDriverWait(browser2,10)
            try:
                expand_button = WebDriverWait(browser2, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Expand truncated text']"))
        )
                expand_button.click()
                expand = True
            except:
                expand = False
            try:
                 author_button = WebDriverWait(browser2, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test-id='author-list-expand']"))
        )
                 browser2.execute_script("arguments[0].click();", author_button)
                 author = True
            except:
                author = False
            html2 = browser2.page_source
            keywords_paper = page_soup.find_all('span', attrs={'class':'cl-paper-fos'})[i].text
            soup = BeautifulSoup(html2, 'html.parser')
            paper_url = browser2.current_url
            
            writeSearchResults(soup,query,keywords_paper,expand,paper_url)
    return page_soup

def searchCorrection(input_str):
    spell = SpellChecker()

    words = input_str.split()

    misspelled = spell.unknown(words)

    corrected_words = []
    for word in words:       
        corrected_word = spell.correction(word) if word in misspelled else word
        if corrected_word is not None:
            corrected_words.append(corrected_word)

    corrected_str = ' '.join(corrected_words)
    return corrected_str if corrected_words else input_str

# query = searchCorrection("deep learning")
# soup = search_and_parse(query)
# print("done")