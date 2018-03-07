from __future__ import unicode_literals
import youtube_dl
from dropbox import DropboxOAuth2FlowNoRedirect
import dropbox
import pyperclip
import configparser

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'downloading':
        print(d['filename'], d['_percent_str'], d['_eta_str'])
    if d['status'] == 'finished':
        print('Done downloading, now converting...')
    if d['status'] == 'error':
        print('Error downloading')

def config_reader():
    config = configparser.ConfigParser()
    config.read('config.ini')

    user_token = config['Data']['user_token']
    return user_token


def config_writer(token):
    config = configparser.ConfigParser()
    config.read('config.ini')

    config.set('Data', 'user_token', token)

    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def menu():
    print("""
Menu:
1 | Single Song
2 | PlayList boi
7 | Am I logged in dropbox?
8 | DropboxLogin
9 | Salir""")


def connect_db():
    APP_KEY = "8b7lcrabzxhy9uz"
    APP_SECRET = "5xakxbps2e8a2dt"

    auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)

    authorize_url = auth_flow.start()
    print("1. Go to(already coppied in Ctrl + C): " + authorize_url)
    print("2. Click \"Allow\" (you might have to log in first).")
    print("3. Copy the authorization code.")
    pyperclip.copy(authorize_url)
    yeah = 0

    while yeah != 1:
        try:
            auth_code = input("Enter the authorization code here: \n").strip()
            oauth_result = auth_flow.finish(auth_code)
            yeah = 1
        except Exception:
            print("La has liado parda, vuelve a empezar\n")

    dbx = dropbox.Dropbox(oauth_result.access_token)

    print(dbx.users_get_current_account())

    return oauth_result.access_token


def dw_single(user_token):
    db_up = 0
    if user_token is not None:
        db_up = int(input("¿Quieres subir la cacion a dropbox? 1 | Si // 2 | No\n").strip())

    try:
        url = str(input("Introduce la url del video\n") + " ")
        carpeta = str(input("Introduce el nombre de la carpeta destino(sin espacios)\n"))
        if carpeta == '':
            dir = 'downloads/%(title)s.%(ext)s'
        else:
            dir = 'downloads/' + carpeta + '/%(title)s.%(ext)s'

        print("Leeeet's gooo")
        options = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': dir,
            'noplaylist': True,
            'nocheckcertificate': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'ffmpeg_location': './lib/',
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
        }

        with youtube_dl.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url)

        # pprint(info)
        s_name = info['title'] + '.mp3'
        if carpeta == '':
            s_dir = './downloads/' + s_name
        else:
            s_dir = './downloads/' + carpeta + s_name

        if db_up == 1:
            try:
                dbx = dropbox.Dropbox(user_token)
                file = open(s_dir, "rb")
                dbx.files_upload(file.read(), '/' + s_name)
                shared_link_metadata = dbx.sharing_create_shared_link_with_settings('/' + s_name)
                print(shared_link_metadata.url)
                pyperclip.copy(shared_link_metadata.url)
            except Exception:
                print(Exception)
                print("Error subiendo a dropbox\n")

        print("We did it !\n")

    except Exception:
        print(Exception)
        print("En algo la has cagado subnormal, que no es tan dificil chico.2 cositas, dos, DOS.\nVueve a empezar mongolo\n")


def dw_playlist():
    try:
        url = str(input("Introduce la url de la playlist\n"))
        carpeta = str(input("Introduce el nombre de la carpeta destino(sin espacios)\n").strip())
        options = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': 'downloads/' + carpeta + '/%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s',
            'noplaylist': False,
            'nocheckcertificate': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'ffmpeg_location': './lib/',
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
        }

        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([url])

        print("We did it !")
    except:
        print(
            "En algo la has cagado subnormal, que no es tan dificil chico.2 cositas, dos, DOS.\nVueve a empezar mongolo\n")


def muudownloader():
    print("""
    ************
    Youtube file downloader
    ************""")
    opc = 55
    user_token = None
    while opc != 9:
        try:
            menu()
            opc = int(input("Selecione Opcion\n"))
        except:
            print("Debes escoger una de las opciones\n")

        if opc == 1:
            dw_single(user_token)

        if opc == 2:
            dw_playlist()

        if opc == 7:
            try:
                user_token = config_reader()
                dbx = dropbox.Dropbox(user_token)
                print(dbx.users_get_current_account())
            except:
                print('Token invalido o fichero Config.ini no encontrado')

        if opc == 8:
            try:
                value = config_reader()
                if value != '':
                        user_token = value
                        dbx = dropbox.Dropbox(user_token)
                        print(dbx.users_get_current_account())
                else:
                    user_token = connect_db()
                    config_writer(user_token)
            except:
                print('Token invalido o fichero Config.ini no encontrado')


def test():
    config_writer('0xwdf23KA')
    value = config_reader()
    print(value)


if __name__ == '__main__':
    muudownloader()
    # test()
