from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

app = Flask(__name__)

def search_judgments(keyword, law, article):
    base_url = "https://maqam.najah.edu/search/"

    queries = {
        'nagog': f"{keyword} المادة {article} {law} نقض",
        'appeal': f"{keyword} المادة {article} {law} استئناف"
    }

    results = {}

    for type_, query in queries.items():
        query_string = urlencode({'q': query})
        search_url = base_url + '?' + query_string

        try:
            response = requests.get(search_url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            results[f'{type_}_decisions'] = []
            results[f'full_search_link_{type_}'] = search_url
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        decisions = []
        
        # 🧠 الحل الذكي هنا
        list_items = soup.select('ul.list-unstyled li.py-2.border-bottom a')

        for link in list_items[:3]:  # نأخذ أول 3 روابط فقط
            href = link.get('href')
            title = link.get_text(strip=True)

            if href and title:
                decisions.append({
                    'title': title,
                    'link': f"https://maqam.najah.edu{href}"
                })

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
