from __future__ import unicode_literals
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *

#
#   Web Browser Class
class browser(QMainWindow):
    def __init__(self):
        super(browser, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        # Crear entorno de tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.closeTab)
        # Crear primera tab
        self.tab1 = QWidget()
        self.tabWebView = []
        self.lNameLine = []
        self.tabs.addTab(self.tab1, "New Tab")
        self.tab1UI(self.tab1)

        self.setWindowTitle("MuuExplorer")
        self.setCentralWidget(self.tabs)
        self.showMaximized()
        # Comando para nueva tab
        QShortcut(QKeySequence("Ctrl+T"), self, self.addTab)

    def addTab(self):
        tab = QWidget()
        self.tabs.addTab(tab, "New Tab")
        self.tab1UI(tab)

        index = self.tabs.currentIndex()
        self.tabs.setCurrentIndex(index + 1)
        # self.tabWebView[self.tabs.currentIndex()].load( QUrl('about:blank'))

    def goBack(self):
        index = self.tabs.currentIndex()
        self.tabWebView[index].back()

    def goNext(self):
        index = self.tabs.currentIndex()
        self.tabWebView[index].forward()

    def goRefresh(self):
        index = self.tabs.currentIndex()
        self.tabWebView[index].reload()

    def changePage(self):
        index = self.tabs.currentIndex()
        pageTitle = self.sender().title()[:15]
        self.tabs.setTabText(index, pageTitle)
        self.lNameLine[self.tabs.currentIndex()].setText(self.sender().url().url())

    def load_started(self):
        return

    def tab1UI(self, tabName):
        webView = QWebEngineView()

        backButton = QPushButton("")
        backIcon = QIcon()
        backIcon.addPixmap(QPixmap("back.svg"))
        backButton.setIcon(backIcon)
        backButton.setFlat(True)

        nextButton = QPushButton("")
        nextIcon = QIcon()
        nextIcon.addPixmap(QPixmap("next.svg"))
        nextButton.setIcon(nextIcon)
        nextButton.setFlat(True)

        refreshButton = QPushButton("")
        refreshIcon = QIcon()
        refreshIcon.addPixmap(QPixmap("refresh.svg"))
        refreshButton.setIcon(refreshIcon)
        refreshButton.setFlat(True)
        QShortcut(QKeySequence("F5"), self, self.goRefresh)

        backButton.clicked.connect(self.goBack)
        nextButton.clicked.connect(self.goNext)
        refreshButton.clicked.connect(self.goRefresh)

        self.newTabButton = QPushButton("+")
        self.destroyTabButton = QPushButton("-")
        self.tabWidget = QTabWidget()

        nameLine = QLineEdit()
        nameLine.returnPressed.connect(self.requestUri)

        tabGrid = QGridLayout()

        tabGrid.setContentsMargins(0, 0, 0, 0)

        navigationFrame = QWidget()
        navigationFrame.setMaximumHeight(32)

        navigationGrid = QGridLayout(navigationFrame)
        navigationGrid.setSpacing(0)
        navigationGrid.setContentsMargins(0, 0, 0, 0)
        navigationGrid.addWidget(backButton, 0, 1)
        navigationGrid.addWidget(nextButton, 0, 2)
        navigationGrid.addWidget(refreshButton, 0, 3)
        navigationGrid.addWidget(nameLine, 0, 4)

        tabGrid.addWidget(navigationFrame)

        webView = QWebEngineView()
        htmlhead = "<head><style>body{ background-color: #fff; }</style></head><body></body>";
        webView.setHtml(htmlhead)

        # webView.loadProgress.connect(self.loading)
        webView.loadFinished.connect(self.changePage)

        frame = QFrame()
        frame.setFrameStyle(QFrame.Panel)

        gridLayout = QGridLayout(frame);
        # gridLayout.setObjectName(QStringLiteral("gridLayout"));
        gridLayout.setContentsMargins(0, 0, 0, 0);
        gridLayout.addWidget(webView, 0, 0, 1, 1);
        frame.setLayout(gridLayout)

        self.tabWebView.append(webView)
        self.tabWidget.setCurrentWidget(webView)
        self.lNameLine.append(nameLine)
        tabGrid.addWidget(frame)
        tabName.setLayout(tabGrid)

    def tab2UI(self):
        vbox = QVBoxLayout()
        tbl1 = QTableWidget()
        tbl1.setRowCount(5)
        tbl1.setColumnCount(5)
        vbox.addWidget(tbl1)
        tbl1.setItem(0, 0, QTableWidgetItem("1"))  # row, col
        self.tab2.setLayout(vbox)

    def requestUri(self):
        if self.tabs.currentIndex() != -1:

            urlText = self.lNameLine[self.tabs.currentIndex()].text()

            ##########################
            # no protocol?
            if 'http' not in urlText:
                self.lNameLine[self.tabs.currentIndex()].setText('https://' + urlText)

            url = QUrl(self.lNameLine[self.tabs.currentIndex()].text())

            print(self.tabs.currentIndex())
            if url.isValid():
                self.tabWebView[self.tabs.currentIndex()].load(url)
            else:
                print("Url not valid")
        else:
            print("No tabs open, open one first.")

    def closeTab(self, tabId):
        print(tabId)
        del self.lNameLine[tabId]
        del self.tabWebView[tabId]
        self.tabs.removeTab(tabId)

# test webbrowser
def webbrowser():
    app = QApplication(sys.argv)
    ex = browser()
    ex.show()
    sys.exit(app.exec_())