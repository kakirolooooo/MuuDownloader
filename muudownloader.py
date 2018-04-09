from __future__ import unicode_literals
import youtube_dl
from dropbox import DropboxOAuth2FlowNoRedirect
import dropbox
import pyperclip
import configparser
import sys
import traceback
import pickle
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from qtconsole.manager import QtKernelManager
from qtconsole.rich_jupyter_widget import RichJupyterWidget


# The ID of an installed kernel, e.g. 'bash' or 'ir'.
USE_KERNEL = 'python3'

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
        print('Done downloading, now converting...\n\n')
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
#
# Connect to dropbox
def connect_db():
    APP_KEY = "8b7lcrabzxhy9uz"
    APP_SECRET = "5xakxbps2e8a2dt"

    auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)

    authorize_url = auth_flow.start()
    print("1. Go to(already coppied in Ctrl + C): " + authorize_url)
    print("2. Click \"Allow\" (you might have to log in first).")
    print("3. Copy the authorization code.")
    #webbrowser()
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

#
#Check if logged in dropbox
def if_logged():
    try:
        user_token = config_reader()
        dbx = dropbox.Dropbox(user_token)
        print(dbx.users_get_current_account())
    except:
        print('Token invalido o fichero Config.ini no encontrado')
#
# Log into dropbox
def log_db():
    try:
        value = config_reader()
        if value != '':
            user_token = value
            dbx = dropbox.Dropbox(user_token)
            print(dbx.users_get_current_account())
        else:
            user_token = connect_db()
            config_writer(user_token)
        shared = {"user_token": user_token, "db_logged": True}
        fp = open("data.pkl", "wb")
        pickle.dump(shared, fp)
        fp.close()
    except:
        print("Token invalido o fichero Config.ini no encontrado")
        shared = {"user_token": "", "db_logged": False}
        fp = open("data.pkl", "wb")
        pickle.dump(shared, fp)
        fp.close()

def dw_single(user_token = None):
    shared = {"flag": 1}
    fp = open("data.pkl", "wb")
    pickle.dump(shared, fp)
    fp.close()

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
            s_dir = './downloads/' + carpeta + '/' + s_name

        if db_up == 1:
            try:
                dbx = dropbox.Dropbox(user_token)
                file = open(s_dir, "rb")
                dbx.files_upload(file.read(), '/' + s_name)
                shared_link_metadata = dbx.sharing_create_shared_link_with_settings('/' + s_name)
                print(shared_link_metadata.url)
                pyperclip.copy(shared_link_metadata.url)
            except:
                _, _, tb = sys.exc_info()
                traceback.print_tb(tb)  # Fixed format
                tb_info = traceback.extract_tb(tb)
                filename, line, func, text = tb_info[-1]
                print('An error occurred on line {} in statement {}'.format(line, text))

                print("Error subiendo a dropbox\n")
        print("We did it !\n")
    except:
        print(Exception)
        print("En algo la has cagado subnormal, que no es tan dificil chico.2 cositas, dos, DOS.\nVueve a empezar mongolo\n")

    shared = {"flag": 0}
    fp = open("data.pkl", "wb")
    pickle.dump(shared, fp)
    fp.close()

def dw_playlist():
    shared = {"flag": 1}
    fp = open("data.pkl", "wb")
    pickle.dump(shared, fp)
    fp.close()
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

    shared = {"flag": 0}
    fp = open("data.pkl", "wb")
    pickle.dump(shared, fp)
    fp.close()

def dw_sfast():
    shared = {"flag": 1}
    fp = open("data.pkl", "wb")
    pickle.dump(shared, fp)
    fp.close()
    try:
        url = pyperclip.paste()
        dir = 'downloads/%(title)s.%(ext)s'

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
            ydl.extract_info(url)

        print("We did it fast&loud !\n")

    except:
        print(Exception)
        print("En algo la has cagado subnormal, que no es tan dificil chico.2 cositas, dos, DOS.\nVueve a empezar mongolo\n")

    shared = {"flag": 0}
    fp = open("data.pkl", "wb")
    pickle.dump(shared, fp)
    fp.close()

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


###enviar texto de stdout a Qwidget
class OutLog:
    def __init__(self, edit, out, color=None):
        """(edit, out=None, color=None) -> can write stdout, stderr to a
        QTextEdit.
        edit = QTextEdit
        out = alternate stream ( can be the original sys.stdout )
        color = alternate color (i.e. color stderr a different color)
        """
        self.edit = edit
        self.out = out
        self.color = color

    def write(self, m):
        if self.color:
            tc = self.edit.textColor()
            self.edit.setTextColor(self.color)

        self.edit.moveCursor(QTextCursor.End)
        self.edit.insertPlainText(m)

        if self.color:
            self.edit.setTextColor(tc)

        if self.out:
            self.out.write(m)

