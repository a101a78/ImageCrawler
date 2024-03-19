import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

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
                if result == "SUCCESS":
                    print(f"[RETRY-SUCCESS] {src}")
                    increment_saved_images_count()
                    break
                elif result == "EXISTS":
                    print(f"[RETRY-EXISTS] {src}")
                    break
                elif result == "FAIL":
                    print(f"[RETRY-FAIL] {src}")
                    retry_count += 1
                time.sleep(WAIT_DELAY)
            if retry_count == RETRY_LIMIT:
                print(f"[RETRY-LIMIT-REACHED] {src}")
        failed_images.clear()

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("Finish the crawl because there are no more new images.")
            print(f"Total saved images: {get_saved_images_count()}")
            break  # 더 이상 새로운 이미지가 로드되지 않으면 종료
        last_height = new_height

        collect_images(driver, image_urls, existing_images, folder_path, failed_images)

    driver.close()


def collect_images(driver, image_urls, existing_images, folder_path, failed_images):
    from image_handler import downloader
    current_image_count = len(image_urls)
    images = driver.find_elements(By.CSS_SELECTOR, 'img.rg_i.Q4LuWd')
    for index, image in enumerate(images):
        if stop_crawling.is_set():
            break
        if index < current_image_count:
            continue
        try:
            driver.execute_script("arguments[0].click();", image)
            time.sleep(WAIT_DELAY)
            high_res_image = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, 'img.sFlh5c.pT0Scc.iPVvYb'))
            )
            src = high_res_image.get_attribute('src')
            if src.startswith('http') and src not in image_urls:
                image_urls.add(src)
                result = downloader(src, folder_path, existing_images)
                if result == "SUCCESS":
                    print(f"[SUCCESS] {src}")
                    increment_saved_images_count()
                elif result == "EXISTS":
                    print(f"[EXISTS] {src}")
                elif result == "FAIL":
                    print(f"[FAIL] {src}")
        except Exception as e:
            print(f"[ERROR] {type(e).__name__}")
            failed_images.add(src)
