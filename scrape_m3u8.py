import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

# 网站基础URL和下载链接特定域名
base_url = "https://asian-bondage.com"
category_url = f"{base_url}/category/jinan-rope/"
download_domain = "hotlink.cc"

# 直接定义的cookies（替换为实际的值）
cookies = {
    '__ddg1_': 'CiFIMRaCUMhCWQXrdFjf',
    'lang': '1',
    'aff': '9247',
    'xfsts': '24ewfzqggnksv7wt',
    'login': 'udiskboot@hotmail.com',
    'rand': '1722056490',
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

def get_m3u8_url(video_page_url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    driver.get(video_page_url)

    # 添加cookies
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

    soup = BeautifulSoup(page_source, 'html.parser')
    for script in soup.find_all('script'):
        if 'm3u8' in script.text:
            try:
                m3u8_url = script.text.split('m3u8')[1].split('"')[0]
                return m3u8_url
            except IndexError:
                continue
    return None

if __name__ == "__main__":
    current_page_number = 1337  # 从最后一页开始
    all_m3u8_urls = []

    while current_page_number > 0:
        current_page = f"{category_url}page/{current_page_number}/"
        print(f"处理页面: {current_page}")
        soup = get_soup(current_page)
        article_links = get_article_links(soup)
        all_download_links = []

        for article_link in article_links:
            download_links = get_download_links(article_link, download_domain)
            all_download_links.extend(download_links)

        for link in all_download_links:
            m3u8_url = get_m3u8_url(link)
            if m3u8_url:
                print(f"找到 m3u8 链接: {m3u8_url}")
                all_m3u8_urls.append(m3u8_url)
            else:
                print(f"未找到 m3u8 链接: {link}")

        # 处理上一页
        current_page_number -= 1

    print(f"所有找到的 m3u8 链接: {all_m3u8_urls}")
