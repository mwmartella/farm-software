#In here we have the actual logic that links the GUI to the API.
import requests
from uuid import UUID

from schema.business import BusinessCreate, BusinessRead, BusinessUpdate

class BusinessAPI:

    def __init__(self, base_url: str):
        #Gets the URL that is passed to it, in this case by the run GUI file.
        self.base_url = base_url
        #This function assigns self as the URL for the API, we do this inside a class like this because everything inside this class will need it.
        
    @staticmethod
    #this stops the function from needing 'self' as the first argument.
    # Which it would normally get as a result from being in a class.
    # This is because this function does not need it as it works within the other functions.
    def _handle_error(response: requests.Response):
        #This function is the part that gets the errors back from the API and shows them to the user so the user sees the actual custom error messages.
        #The naming convention here with the leading underscore is to signal to anyone who reads the code that this function was only designed to be used inside this class.
        try:
            detail = response.json().get("detail", "An unexpected error occurred.")
            #the response.json().get part here is the part that gets the proper error message from the API.
            #The string after that is the fallback incase an unhandled error occurs.
            #this part is the true function, its handling errors thrown by the API
        except ValueError:
            detail = "An unexpected error occurred."
            #if an error outside the API happens this will trigger the value error and show the user the hard coded string.
        raise Exception(detail)

    def create_business(self, payload: BusinessCreate) -> BusinessRead:
        #this function sends the payload to create a business to the api
        response = requests.post(
            f"{self.base_url}/businesses/",
            json=payload.model_dump()
            #converts the payload to a JSON - This is different to the model_dump() in the repo which does the JSON-SQL Object conversion
        )
        if not response.ok:
            self._handle_error(response)
            #This calls the function for handling the errors, same logic, any API errors will be passed to the user.
        return BusinessRead(**response.json())
        #This gets the JSON dict back from the API and then converts it to the pydantic model to show the user.

    def list_businesses(self) -> list[BusinessRead]:
        #gets the lists of businesses from the API
        response = requests.get(f"{self.base_url}/businesses/")
        if not response.ok:
            self._handle_error(response)
        return [BusinessRead(**b) for b in response.json()]
        #pretty simple this one, gets the response, converts the JSON to pydantic and handles any errors.

    def get_business_by_id(self, business_id: UUID) -> BusinessRead:
        #Calls the API to get a business with an ID supplied by the GUI
        response = requests.get(f"{self.base_url}/businesses/{business_id}")
        if not response.ok:
            self._handle_error(response)
        return BusinessRead(**response.json())
        #again pretty simple use of the API here.

    def update_business(self, business_id: UUID, payload: BusinessUpdate) -> BusinessRead:
        #this function calls the API to update the values that have been supplied by the GUI
        #The api has been programmed to handle blank entries.
        response = requests.patch(
            f"{self.base_url}/businesses/{business_id}",
            json=payload.model_dump(exclude_unset=True)
        )
        if not response.ok:
            self._handle_error(response)
        return BusinessRead(**response.json())

    def delete_business(self, business_id: UUID) -> dict:
        #this calls the API delete endpoint for removing an entry using ID.
        response = requests.delete(f"{self.base_url}/businesses/{business_id}")
        if not response.ok:
            self._handle_error(response)
        return response.json()