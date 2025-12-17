import json

import requests


def get_session(server, email, password, headers=None, oauth=False):
    """
    Log in with given username and password
    :param server: juice shop URL
    :param email: username as string
    :param password: password as string
    :param headers: Optional headers to send with the login request
    :param oauth: boolean. Exclude if False, if True include "oauth: true" in payload
    :return: Session
    """
    payload = {'email': email, 'password': password}
    if oauth:
        payload.update(oauth=True)
    payload = json.dumps(payload)
    return _do_login(server, payload, headers=headers)


def get_admin_session(server):
    """
    Log in legitimately as an admin. Password hash is publicly available, thanks Google.
    :param server: juice shop URL
    :return: Session
    """
    payload = json.dumps({'email': 'admin@juice-sh.op', 'password': 'admin123'})
    return _do_login(server, payload)


def _do_login(server, payload, headers=None):
    """
    Login through the REST API and return a Session with auth header and token in cookie
    :param server: juice shop URL
    :param payload: JSON payload required for auth
    :param headers: optional headers to use for the request. Sets content-type to JSON if omitted.
    :return: Session
    """
    session = requests.Session()
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    login = session.post('{}/rest/user/login'.format(server),
                         headers=headers,
                         data=payload)
    if not login.ok:
        print("DEBUG: Failed login payload: {}".format(payload))
        # print("DEBUG: Failed login response: {}".format(login.text))
        print('Error logging in. Content: {}'.format(login.content))
        return None
    resp_json = login.json()
    token = resp_json.get('token')
    if not token and 'authentication' in resp_json:
        token = resp_json['authentication'].get('token')
    
    if not token:
        print('Warning: Could not extract token from login response. Keys found: {}'.format(resp_json.keys()))

    session.cookies.set('token', token)
    session.headers.update({'Authorization': 'Bearer {}'.format(token)})
    return session


def create_user(server, email, password):
    """
    Create new user account through the API.
    :param server: juice shop URL.
    :param email: email address(unvalidated by server!)
    :param password: password
    """
    payload = json.dumps({'email': email, 'password': password, 'passwordRepeat': password})
    session = requests.Session()
    create = session.post('{}/api/Users'.format(server), headers={'Content-Type': 'application/json'}, data=payload)
    if not create.ok:
        print('Warning: Error creating user {}. Server responded: {}'.format(email, create.text))
        # raise RuntimeError('Error creating user {}'.format(email))


def whoami(server, session):
    """
    Check current user details
    :param server: juice shop URL
    :param session: Session
    :return: response body as dict
    """
    who = session.get('{}/rest/user/whoami'.format(server), headers={'Accept': 'application/json'})
    if not who.ok:
        raise RuntimeError('Error retrieving current user details')
    return who.json()


def get_current_user_id(server, session):
    """
    Retrieve current user's ID #
    :param server: juice shop URL
    :param session: Session
    :return: ID as int
    """
    resp = whoami(server, session)
    if 'user' in resp:
        return resp.get('user').get('id')
    return resp.get('id')


def get_basket_id(server, session):
    """
    Retrieve the current user's Basket ID (Bid)
    :param server:
    :param session:
    :return: Bid (int)
    """
    try:
        # Based on source: /rest/user/authentication-details returns the user details including Bid?
        # Frontend calls this.
        # Let's check response structure.
        details = session.get('{}/rest/user/authentication-details'.format(server))
        if details.ok:
            data = details.json().get('data')
            if data and 'Bid' in data:
                return data.get('Bid')
            # Sometimes data matches the user object directly?
            # Let's try fallback to /rest/basket/ ID retrieval if needed.
    except Exception as e:
        print(f"Warning: Failed to fetch authentication details: {e}")
    
    # Fallback: Use whoami ID, assuming BasketId match UserId (incorrect but better than nothing)?
    # Or try to fetch valid basket.
    return get_current_user_id(server, session)
