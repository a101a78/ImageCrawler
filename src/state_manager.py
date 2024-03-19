import threading

# 크롤링 중단을 위한 이벤트
stop_crawling = threading.Event()

# 저장된 이미지 수
_saved_images_count = 0
# 저장된 이미지 수를 위한 락
_count_lock = threading.Lock()


def increment_saved_images_count():
    global _saved_images_count
    with _count_lock:
        _saved_images_count += 1


def get_saved_images_count():
    with _count_lock:
        return _saved_images_count
