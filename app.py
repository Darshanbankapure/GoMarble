from flask import Flask, request, jsonify
from scraper import fetch_all_reviews

app = Flask(__name__)

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    url = request.args.get('page')
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400
    
    reviews_data = fetch_all_reviews(url)
    return jsonify(reviews_data)

if __name__ == "__main__":
    app.run(debug=True)
