from authentication import get_admin_session
from browser import solve_browser_challenges
from feedback import solve_feedback_challenges
from filehandling import solve_file_handling_challenges
from misc import solve_misc_challenges
from products import solve_product_challenges
from users import solve_user_challenges
from security_misconfiguration import solve_security_misconfiguration_challenges
from cryptographic_issues import solve_cryptographic_challenges
from advanced import solve_advanced_challenges
from premium import solve_premium_challenges

if __name__ == '__main__':
    server = 'http://localhost:3000'
    session = get_admin_session(server)
    
    try: solve_file_handling_challenges(server)
    except Exception as e: print(f"File handling failed: {e}")

    try: solve_user_challenges(server)
    except Exception as e: print(f"User challenges failed: {e}")

    try: solve_feedback_challenges(server)
    except Exception as e: print(f"Feedback challenges failed: {e}")

    try: solve_product_challenges(server)
    except Exception as e: print(f"Product challenges failed: {e}")

    try: solve_misc_challenges(server)
    except Exception as e: print(f"Misc challenges failed: {e}")

    try: solve_security_misconfiguration_challenges(server)
    except Exception as e: print(f"Security challenges failed: {e}")

    try: solve_cryptographic_challenges(server)
    except Exception as e: print(f"Crypto challenges failed: {e}")

    # Selenium-based - comment out the below if you don't have the Chromedriver set up.
    try:
        solve_browser_challenges(server)
    except Exception as e:
        print(f"Browser challenges failed: {e}")

    try: solve_advanced_challenges(server)
    except Exception as e: print(f"Advanced challenges failed: {e}")

    try: solve_premium_challenges(server)
    except Exception as e: print(f"Premium challenges failed: {e}")
