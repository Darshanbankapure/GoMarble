# GoMarble
Develop an API server capable of extracting reviews information from any given product page (e.g., Shopify, Amazon). The API should dynamically identify CSS elements of reviews and handle pagination to retrieve all reviews.

# Steps to Follow

1. Install all dependencies - pip install -r requirements.txt
2. Replace the API key in the .env File
3. Run the code in terminal- Run app.py
4. Enter the website link in bash - curl "API_link"

   For example (Amazon Link) - curl "http://127.0.0.1:5000/api/reviews?page=https://www.amazon.in/Crocs-Brooklyn-Woven-Buckle-Sandal/dp/B0CR827JZ7/ref=sr_1_1?_encoding=UTF8&rps=1&s=shoes&sr=1-1&psc=1"

