from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import json
from openai import OpenAI

client = OpenAI(api_key="OPEN_API_KEY")

def clean_html(html_content):
    # Start cleaning from the first occurrence of the word "review"
    review_start_index = html_content.lower().find("review")
    if review_start_index == -1:
        return None  # If "review" is not found, return None

    soup = BeautifulSoup(html_content[review_start_index:], 'html.parser')

    # Remove unnecessary tags
    for tag in soup(['style', 'script', 'iframe', 'input', 'a', 'noscript', 'img', 'hr', 'video']):
        tag.decompose()

    # Get the cleaned HTML
    cleaned_html = str(soup)

    return cleaned_html

def get_css_selectors(html_content):
    
    prompt = f"""
    You are an expert in web scraping and HTML analysis. Analyze the following HTML content, extracted from a product reviews page, and identify the required CSS selectors:
    1. CSS selector for the container holding all reviews.
    2. CSS selectors for each field in a review:
       - Title
       - Body
       - Rating
       - Reviewer name
    3. CSS selector for pagination to move to the next page which can be written as see more reviews, next page or other pagination methods.
    4. Logic for determining the next page link if pagination is available.
    5. next_page_link should strictly contain links which navigate to the next page

    HTML Content (truncated for length):
    {html_content}


    veryy veryyy important, Strictly just respond as the json below in a json format and nothing else
    Strictly Respond in JSON format as follows and nothing else:
    {{"reviews_container": "CSS selector",
       "review_fields": {{"title": "CSS selector",
                         "body": "CSS selector",
                         "rating": "CSS selector",
                         "reviewer": "CSS selector"}},
       "pagination": "CSS selector",
       "next_page_link": "URL or selector logic"}}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in web scraping."},
                {"role": "user", "content": prompt}
            ]
        )
        result = response.choices[0].message.content.strip()
        print(result)
        
        if 'json' in result:
            result = result[8:-4]
        print(result)
        return json.loads(result)

    except Exception as e:
        print(f"Error during OpenAI API call: {e}")
        return None

def extract_reviews(page, selectors):
    reviews = []

    review_elements = page.query_selector_all(selectors["reviews_container"])
    for review in review_elements:
        title = review.query_selector(selectors["review_fields"]["title"])
        body = review.query_selector(selectors["review_fields"]["body"])
        rating = review.query_selector(selectors["review_fields"]["rating"])
        reviewer = review.query_selector(selectors["review_fields"]["reviewer"])

        reviews.append({
            "title": title.inner_text().strip() if title else "No Title",
            "body": body.inner_text().strip() if body else "No Body",
            "rating": rating.inner_text().strip() if rating else "No Rating",
            "reviewer": reviewer.inner_text().strip() if reviewer else "Anonymous"
        })

    return reviews

def handle_pagination(page, selectors):
    next_page_link = page.query_selector(selectors["next_page_link"])
    if next_page_link and next_page_link.is_enabled():
        next_page_link.click()
        page.wait_for_load_state("domcontentloaded")
        return True
    return False

def fetch_all_reviews(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        all_reviews = []
        try:
            page.goto(url)
            page.wait_for_load_state("domcontentloaded")

            # Extract HTML content and dynamically get CSS selectors
            html_content = page.content()
            cleaned_html = clean_html(html_content)
            if not cleaned_html:
                raise ValueError("Failed to clean HTML.")
            
            selectors = get_css_selectors(cleaned_html)
            while True:
                # Extract reviews from the current page
                reviews = extract_reviews(page, selectors)
                all_reviews.extend(reviews)

                # Handle pagination
                if not handle_pagination(page, selectors):
                    break

        except Exception as e:
            print(f"Error while fetching reviews: {e}")
        finally:
            browser.close()

    return {
        "reviews_count": len(all_reviews),
        "reviews": all_reviews
    }