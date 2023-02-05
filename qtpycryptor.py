import os
import sys
import time
import base64
import hashlib
import binascii
#from crypto.cipher import AES
from Crypto.Cipher import AES #from pycryptodome package
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import re
import pdb #for debugging line by line

class Pycryptor:
    
    """
QTPycryptor 1.0.1

A simple text encryption script
    """
    
    def mainGui(self): #This is the main window that holds the primary widgets
        app = QApplication(sys.argv)
    
        #Main window
        self.mainWin = QMainWindow()
        self.mainWin.setWindowTitle('QTPycryptor - Text Encryption')
        self.mainWin.setGeometry(200,200,500,825)
        self.mainWin.setFixedSize(self.mainWin.size())
        self.mainWin.show()

        #Textbox
        self.dispText = QTextEdit(self.mainWin)
        self.dispText.setGeometry(12,32,475,600)
        self.dispText.setReadOnly(True)
        #self.dispText.setTextInteractionFlags(Qt.NoTextInteraction)
        pal1 = self.dispText.viewport().palette()
        pal1.setColor(self.dispText.viewport().backgroundRole(), QColor(200,200,200))
        self.dispText.viewport().setPalette(pal1)
        self.dispText.show()

        #Menu bar
        mainMenu = self.mainWin.menuBar()
        mainMenu.setNativeMenuBar(False)
        #File Menu
        fileMenu = mainMenu.addMenu('&File')
        openFileButton = QAction(QIcon(),'Open File',self.mainWin)
        openFileButton.setShortcut('Ctrl+O')
        openFileButton.setStatusTip('Open a text file')
        openFileButton.triggered.connect(self.openFile)
        saveFileButton = QAction(QIcon(),'Save',self.mainWin)
        saveFileButton.setShortcut('Ctrl+S')
        saveFileButton.setStatusTip('Save the currently displayed text into a file')
        saveFileButton.triggered.connect(self.saveFile)
        fileMenu.addAction(openFileButton)
        fileMenu.addAction(saveFileButton)
        #Options
        optionMenu = mainMenu.addMenu('&Options')
        findTextButton = QAction(QIcon(),'Find Text',self.mainWin)
        findTextButton.setShortcut('Ctrl+F')
        findTextButton.setStatusTip('Search for a particular string in the text window')
        findTextButton.triggered.connect(self.searchPopup)
        optionMenu.addAction(findTextButton)
        #'About'
        aboutMenu = mainMenu.addMenu('A&bout')
        helpButton = QAction(QIcon(),'&Help',self.mainWin)
        helpButton.setShortcut('F4')
        helpButton.triggered.connect(self.helpPopup)
        aboutMenu.addAction(helpButton)
    
        #Textbox for log
        self.dispLog = QTextEdit(self.mainWin)
        self.dispLog.setReadOnly(True)
        self.dispLog.setGeometry(12,642,475,100)
        self.dispLog.setTextInteractionFlags(Qt.NoTextInteraction)
        pal2 = self.dispLog.viewport().palette()
        pal2.setColor(self.dispLog.viewport().backgroundRole(), QColor(0,0,0))
        self.dispLog.viewport().setPalette(pal2)
        self.dispLog.setTextColor(QColor(0,250,0))
        self.dispLog.show()
    
        #Text input for key
        #hash_key_label = QLabel(self.mainWin)
        #hash_key_label.setAlignment(Qt.AlignLeft)
        #hash_key_label.setText('Private key:')
        #hash_key_label.setGeometry(12,750,100,20)
        #hash_key_label.show()
    
        self.hash_key_edit = QLineEdit(self.mainWin)
        #self.hash_key_edit.setGeometry(12,770,200,27)
        self.hash_key_edit.setGeometry(12,755,200,27)
        self.hash_key_edit.setEchoMode(QLineEdit.Password)
        self.hash_key_edit.setPlaceholderText("Enter Private Key here...")
        self.hash_key_edit.show()
        #QObject.connect(self.hash_key_edit,SIGNAL("returnPressed()"),self.execute_decrypt)
        self.hash_key_edit.returnPressed.connect(self.execute_decrypt)
    
        #Buttons
        decrypt_button = QPushButton(self.mainWin)
        decrypt_button.setText('Decrypt')
        decrypt_button.setGeometry(112,790,100,20)
        decrypt_button.show()
        #QObject.connect(decrypt_button,SIGNAL("clicked()"),self.execute_decrypt)
        decrypt_button.clicked.connect(self.execute_decrypt)

        encrypt_button = QPushButton(self.mainWin)
        encrypt_button.setText('Encrypt')
        encrypt_button.setGeometry(11,790,100,20)
        encrypt_button.show()
        #QObject.connect(encrypt_button,SIGNAL("clicked()"),self.execute_encrypt)
        encrypt_button.clicked.connect(self.execute_encrypt)

        clear_button = QPushButton(self.mainWin)
        clear_button.setText('Clear Display')
        clear_button.setGeometry(387,750,100,60)
        clear_button.show()
        #QObject.connect(clear_button,SIGNAL("clicked()"),self.clear_dispText)
        clear_button.clicked.connect(self.clear_dispText)

        sys.exit(app.exec_())


    def clear_dispText(self): #just clears the text off the gray display
        if self.dispText.toPlainText():
            self.dispText.clear()
            self.dispLog.append('Text cleared')
        if not self.dispText.toPlainText():
            self.dispLog.append('Nothing to clear')
    
    def execute_decrypt(self):
        if not self.hash_key_edit.text():
            try:
                self.decipher()
                self.hash_key_edit.clear()
                self.dispText.setReadOnly(False) #enable text modification
                #self.dispText.setTextInteractionFlags(Qt.NoTextInteraction) #enable text modification
            except UnicodeDecodeError:
                self.dispLog.append('You must enter a (valid) private key.')
                self.hash_key_edit.clear()
            except binascii.Error as err1:
                self.dispLog.append('Unable to decrypt - Text is already in plaintext.')
                self.hash_key_edit.clear()

        if self.hash_key_edit.text():
            try:
                self.decipher()
                self.hash_key_edit.clear()
                self.dispText.setReadOnly(False) #enable text modification
                #self.dispText.setTextInteractionFlags(Qt.NoTextInteraction) #enable text modification
            except UnicodeDecodeError:
                self.dispLog.append('Your private key is invalid.')
                self.hash_key_edit.clear()
            except binascii.Error as err2:
                self.dispLog.append('Unable to decrypt - Text is already in plaintext.')
                self.hash_key_edit.clear()            
        
    def decipher(self):
        try:
            if self.dispText.toPlainText():
                ciphertext = self.dispText.toPlainText()
                bytes_ciphertext = bytes(base64.b64decode(ciphertext))
                iv = "0123456789abcdef"
                keypass = self.hash_key_edit.text()
                key = hashlib.sha256(bytes(keypass,"utf-8")).digest()   #hash the given pass phrase
                decryptor = AES.new(key, AES.MODE_CFB, iv.encode("utf8"))  #create AES object for decryption using the generated hashed key and an arbitrary iv
                bytes_plaintext = decryptor.decrypt(bytes_ciphertext)
                plaintext = str(bytes_plaintext,"utf-8")
                self.dispText.clear()
                self.dispText.setText(plaintext)
                self.dispLog.append('Decryption successful.')
            else:
                self.dispLog.append('No file selected')
        except Exception as e:
            print(e)
            self.dispLog.append('decipher error')

    def execute_encrypt(self):
        #pdb.set_trace()
        if not self.hash_key_edit.text():
            try:
                self.cipher()
                self.hash_key_edit.clear()
                self.dispText.setReadOnly(True) #disable text modification
                #self.dispText.setTextInteractionFlags(Qt.NoTextInteraction) #disable text modification
            except UnicodeDecodeError:
                self.dispLog.append('You must enter a (valid) private key.')
                self.hash_key_edit.clear()
            except binascii.Error as err1:
                self.dispLog.append('Unable to decrypt - Text is already in plaintext.')
                self.hash_key_edit.clear()

        if self.hash_key_edit.text():
            try:
                self.cipher()
                self.hash_key_edit.clear()
                self.dispText.setReadOnly(True) #disable text modification
                #self.dispText.setTextInteractionFlags(Qt.NoTextInteraction) #disable text modification
            except UnicodeDecodeError:
                self.dispLog.append('Your private is invalid.')
                self.hash_key_edit.clear()
            except binascii.Error as err2:
                self.dispLog.append('Unable to decrypt - Text is already in plaintext.')
                self.hash_key_edit.clear()

    def cipher(self):
        try:
            if self.dispText.toPlainText():
                #pdb.set_trace()
                plaintext = self.dispText.toPlainText()
                iv = "0123456789abcdef"
                keypass = self.hash_key_edit.text()
                key = hashlib.sha256(bytes(keypass,"utf-8")).digest()
                encryptor = AES.new(key, AES.MODE_CFB, iv.encode("utf8"))
                bytes_ciphertext = encryptor.encrypt(plaintext.encode("utf8"))
                ciphertext = str(base64.b64encode(bytes_ciphertext),"utf-8")
                self.dispText.clear()
                self.dispText.setText(ciphertext)
                self.dispLog.append('Encryption successful.')
            else:
                self.dispLog.append('No file selected')
        except Exception as e:
            print(e)
            self.dispLog.append('cipher error')

    def openFile(self):
        #pdb.set_trace()
        try:
            filename,_ = QFileDialog.getOpenFileName(self.mainWin,'Open File')
            fh = open(filename)
            self.dispText.setText(fh.read())
            fh.close()
        #except FileNotFoundError:
        except Exception as e:
            print('Error:'+e)

    def saveFile(self):
        try:
            filename,_ = QFileDialog.getSaveFileName(self.mainWin,'Save File')
            fh = open(filename,'w')
            text = self.dispText.toPlainText()
            fh.write(text)
            fh.close
        except Exception as e1:
            pass

    def searchText(self):
        #grab the text to search from
        text = self.dispText.toPlainText()
        #grab the text to find
        query = self.searchBar.toPlainText()

    def helpPopup(self): #Pop up window for help text
        self.popup = QDialog(self.mainWin)
        self.popup.setWindowTitle("QTPycryptor Help")
        self.popup.setGeometry(800,200,500,300)
        self.popup.show()

        self.helpText = QTextEdit(self.popup)
        self.helpText.setGeometry(10,10,480,280)
        self.helpText.setText(self.__doc__)
        self.helpText.setReadOnly(True)
        self.helpText.setTextInteractionFlags(Qt.NoTextInteraction)
        pal1 = self.helpText.viewport().palette()
        pal1.setColor(self.helpText.viewport().backgroundRole(), QColor(200,200,200))
        self.helpText.viewport().setPalette(pal1)
        self.helpText.show()

    def searchPopup(self): #pop up window for find text
        self.popup2 = QDialog(self.mainWin)
        self.popup2.setWindowTitle("Find Text")
        self.popup2.setGeometry(800,200,375,110)
        self.popup2.show()

        #Searchbar
        self.searchBar = QLineEdit(self.popup2)
        self.searchBar.setGeometry(12,12,350,27)
        self.searchBar.setPlaceholderText("Search...")
        self.searchBar.show()

        #Buttons
        find_button = QPushButton(self.popup2)
        find_button.setText('Find')
        find_button.setGeometry(11,50,100,20)
        find_button.show()
        find_button.clicked.connect(self.searchText)

        find_all_button = QPushButton(self.popup2)
        find_all_button.setText('Find All')
        find_all_button.setGeometry(11,72,100,20)
        find_all_button.show()

        caseSens_checkbox = QCheckBox("Case Sensitive", self.popup2)
        caseSens_checkbox.setGeometry(250,50,100,20)
        caseSens_checkbox.show()

        wholeWords_checkbox = QCheckBox("Whole words only", self.popup2)
        wholeWords_checkbox.setGeometry(250,72,150,20)
        wholeWords_checkbox.show()

        
if __name__ == '__main__':
 
    pycryptor = Pycryptor()
    print(pycryptor.__doc__)
    pycryptor.mainGui()
