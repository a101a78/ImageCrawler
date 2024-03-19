import hashlib
import urllib.request


def downloader(src, folder_path, existing_images):
    try:
        image_data = urllib.request.urlopen(src).read()
        image_hash = hashlib.sha256(image_data).hexdigest()
        if image_hash not in existing_images:
            with open(f"{folder_path}/{image_hash}.jpg", 'wb') as file:
                file.write(image_data)
            existing_images.add(image_hash)
            return "SUCCESS"
        else:
            return "EXISTS"
    except Exception:
        return "FAIL"
