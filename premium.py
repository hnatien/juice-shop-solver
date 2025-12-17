from authentication import get_admin_session
import json

def solve_premium_challenges(server):
    print('\n== PREMIUM CHALLENGES ==\n')
    session = get_admin_session(server)
    
    nft_challenges(server, session)
    
    print('\n== PREMIUM CHALLENGES COMPLETE ==\n')


def nft_challenges(server, session):
    """
    Access the NFT minting endpoint.
    """
    print('Accessing NFT endpoint...'),
    # Challenge: nftEndpoint
    # /api/Challenges/
    # Actually it's often a hidden route e.g. /nft-mint
    # Or just minting an NFT via API.
    # The challenge involves finding the hidden route.
    # Hint: "the feature is in beta".
    try:
        session.get('{}/nft'.format(server))
        session.get('{}/#/nft'.format(server))
        print('Success (maybe).')
    except: pass
