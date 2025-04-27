from flask import Flask, request, jsonify
import time
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

def search_judgments(materials, type_of_case=None):
    base_url = "https://maqam.najah.edu/search/"
    results = []

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    for material in materials:
        article = material.get('article')
        law = material.get('law')

        if not article or not law:
            continue

        # بناء استعلامين لكل مادة: نقض واستئناف
        for keyword in ["نقض", "استئناف"]:
            query = f"مادة {article} {law} {keyword}"
            search_url = base_url + '?' + urlencode({'q': query})

            driver.get(search_url)
            time.sleep(2)

            try:
                link_element = driver.find_element(By.XPATH, "//ul[@class='list-unstyled']//li[contains(@class, 'py-2 border-bottom')]//a")
                title = link_element.text.strip()
                href = link_element.get_attribute('href')

                if title and href:
                    results.append({
                        'search_target': f"مادة {article}",
                        'search_type': keyword,
                        'title': title,
                        'link': href
                    })

            except Exception as e:
                print(f"❌ لا توجد نتائج لـ: {query}")

    # إضافة بحث لنوع القضية إذا كان موجود
    if type_of_case:
        for keyword in ["نقض", "استئناف"]:
            query = f"{type_of_case} {keyword}"
            search_url = base_url + '?' + urlencode({'q': query})

            driver.get(search_url)
            time.sleep(2)

            try:
                link_element = driver.find_element(By.XPATH, "//ul[@class='list-unstyled']//li[contains(@class, 'py-2 border-bottom')]//a")
                title = link_element.text.strip()
                href = link_element.get_attribute('href')

                if title and href:
                    results.append({
                        'search_target': type_of_case,
                        'search_type': keyword,
                        'title': title,
                        'link': href
                    })

            except Exception as e:
                print(f"❌ لا توجد نتائج لـ: {query}")

    driver.quit()
    return results

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    materials = data.get('materials', [])
    type_of_case = data.get('type_of_case', None)

    if not materials:
        return jsonify({"error": "❌ يجب إرسال قائمة المواد"}), 400

    results = search_judgments(materials, type_of_case)
    return jsonify(results)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
