# flask_search_judgments.py
# 🔹 سكربت الباحث القضائي المتطور عبر Selenium + Flask

from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from urllib.parse import urlencode
import time

app = Flask(__name__)

def search_judgments(keyword, law, article):
    base_url = "https://maqam.najah.edu/search/?"

    queries = {
        'nagog': f"{keyword} المادة {article} {law} نقض",
        'appeal': f"{keyword} المادة {article} {law} استئناف"
    }

    results = {}

    chrome_options = Options()
    chrome_options.add_argument('--headless')  # بدون واجهة
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    for type_, query in queries.items():
        query_string = urlencode({'q': query})
        search_url = base_url + query_string

        driver.get(search_url)
        time.sleep(3)  # انتظار تحميل النتائج

        decisions = []
        links = driver.find_elements(By.XPATH, "//ul[@class='list-unstyled']//li//a[contains(@href, '/judgments/')]")

        count = 0
        for link in links:
            href = link.get_attribute('href')
            title = link.text.strip()

            if href and title:
                decisions.append({
                    'title': title,
                    'link': href
                })
                count += 1
            if count >= 3:
                break

        results[f'{type_}_decisions'] = decisions
        results[f'full_search_link_{type_}'] = search_url

    driver.quit()

    return results

@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '').strip()
    law = request.args.get('law', '').strip()
    article = request.args.get('article', '').strip()

    if not keyword or not law or not article:
        return jsonify({"error": "❌ يجب توفير كلمة مفتاحية، اسم القانون، ورقم المادة"}), 400

    results = search_judgments(keyword, law, article)
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
