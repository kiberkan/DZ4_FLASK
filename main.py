from flask import Flask, request, jsonify
import requests
from threading import Thread
import time
import argparse

#Запустите программу из командной строки:
#python main.py https://example.com/images/image1.jpg https://example.com/images/image2.png
#Откройте браузер и перейдите на адрес http://127.0.0.1:5000/download
#Отправьте POST-запрос с JSON-объектом, содержащим список URL-адресов:
#{
#  "urls": [
#    "https://example.com/images/image1.jpg",
#    "https://example.com/images/image2.png"
#  ]
#}

app = Flask(__name__)

def download_image(url, filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Ошибка скачивания {url}: {e}")
        return False

@app.route('/download', methods=['POST'])
def download_images():
    urls = request.json.get('urls')
    if not urls:
        return jsonify({"error": "Отсутствуют URL-адреса изображений"}), 400
    start_time = time.time()

    def download_thread(url):
        filename = url.split('/')[-1]
        success = download_image(url, filename)
        print(f"Изображение {filename} скачано за {time.time() - start_time:.2f} сек. ({'Успешно' if success else 'Ошибка'})")

    threads = [Thread(target=download_thread, args=(url,)) for url in urls]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    total_time = time.time() - start_time
    return jsonify({"message": f"Скачивание завершено за {total_time:.2f} сек."}), 200

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("urls", nargs="+", help="Список URL-адресов изображений")
    args = parser.parse_args()
    urls = args.urls
    app.run(debug=True)


