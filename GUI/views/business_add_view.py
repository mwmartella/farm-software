#Here goes nothing as my first proper GUI attempt
from PySide6.QtWidgets import QWidget, QLineEdit, QComboBox, QLabel, QPushButton, QFormLayout, QVBoxLayout, QMessageBox

from GUI.helpers import optional_text, format_model_for_display

from schema.business import BusinessCreate #Apparently we will need this


class BusinessAddView(QWidget): #This creates the class that lets the program know that this is a GUI screen.
    def __init__(self, business_api):
        #This is expecting the API to be passed when called, without this the API would explicitly be written
        # That would break your MVC rules so keeping it separate makes it easier to edit and test.
        super().__init__() #When the screen is created this runs

        self.business_api = business_api

        self.name_input = QLineEdit() #These are all the input fields for the user, they are all text boxes
        self.code_input = QLineEdit()
        self.abn_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.is_supplier_input = QComboBox() #Up to here then it is combo box or dropdown
        self.is_supplier_input.addItem("Yes", True) #This adds a layer of ease for the user, the user sees yes, the data stores True
        self.is_supplier_input.addItem("No", False) #Same for no and False

        self.status_label = QLabel("") #I am not quite sure why the empty string for label when the button comes with a tag?
        #Now im thinking it is what gets returned to the user, the blank string is a place-holder?
        self.save_button = QPushButton("Add Business") #This is the add button for the user

        form = QFormLayout() #This function creates the layout template for the view
        form.addRow("Business name:", self.name_input) #The following then adds our widgets to the form layout
        form.addRow("Business code:", self.code_input)
        form.addRow("ABN:", self.abn_input)
        form.addRow("Phone:", self.phone_input)
        form.addRow("Email:", self.email_input)
        form.addRow("Are they a supplier?", self.is_supplier_input)

        layout = QVBoxLayout(self) #This then orders the layouts we want and declares it belongs to the current screen
        layout.addLayout(form) #Form First
        layout.addWidget(self.save_button) #Then save Button
        layout.addWidget(self.status_label) #Then the label which I think is the return data?

        self.save_button.clicked.connect(self.on_save_clicked)

    def clear_form(self):
        self.name_input.clear()
        self.code_input.clear()
        self.abn_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.is_supplier_input.setCurrentIndex(0)
        self.status_label.setText("")
    #Ok here is the function for the save button but im going to have to tweak it to suit my program.
    #My understanding is that my program already handles errors so any errors need to be pop-ups from those exceptions.
    def on_save_clicked(self):
        try:
            payload = BusinessCreate( #Here is where we generate the payload back to the API
                name=self.name_input.text().strip(), #Mostly this just captures the text the user input
                code=self.code_input.text().strip(),
                abn=optional_text(self.abn_input),
                phone=optional_text(self.phone_input),
                email=optional_text(self.email_input),
                is_supplier=self.is_supplier_input.currentData(),
                #Here is a little different because what is in the combo box is not what we want.
                #We want the value that it converts to in a boolean so we use currentData() to get that.
            )

            business = self.business_api.create_business(payload)

            self.status_label.setText(f"Created: {business.name} ({business.code})")

            QMessageBox.information(
                self,
                "Business Created",
                format_model_for_display(business)
            )

            self.clear_form()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error",
                str(error)
            )

