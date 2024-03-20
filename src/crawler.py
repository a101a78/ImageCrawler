import sys
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from color_formatter import log_with_color
from config import *
from state_manager import *


def init_driver(service):
    from selenium import webdriver
    driver = webdriver.Edge(service=service)
    driver.get("https://www.google.co.kr/imghp?hl=ko&ogbl")
    return driver


def search_for_images(driver, keyword):
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(keyword)
    search_box.send_keys(Keys.ENTER)

    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH, '//*[@id="islrg"]/div[1]/div[1]/a[1]/div[1]/img'))
    )


def scroll_and_collect_images(driver, existing_images, folder_path, failed_images):
    from image_handler import downloader
    image_urls = set()
    last_height = driver.execute_script("return document.body.scrollHeight")

    while not stop_crawling.is_set():
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(LOAD_DELAY)  # 스크롤 후 페이지 로드 대기

        # 새로운 페이지가 로드될 때마다 실패한 이미지 재시도
        for src in list(failed_images):
            retry_count = 0
            while retry_count < RETRY_LIMIT:
                result = downloader(src, folder_path, existing_images)
                log_with_color(result, result, src)
                if result == "SUCCESS":
                    increment_saved_images_count()
                    break
                elif result == "EXISTS":
                    break
                elif result == "FAIL":
                    retry_count += 1
                time.sleep(WAIT_DELAY)
            if retry_count == RETRY_LIMIT:
                log_with_color("FAIL", "RETRY-LIMIT-REACHED", src)
        failed_images.clear()

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("Finish the crawl because there are no more new images.")
            print(f"Total saved images: {get_saved_images_count()}")
            break  # 더 이상 새로운 이미지가 로드되지 않으면 종료
        last_height = new_height

        collect_images(driver, image_urls, existing_images, folder_path, failed_images)

    driver.close()
    sys.exit()


def collect_images(driver, image_urls, existing_images, folder_path, failed_images):
    from image_handler import downloader
    images = driver.find_elements(By.CSS_SELECTOR, 'img.rg_i.Q4LuWd')
    for image in images:
        src = None
        if stop_crawling.is_set():
            break
        try:
            driver.execute_script("arguments[0].click();", image)
            time.sleep(WAIT_DELAY)
            high_res_image = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, 'img.sFlh5c.pT0Scc.iPVvYb'))
            )
            src = high_res_image.get_attribute('src')
            if src and src.startswith('http') and src not in image_urls:
                image_urls.add(src)
                result = downloader(src, folder_path, existing_images)
                log_with_color(result, result, src)
                if result == "SUCCESS":
                    increment_saved_images_count()
        except Exception as e:
            if src:
                log_with_color("ERROR", "ERROR", type(e).__name__)
                failed_images.add(src)
