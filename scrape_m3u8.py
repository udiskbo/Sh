import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests

# 网站基础URL和下载链接特定域名
base_url = "https://asian-bondage.com"
download_domain = "hotlink.cc"

# 直接定义的cookies（替换为实际的值）
cookies = {
    '__ddg1_': 'p9QSvVBQs5pL9wiaMXEX',
    'lang': '1',
    'aff': '9247',
    'xfsts': 'v49u4qvy4gmm6fn7',
    'login': 'udiskboot@hotmail.com',
    'rand': '1721554014',
    'current_file_id': '7495999'
}

def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def get_article_links(soup):
    article_links = [a['href'] for a in soup.find_all('a', href=True) if a.parent.name == 'h2' and 'entry-title' in a.parent.get('class', [])]
    return article_links

def get_download_links(article_url, download_domain):
    soup = get_soup(article_url)
    links = [a['href'] for a in soup.find_all('a', href=True)]
    download_links = [link for link in links if download_domain in link]
    return download_links

def get_next_page(soup):
    next_page = soup.find('a', class_='next page-numbers')
    if next_page:
        return next_page['href']
    return None

def get_m3u8_url(video_page_url):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    driver.get(video_page_url)

    for name, value in cookies.items():
        driver.add_cookie({'name': name, 'value': value})

    driver.refresh()
    time.sleep(5)  # 等待cookies生效

    try:
        # 尝试找到并点击播放按钮
        play_button = driver.find_element(By.CSS_SELECTOR, ".jw-video")
        actions = ActionChains(driver)
        actions.move_to_element(play_button).click().perform()
        time.sleep(10)  # 延长等待时间，确保视频加载和网络请求记录
    except Exception as e:
        print(f"未找到播放按钮: {e}")

    page_source = driver.page_source
    driver.quit()

    # 使用 BeautifulSoup 解析页面源码
    soup = BeautifulSoup(page_source, 'html.parser')
    for script in soup.find_all('script'):
        if 'm3u8' in script.text:
            try:
                m3u8_url = script.text.split('m3u8')[1].split('"')[1]
                return m3u8_url
            except IndexError as e:
                print(f"Error parsing m3u8 URL: {e}")
                return None
    return None

if __name__ == "__main__":
    current_page = f"{base_url}/page/1/"
    all_download_links = []
    max_pages = 5  # 抓取的最大页数
    current_page_num = 0

    while current_page and current_page_num < max_pages:
        soup = get_soup(current_page)
        article_links = get_article_links(soup)
        
        for article_link in article_links:
            download_links = get_download_links(article_link, download_domain)
            all_download_links.extend(download_links)
        
        print(f"抓取完毕: {current_page}")
        current_page = get_next_page(soup)
        current_page_num += 1

    with open('m3u8_links.txt', 'w') as file:
        for link in all_download_links:
            m3u8_url = get_m3u8_url(link)
            if m3u8_url:
                file.write(m3u8_url + "\n")
                print(f"找到m3u8链接: {m3u8_url}")
            else:
                print(f"未找到m3u8链接: {link}")
