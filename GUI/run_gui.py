import sys
import os

from PySide6.QtWidgets import QApplication

from GUI.api.business_api import BusinessAPI
from GUI.views.business_add_view import BusinessAddView


def main():
    app = QApplication(sys.argv)
    # QApplication is the modules guts that runs the GUI, sys.argv is for when the user adds any command line arguments

    api_url = os.getenv("API_URL", "http://localhost:8000")
    #This gest the API address from the ENV file but falls back to the default if it fails.

    business_api = BusinessAPI(base_url=api_url)
    # Creates the API client that all views will use to communicate with the backend.

    window = BusinessAddView(business_api)
    #The GUI has to do something, the only thing we have for it to do is create the 1 window we coded.
    # When we eventually build the overall wrapper window that is what would be created here and the buttons within it would call the other windows.
    #the api is passed as an argument so the gui_api files can use it, which will also default back to local host as set above.

    window.setWindowTitle("Farm Software")
    #naming the window
    window.show()
    #tell the program to show it

    sys.exit(app.exec())
    #app.exec() runs the loop for the window, sits and waits for user input
    #sys.exit() cleany exits it when the loop ends.


if __name__ == "__main__":
    main()
#this is the entry point for the whole app __name__ is used so it can not be auto run by an import, projecting the whole thing.