class widgetconsole(QMainWindow):
    """A window that contains a single Qt console."""
    def __init__(self):
        super().__init__()
        self.jupyter_widget = self.make_console_widget()
        self.setCentralWidget(self.jupyter_widget)

    def make_console_widget(self):
        """Start a kernel, connect to it, and create a RichJupyterWidget to use it
        """
        kernel_manager = QtKernelManager(kernel_name=USE_KERNEL)
        kernel_manager.start_kernel()

        kernel_client = kernel_manager.client()
        kernel_client.start_channels()

        jupyter_widget = RichJupyterWidget()
        jupyter_widget.kernel_manager = kernel_manager
        jupyter_widget.kernel_client = kernel_client
        jupyter_widget.execute('import muudownloader')
        return jupyter_widget

    def shutdown_kernel(self):
        #print('Shutting down kernel...')
        self.jupyter_widget.kernel_client.stop_channels()
        self.jupyter_widget.kernel_manager.shutdown_kernel()

    def test(self):
        print('hola esto es una prueba')
        self.console.jupyter_widget.append_stream('vamo a vererererer')

#
# Muu Downloader GUI
#
class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()

        shared = {"flag": 0}
        fp = open("data.pkl", "wb")
        pickle.dump(shared, fp)
        fp.close()
        self.uflag = 0
        self.db_flag = 0
        self.user_token = None
        self.mview = QWidget()
        self.console = QWidget()
        self.console = widgetconsole()
        self.setCentralWidget(self.mview)
        self.menu()
        self.create_toolbar()
        self.initUI()
        self.console.jupyter_widget.append_stream('\n >>Welcome to MuuDownloader'
                                              'Use te buttons an follow the instructions on the console to do the job')

    def initUI(self):

        self.user_token = config_reader()
        if self.user_token != "" and self.user_token is not None:
            self.uflag = 1
            self.update_toolbar()

        grid = QGridLayout()

        btn = QPushButton('Button')
        btn.resize(btn.sizeHint())
        # btn.clicked.connect(muudownloader())

        textEdit = QTextEdit()
        textEdit.setGeometry(QRect(20, 200, 431, 241))
        textEdit.setObjectName("textEdit")

        #sys.stdout = OutLog(textEdit, sys.stdout)


        grid.addWidget(self.console, 6, 6)


        #grid.addWidget(textEdit,6,6)
        #grid.addWidget(btn, 4, 4)
        self.mview.setLayout(grid)
        self.resize(600, 300)
        self.setWindowTitle('MuuDownloader')
        self.setWindowIcon(QIcon('img/rocket.ico'))

    def menu(self):
        exitact = QAction('Exit', self)
        exitact.setShortcut('Ctrl+Q')
        exitact.triggered.connect(qApp.quit)

        d_sfast = QAction('Dfast', self)
        d_sfast.setShortcut('Ctrl+F')

        ftext = 'muudownloader.dw_sfast()'
        d_sfast.triggered.connect(lambda: self.handlele('muudownloader.dw_sfast()', fast=True))

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        actionsMenu = menubar.addMenu('&Actions')
        fileMenu.addAction(exitact)
        actionsMenu.addAction(d_sfast)

    def create_toolbar(self):
        #
        #   Agregar on load, carga automatica del login, leyendo fichero serializado + config
        #
        self.btn0 = QAction(QIcon('img/rocket.ico'), 'Download Single MP3', self)
        #btn0.setShortcut('Ctrl+Q')

        dw_single = 'muudownloader.dw_single()'

        print(self.user_token)
        print(dw_single)
        self.btn0.triggered.connect(lambda: self.handlele(dw_single))

        self.btn1 = QAction(QIcon('img/playlist.svg'), 'Download MP3 Playlist', self)
        self.btn1.triggered.connect(lambda: self.handlele('muudownloader.dw_playlist()'))

        self.btn2 = QAction(QIcon('img/dropbox.svg'), 'Connect to Dropbox', self)
        self.btn2.triggered.connect(lambda: self.handlele('muudownloader.log_db()', dropb=True))

        self.btn4 = QAction(QIcon('img/circular-arrow.svg'), 'Interrupt task and reset', self)
        self.btn4.triggered.connect(lambda: self.handlele('', reset=True))
        self.btn4.setShortcut('Ctrl+P')

        self.toolbar = self.addToolBar('Toolbar_menu')
        self.toolbar.addAction(self.btn0)
        self.toolbar.addAction(self.btn1)
        self.toolbar.addAction(self.btn2)
        self.toolbar.addAction(self.btn4)
        if self.uflag == 0:
            self.btn3 = QAction(QIcon('img/save.svg'), 'Save Dropbox conection for fut', self)
            self.btn3.triggered.connect(lambda: self.save_db_config())
            self.toolbar.addAction(self.btn3)

    def update_toolbar(self):
        try:
            self.toolbar.clear()
            self.btn0u = QAction(QIcon('img/rocket.ico'), 'Download Single', self)
            dw_single = 'muudownloader.dw_single("{}")'.format(self.user_token)
            self.btn0u.triggered.connect(lambda: self.handlele(dw_single))
            print(dw_single)
            self.toolbar.addAction(self.btn0u)
            self.toolbar.addAction(self.btn1)
            self.toolbar.addAction(self.btn2)
            self.toolbar.addAction(self.btn4)
            if self.uflag == 0:
                self.toolbar.addAction(self.btn3)
        except:
            print('se picio')

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def handlele(self, _str, dropb=False, fast=False, reset=False):
        #self.console.jupyter_widget.restart_kernel('restarting', True)
        fp = open("data.pkl", 'rb')
        shared = pickle.load(fp)
        flag = shared['flag']
        fp.close()
        if reset:
            self.console.jupyter_widget.confirm_restart = False
            self.console.jupyter_widget.restart_kernel('¿Terminar tarea y empezar la seleccionada?', True)
            self.console.jupyter_widget.execute('import muudownloader')
            self.console.jupyter_widget.execute('')
            self.console.jupyter_widget.execute('clear')
            self.console.jupyter_widget.execute('')
            self.console.jupyter_widget.clear()
            shared = {"flag": 0}
            fp = open("data.pkl", "wb")
            pickle.dump(shared, fp)
            fp.close()
        else:
            if flag == 0:
                if fast:
                    self.console.jupyter_widget.clear()
                    self.console.jupyter_widget.execute(_str)
                else:
                    self.console.jupyter_widget.clear()
                    self.console.jupyter_widget.execute(_str)
                    # if self.flag == 0:
                    #     self.console.jupyter_widget.clear()
                    #     self.flag = 1
                    #     self.console.jupyter_widget.execute(_str)
                    # else:
                    #     self.console.jupyter_widget.confirm_restart = False
                    #     self.console.jupyter_widget.restart_kernel('¿Terminar tarea y empezar la seleccionada?', True)
                    #     self.console.jupyter_widget.execute('import muudownloader')
                    #     self.console.jupyter_widget.execute('')
                    #     self.console.jupyter_widget.execute('clear')
                    #     self.console.jupyter_widget.execute('')
                    #     self.console.jupyter_widget.clear()
                    #     self.flag = 0
                    if dropb:
                        self.db_flag = 1

    #
    #Check if logged in dropbox
    def if_logged(self):
        try:
            self.user_token = config_reader()
            dbx = dropbox.Dropbox(self.user_token)
            print(dbx.users_get_current_account())
        except:
            print('Token invalido o fichero Config.ini no encontrado')
    #
    # Log into dropbox
    def log_db(self):
        try:
            value = config_reader()
            if value != '':
                self.user_token = value
                dbx = dropbox.Dropbox(self.user_token)
                print(dbx.users_get_current_account())
            else:
                self.user_token = connect_db()
                config_writer(self.user_token)


            shared = {"user_token": self.user_token}
            fp = open("data.pkl", "wb")
            pickle.dump(shared, fp)
            fp.close()

        except:
            self.console.jupyter_widget.execute_on_complete_input = True
            self.console.jupyter_widget.execute('print("Token invalido o fichero Config.ini no encontrado")')

    def save_db_config(self):
        if self.db_flag == 1:
            fp = open("data.pkl", 'rb')
            shared = pickle.load(fp)
            db_logged = shared['db_logged']
            fp.close()
            if db_logged:
                self.user_token = shared['user_token']
                self.update_toolbar()
            else:
                self.db_flag = 0
        else:
            mensajee = "la liaste esto no vale"
            print(mensajee)
            #self.console.jupyter_widget.include_output(mensajee)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainUI()
    ex.show()
    sys.exit(app.exec_())





