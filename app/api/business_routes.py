from fastapi import APIRouter, Depends, status, HTTPException
#api router defines the route group/Depends injects dependencies
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db import get_db
from schema.business import BusinessCreate, BusinessRead
from app.repositories.business_repository import create_business as create_business_repo
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
        raise HTTPException(status_code=409, detail=f"Business with code '{business_data.code}' already exists.")
        #this is the controller that handles the exception that we questioned in the repo

