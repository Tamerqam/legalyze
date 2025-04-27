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

        decisions = []
        try:
            response = requests.get(search_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # استخراج أول 3 روابط فقط من قرارات الأحكام القضائية
            for link in soup.find_all('a', href=True):
                href = link['href']
                title = link.get_text(strip=True)

                # فلترة ذكية: فقط الروابط التي تحتوي على "/judgments/" مع عنوان نصي
                if href.startswith("/judgments/") and title and "القضية رقم" in title:
                    decisions.append({
                        'title': title,
                        'link': f"https://maqam.najah.edu{href}"
                    })

                    if len(decisions) >= 3:
                        break

        except Exception as e:
            decisions = []

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
