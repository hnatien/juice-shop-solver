from users import login_jim, solve_user_challenges
from products import forge_coupon, manipulate_basket, deluxe_fraud
from feedback import solve_feedback_challenges
import requests

server = 'http://localhost:3000'

print("=== FAST FIX RUN ===")

# 1. User Fixes
# solve_user_challenges(server) # Skip long user challenges

# 2. Deluxe (Jim or Fresh)
# jim_session = login_jim(server) 
from users import register_new_user
fresh_session = register_new_user(server)
deluxe_fraud(server, fresh_session)

# 3. Product Fixes
# manipulate_basket needs a session (admin usually fine)
# But we need a valid basket. get_admin_session handles login.
from authentication import get_admin_session
admin_session = get_admin_session(server)

manipulate_basket(server, admin_session)
forge_coupon(server)

# 4. Feedback
solve_feedback_challenges(server)

print("=== DONE ===")
