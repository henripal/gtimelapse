import gdata.photos.service
import oauth2client.client
import oauth2client.file.Storage
import webbrowser
import httplib2
import datetime.datetime
import datetime.timedelta
import sys


def oauth2login(client_secrets, credential_store, email):
    """ Authenticates using google web form and returns gdata object.

    This is a slightly updated and modified version of the code
    from user @legoktm available at
    https://github.com/legoktm/picasa/blob/master/picasa.py

    Parameters
    ----------
    client_secrets: string
        The client_secrets json file downloaded from the google app page
    credential_store: string
        The temporary filename where the user credentials will be stored
    email: string
        The email of the user whose photos are being retrieved

    Returns
    -------
    gd_client: gdata PhotosService
        The gdata photo service object post authentification.
    """
    scope = 'https://picasaweb.google.com/data/'
    user_agent = 'myapp'

    storage = oauth2client.file.Storage(credential_store)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        flow = oaut2client.client.flow_from_clientsecrets(
            client_secrets,
            scope=scope,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob')
        uri = flow.step1_get_authorize_url()
        webbrowser.open(uri)
        code = raw_input('Enter the authentication code: ').strip()
        credentials = flow.step2_exchange(code)
        storage.put(credentials)

    if (credentials.token_expiry - datetime.datetime.utcnow()) < datetime.timedelta(minutes=5):
        http = httplib2.Http()
        http = credentials.authorize(http)
        credentials.refresh(http)

    gd_client = gdata.photos.service.PhotosService(source=user_agent,
                                                   email=email,
                                                   additional_headers={'Authorization': 'Bearer %s' % credentials.access_token})

    return gd_client


def process_album(album_name, gd):
    """  Downloads an album from an opened gdata object

    Parameters
    ----------
    album_name: string
        The name of the album being downloaded
    gd: gdata object
        The previously created PhotosService object
    """
    albums = gd.GetUserFeed()
    for album in albums.entry:
        if album.title.text == album_name:
            album_toprocess = album

    print 'Starting %s' % (album_name)
    photos = gd.GetFeed(album_toprocess.GetPhotosUri()).entry
    for photo in photos:
        url = photo.GetMediaURL()
        media = gd.GetMedia(url)
        pname = photo.title.text
        data = media.file_handle.read()
        media.file_handle.close()
        sys.stdout.flush()
        out = open('./img/' + pname, 'wb')
        out.write(data)
        out.close()
        print 'Grabbed %s' % (pname)


def print_albums(gd):
    """ Utility function printing the name of all albums
    Parameters
    ----------
    gd: gdata object
        The previously created PhotosService object
    """
    albums = gd.GetUserFeed()
    for album in albums.entry:
        print 'title: %s, number of photos: %s, id: %s' % (album.title.text,
                                                           album.numphotos.text,
                                                           album.gphoto_id.text)


def main():
    gd = oauth2login('client_secrets.json', 'temp', 'henri.palacci@gmail.com')
    process_album('Pierre', gd)
    return gd
