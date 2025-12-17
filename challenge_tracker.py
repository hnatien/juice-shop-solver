"""
Helper module to track solved challenges and skip them automatically.
"""
import requests


_solved_cache = None


def get_solved_challenges(server):
    """
    Fetch list of solved challenge keys from Juice Shop API.
    Returns a set of challenge keys (e.g., 'privacyPolicyChallenge', 'bullyChatbotChallenge')
    """
    global _solved_cache
    
    # Return cache if available
    if _solved_cache is not None:
        return _solved_cache
    
    try:
        r = requests.get(f'{server}/api/Challenges', timeout=5)
        if r.ok:
            challenges = r.json().get('data', [])
            _solved_cache = {c['key'] for c in challenges if c.get('solved')}
            return _solved_cache
    except Exception as e:
        print(f'Warning: Could not fetch solved challenges: {e}')
    
    # Return empty set on error
    return set()


def is_solved(server, challenge_key):
    """
    Check if a specific challenge is already solved.
    
    Args:
        server: Juice Shop URL
        challenge_key: Challenge key (e.g., 'privacyPolicyChallenge')
    
    Returns:
        True if challenge is solved, False otherwise
    """
    solved = get_solved_challenges(server)
    return challenge_key in solved


def refresh_cache():
    """
    Clear the solved challenges cache to force refresh on next call.
    """
    global _solved_cache
    _solved_cache = None


def skip_if_solved(server, challenge_key, task_name="task"):
    """
    Helper function to check and print skip message if challenge already solved.
    
    Args:
        server: Juice Shop URL
        challenge_key: Challenge key to check
        task_name: Human-readable name for logging
    
    Returns:
        True if should skip (already solved), False if should run
    """
    if is_solved(server, challenge_key):
        print(f'Skipping {task_name} (already solved)')
        return True
    return False
