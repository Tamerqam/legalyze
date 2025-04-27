# flask_search_judgments.py
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

app = Flask(__name__)

def search_judgments(keyword, law, article):
    base_url = "https://maqam.najah.edu/search/?"

    queries = {
        'nagog': f"{keyword} المادة {article} {law} نقض",
        'appeal': f"{keyword} المادة {article} {law} استئناف"
    }

    results = {}

    for type_, query in queries.items():
        query_string = urlencode({'q': query})
        search_url = base_url + query_string

        try:
            response = requests.get(search_url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            results[f'{type_}_decisions'] = []
            results[f'full_search_link_{type_}'] = search_url
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        decisions = []
        count = 0

        # تحديد جميع العناصر <a> التي تحتوي على رابط لـ /judgments/
        links = soup.select('ul.list-unstyled li.py-2.border-bottom a[href*="/judgments/"]')

        for link in links:
            href = link.get('href')
            strong_tag = link.find('strong')

            title = strong_tag.get_text(strip=True) if strong_tag else link.get_text(strip=True)

            if href and title:
                decisions.append({
                    'title': title,
                    'link': f"https://maqam.najah.edu{href}"
                })
                count += 1

            if count >= 3:
                break

        results[f'{type_}_decisions'] = decisions
        results[f'full_search_link_{type_}'] = search_url

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
