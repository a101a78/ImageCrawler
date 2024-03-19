import os
import threading

import keyboard
from selenium.webdriver.edge.service import Service

from config import stop_crawling
from crawler import init_driver, search_for_images, scroll_and_collect_images


def monitor_stop():
    print("To stop the crawl, type 'q' and press Enter.")
    keyboard.wait('q')
    stop_crawling.set()
    print("Interrupted by user input.")


def save_image(keyword, folder_path="images"):
    # 이미지 저장 폴더 생성
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    failed_images = set()  # 다운로드에 실패한 이미지 URL 저장

    # 폴더 내의 기존 이미지 파일 이름들을 해시값으로 변환하여 저장
    existing_images = {file_name.split('.')[0] for file_name in os.listdir(folder_path)}

    service = Service(executable_path="msedgedriver.exe")
    driver = init_driver(service)
    search_for_images(driver, keyword)
    scroll_and_collect_images(driver, existing_images, folder_path, failed_images)


if __name__ == "__main__":
    keyword = input("Enter keywords for the images you want to search for: ")

    # 사용자 입력 모니터링을 위한 스레드 시작
    stop_thread = threading.Thread(target=monitor_stop)
    stop_thread.start()

    save_image(keyword)
