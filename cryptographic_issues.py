import codecs
from base64 import b64decode
from authentication import get_admin_session

def solve_cryptographic_challenges(server):
    print('\n== CRYPTOGRAPHIC CHALLENGES ==\n')
    session = get_admin_session(server)
    
    algorithm_confusion(server, session)
    # nested easter egg comes here
    
    print('\n== CRYPTOGRAPHIC CHALLENGES COMPLETE ==\n')


def algorithm_confusion(server, session):
    """
    Change the JWT encryption algo from RS256 to HS256.
    """
    try:
        from misc_jwt import solve_forged_signed_jwt
        solve_forged_signed_jwt(server, session)
    except Exception as e:
        print(f"Error algorithm confusion: {e}")
