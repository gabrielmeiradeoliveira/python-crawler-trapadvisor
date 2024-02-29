import time
import random
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_local_info(soup):
    try:
        name = soup.find('h1', {'class': 'HjBfq'}).text
    except AttributeError:
        name = None

    try:
        phone = soup.find('a', {'class': 'yEWoV'}).text
    except AttributeError:
        phone = None

    try:
        address = soup.find('span', {'class': 'yEWoV'}).text
    except AttributeError:
        address = None

    try:
        cuisine_div = soup.find('div', {'class': 'UrHfr'}).find('div', text='COZINHAS')
        cuisine = cuisine_div.find_next_sibling('div').text
    except AttributeError:
        cuisine = None

    try:
        price_div = soup.find('div', {'class': 'UrHfr'}).find('div', text='FAIXA DE PREÇO')
        price = price_div.find_next_sibling('div').text
    except AttributeError:
        price = None

    try:
        total_reviews = soup.find('span', {'class': 'AfQtZ'}).text.split()[0].replace('.', '')
    except AttributeError:
        total_reviews = None

    try:
        average_rating = soup.find('span', {'class': 'ZDEqb'}).text
    except AttributeError:
        average_rating = None

    return {
        'name': name,
        'address': address,
        'phone': phone,
        'cuisine': cuisine,
        'price': price,
        'total_reviews': total_reviews,
        'average_rating': average_rating,
    }

def get_reviews(soup):
    reviews = []
    for review in soup.find_all('div', {'class': 'review-container'}):
        rating = review.find('span', {'class': 'ui_bubble_rating'})['class'][1].split('_')[-1]
        title = review.find('span', {'class': 'noQuotes'}).text
        content = review.find('p', {'class': 'partial_entry'}).text
        date = review.find('span', {'class': 'ratingDate'})['title']
        reviews.append({'rating': rating, 'title': title, 'content': content, 'date': date})
    return reviews

def scrape_page(url):
    driver.get(url)
    time.sleep(random.randint(5, 10))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup

def main():
    locais = []
    numero_pagina = 0
    try:
        while numero_pagina <= 10: #selecione o numero de páginas que deseja percorrer - 10 em 10
            url = f'https://www.tripadvisor.com.br/Search?geo=303441&q=restaurante&queryParsed=true&searchSessionId=0011633f21f0c492.ssid&searchNearby=false&sid=28B8593E5467463C9F037D6A034A5E081680103846830&blockRedirect=true&rf=4&ssrc=m&o={numero_pagina}'
            soup = scrape_page(url)
            local_links = [link['href'] for link in soup.find_all('a', {'class': 'review_count'})]

            for link in local_links:
                soup = scrape_page('https://www.tripadvisor.com.br' + link)
                local_info = get_local_info(soup)
                local_info['reviews'] = get_reviews(soup)
                locais.append(local_info)

            numero_pagina += 30

        with open('_locais.json', 'w', encoding='utf-8') as f:
            json.dump(locais, f, ensure_ascii=False)
    except Exception as e:
        print(e)
    finally:
        driver.quit()

if __name__ == "__main__":
    options = webdriver.FirefoxOptions()
    options.add_argument('start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-popup-blocking')
    driver = webdriver.Firefox(options=options)
    main()
