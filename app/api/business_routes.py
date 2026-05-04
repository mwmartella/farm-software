from fastapi import APIRouter, Depends, status, HTTPException
#api router defines the route group/Depends injects dependencies
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from uuid import UUID

from app.db import get_db

from app.api.helpers import not_found, already_exists, delete_message, foreign_key_remove_fail

from schema.business import BusinessCreate, BusinessRead, BusinessUpdate

from app.repositories.business_repository import create_business as create_business_repo
from app.repositories.business_repository import list_businesses as list_business_repo
from app.repositories.business_repository import get_business_by_id as get_business_by_id_repo
from app.repositories.business_repository import update_business as update_business_repo
from app.repositories.business_repository import delete_business as delete_business_repo
#rename the repo slightly just to avoid route name confusion

router = APIRouter(prefix="/businesses", tags=["Businesses"])
#creates the router object which knows to get the routes and add them to the API
# we add the prefix argument so instead of every route here having the full name it only needs "/"

@router.post("/", response_model=BusinessRead, status_code=status.HTTP_201_CREATED)
#defines the POST route, HTTP method POST, URL Path /businesses, response format is the schema for read
#status code to be more specific than a generic 200 OK
def create_business(business_data: BusinessCreate, db: Session = Depends(get_db)):
    #this function here is using BusinessCreate to convert JSON to the schema object, And inject the database session
    try:
        business = create_business_repo(db, business_data)
        # calls the repo which inserts into the database and commits it and returns the business model instance
        # then you have to go to main.py and register the router
        return business
    except IntegrityError:
        raise already_exists('Business', business_data.code)
        #this is the controller that handles the exception that we questioned in the repo

@router.get("/", response_model=list[BusinessRead], status_code=status.HTTP_200_OK)
#response model here is list[] because even though the response returns a list we need to declare it a list
def list_businesses(db: Session = Depends(get_db)):
    business_lst = list_business_repo(db)
    return business_lst

@router.get("/{business_id}", response_model=BusinessRead, status_code=status.HTTP_200_OK)
#Note the {business_id} in the path, this is how we capture the UUID from the URL path.
# Whatever function calls this endpoint will pass the argument of UUID which gets added
def get_business_by_id(business_id: UUID, db: Session = Depends(get_db)):
    #Then we assign the type hint to the business_id, this does 2 things:
    #1 - it returns an error 422 if the data it gets is not a UUID
    #2 - because the business_id part matches the {business_id} part, it inputs the Url data
    business_row = get_business_by_id_repo(db, business_id)
    if business_row is None:
        not_found("Business", business_id)
    return business_row

@router.patch("/{business_id}", response_model=BusinessRead)
#even though its an update the response model to get the data is BusinessRead
def update_business(business_id: UUID, business_updates: BusinessUpdate, db: Session = Depends(get_db)):
    business = get_business_by_id_repo(db, business_id)
    if business is None:
        not_found("Business", business_id)
    #In order for the update to have the data it needs, when the user selects the row the ID stored.
    # Then using that ID the get_business_id function is called before running the update functions.
    try:
        updated_business = update_business_repo(db, business, business_updates)
        return updated_business
    except IntegrityError:
        raise already_exists("Business", business_updates.code)
    #Have to raise this error incase user updates a business to one already listed
@router.delete("/{business_id}", status_code=status.HTTP_200_OK)
def delete_business(business_id: UUID, db: Session = Depends(get_db)):
    business = get_business_by_id_repo(db, business_id)
    if business is None:
        not_found("Business", business_id)
    try:
        delete_business_repo(db, business)
    except IntegrityError:
        raise foreign_key_remove_fail("Business")
    return delete_message("Business", business.code)
    #even though there is a return in the function we still need one here