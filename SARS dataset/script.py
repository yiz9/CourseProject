from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re


options = Options()
options.headless = True
driver = webdriver.Chrome('./chromedriver', options=options)


def get_js_soup(url, driver):
    driver.get(url)
    res_html = driver.execute_script('return document.body.innerHTML')
    soup = BeautifulSoup(res_html, 'html.parser')  # beautiful soup object to be used for parsing html content
    return soup


def process_bio(bio):
    bio = bio.encode('ascii', errors='ignore').decode('utf-8')  # removes non-ascii characters
    bio = re.sub('\s+', ' ', bio)  # repalces repeated whitespace characters with single space
    return bio


def remove_script(soup):
    for script in soup(["script", "style"]):
        script.decompose()
    return soup


def scrape_dir_page(dir_url, driver):
    print('-' * 20, 'Scraping directory page', '-' * 20)
    faculty_links = []

    soup = get_js_soup(dir_url, driver)
    count = 0
    for link_holder in soup.find_all('p',
                                     class_='css-1uw1j0b-PromoHeadline e1f5wbog2'):  # get list of all <div> of class 'name'
        rel_link = link_holder.find('a')['href']  # get url
        faculty_links.append(rel_link)

    # CNN
    # for link_holder in soup.find_all('h4',
    #                                  class_='pb-10'):  # get list of all <div> of class 'name'
    #     rel_link = link_holder.find('a')['href']  # get url
    #     # url returned is relative, so we need to add base url
    #     faculty_links.append(rel_link)
    #     count += 1
    #     if count == 5:
    #         break
    print('-' * 20, 'Found {} faculty profile urls'.format(len(faculty_links)), '-' * 20)
    return faculty_links


dir_url = 'https://www.bbc.co.uk/search?q=SARS+china&page=16'
faculty_links = scrape_dir_page(dir_url, driver)


print(faculty_links)


def scrape_faculty_page(fac_url, driver):
    soup = get_js_soup(fac_url, driver)
    bio = ''
    bio_url = ''
    #profile_sec = soup.find_all('div', class_='css-83cqas-RichTextContainer e5tfeyi2')
    profile_sec = soup.find_all('p')
    if profile_sec == None:
        return
    bio_url += fac_url
    for i in profile_sec:
        bio += process_bio(i.get_text(separator=' '))

    return bio_url, bio


bio_urls, bios = [],[]
tot_urls = len(faculty_links)
for i,link in enumerate(faculty_links):
    print ('-'*20,'Scraping faculty url {}/{}'.format(i+1,tot_urls),'-'*20)
    bio_url,bio = scrape_faculty_page(link,driver)
    print(bio_url)
    if bio.strip()!= '' and bio_url.strip()!='':
        bio_urls.append(bio_url.strip())
        bios.append(bio)
driver.close()


def write_lst(lst, file_):
    with open(file_, 'w') as f:
        for l in lst:
            f.write(l)
            f.write('\n')



bio_urls_file = 'sars_url1.txt'
bios_file = 'sars1.txt'
write_lst(bio_urls,bio_urls_file)
write_lst(bios,bios_file)