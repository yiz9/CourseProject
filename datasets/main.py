# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import urllib

options = Options()
options.headless = True
driver = webdriver.Chrome('./chromedriver', options=options)


def get_js_soup(url, driver):
    driver.get(url)
    res_html = driver.execute_script('return document.body.innerHTML')
    soup = BeautifulSoup(res_html, 'html.parser')  # beautiful soup object to be used for parsing html content
    return soup


# tidies extracted text
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
    # execute js on webpage to load faculty listings on webpage and get ready to parse the loaded HTML
    soup = get_js_soup(dir_url, driver)
    count = 0
    # BBC
    # for link_holder in soup.find_all('p',
    #                                  class_='css-1aofmbn-PromoHeadline e1f5wbog2'):  # get list of all <div> of class 'name'
    #     rel_link = link_holder.find('a')['href']  # get url
    #     # url returned is relative, so we need to add base url
    #     faculty_links.append(rel_link)

    #CNN
    for link_holder in soup.find_all('h4',
                                     class_='pb-10'):  # get list of all <div> of class 'name'
        rel_link = link_holder.find('a')['href']  # get url
        # url returned is relative, so we need to add base url
        faculty_links.append(rel_link)
        count += 1
        if count == 5:
            break
    print('-' * 20, 'Found {} faculty profile urls'.format(len(faculty_links)), '-' * 20)
    return faculty_links


dir_url = 'https://search.huffpost.com/search;_ylt=AwrJ61fjDsRfdKoA1wRsBmVH;_ylu=Y29sbwNiZjEEcG9zAzEEdnRpZAMEc2VjA3BhZ2luYXRpb24-?p=covid&pz=10&fr=huffpost&fr2=sb-top&bct=0&b=41&pz=10&bct=0&xargs=0'
faculty_links = scrape_dir_page(dir_url, driver)


print(faculty_links)


def scrape_faculty_page(fac_url, driver):
    soup = get_js_soup(fac_url, driver)
    bio = ''
    bio_url = ''
    ##BBC
    # profile_sec = soup.find_all('div', class_='css-83cqas-RichTextContainer e5tfeyi2')
    profile_sec = soup.find_all('div', class_='content-list-component yr-content-list-text text')

    if profile_sec == None:
        return
    bio_url += fac_url
    for i in profile_sec:
        bio += process_bio(i.get_text(separator=' '))
    # if profile_sec is not None:
    #     all_headers = profile_sec.find_all('h2')
    #     return all_headers
    #     faculty_last_name = all_headers[0].get_text().lower().split()[-1] #find faculty last name
    #     faculty_first_name = all_headers[0].get_text().lower().split()[0]
    #     homepage_txts = ['site','page',faculty_last_name,faculty_first_name]
    #     exceptions = ['course ','research','group','cs','mirror','google scholar']
    #     #find the homepage url and extract all text from it
    #     for hdr in all_headers:  #first find the required header
    #         if hdr.text.lower() == 'for more information':
    #             next_tag = hdr.find_next('li')
    #             #find <li> which has homepage url
    #             while next_tag is not None:
    #                 cand = next_tag.find('a')
    #                 next_tag = next_tag.next_sibling  #sibling means element present at the same level
    #                 try:
    #                     cand['href']
    #                 except:
    #                     continue
    #                 cand_text = cand.string
    #
    #                 if cand_text is not None and (any(hp_txt in cand_text.lower() for hp_txt in homepage_txts) and
    #                     not any(e in cand_text.lower() for e in exceptions)): #compare text to predefined patterns
    #                     bio_url = cand['href']
    #                     homepage_found = True
    #                     #check if homepage url is valid
    #                     if not(is_valid_homepage(bio_url,fac_url)):
    #                         homepage_found = False
    #                     else:
    #                         try:
    #                             bio_soup = remove_script(get_js_soup(bio_url,driver))
    #                         except:
    #                             print ('Could not access {}'.format(bio_url))
    #                             homepage_found = False
    #                     break


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



bio_urls_file = 'bio_urls5.txt'
bios_file = 'bios5.txt'
write_lst(bio_urls,bio_urls_file)
write_lst(bios,bios_file)

# Press the green button in the gutter to run the script.


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
