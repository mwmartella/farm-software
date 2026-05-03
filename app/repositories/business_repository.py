from sqlalchemy.orm import Session #this is the current session that is connected
from sqlalchemy.exc import IntegrityError #This is the error we get when the commit fails on a unique constraint
from sqlalchemy import select
from uuid import UUID

from models.business import Business
#memory jog: the model is the part of the program that lets it know what the columns are and
# what to expect them to contain, so we do not have to type in manual SQL commands over and over.
from schema.business import BusinessCreate, BusinessUpdate
#memory jog: the schema is what the program uses to validate data in either direction.

def create_business(db: Session, business_data: BusinessCreate) -> Business:
    #so this function here is how the data the user inputs gets created into a business object
    # uses the current session connected, uses BusinessCreate to validate the data the user is giving the program
    business = Business(**business_data.model_dump())
    #this turns the pydantic schema we wrote into a normal dictionary
    # and then creates an SQLAlchemy object out of it
    try:
        db.add(business)
        #stages it for insert
        db.commit()
        #writes it to postgres
        db.refresh(business)
        #reloads the database so the auto generated values, UUIDs and TimeStamps etc. are available
    except IntegrityError:
        db.rollback()
        #rollback stops half corrupted data getting stuck and the DB being blocked
        raise
        #this command sends the exception back to the controller instead of the object
        #we do this so the repo is not directly communicating with the user, and therefore staying within MVC rules
    return business
    #return the model object to the controller/API route

def list_businesses(db: Session) -> list[Business]:
    result = db.scalars(select(Business).order_by(Business.name)).all()
    return list(result)
    #This function gets all the data from the Business table for the user, we use the select module from sqlalchemy 2.0.
    #Then we wrap the result in a list so it matches the type hint of what we want.

def get_business_by_id(db: Session, business_id: UUID) -> Business | None:
    return db.get(Business, business_id)
    #Simpler one that returns the data of a business when supplied with a Primary Key.
    # we do not need error handling on this or the list functions as if they find nothing it will just return None, so no error thrown.

def update_business(db: Session, business: Business, update_data: BusinessUpdate) -> Business:
    for field, value in update_data.model_dump(exclude_unset=True).items():
        #Exclude_unsent is the code that tells the program not to update any field that the user did not supply
        setattr(business, field, value)
    try:
        db.commit()
        db.refresh(business)
    except IntegrityError:
        db.rollback()
        raise
    return business

def delete_business(db: Session, business: Business) -> None:
    try:
        db.delete(business)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
        #Will fail on IntegrityError if other tables are FKed to the entry trying to be deleted.

#the last 2 functions are pretty self-explanatory but 1 note to mention.
# Seems counterintuitive that you would not need the ID for these 2 functions, my old SQLITE brain thinks
# "UPDATE WHERE ID =" but we leave that to the controller to make sure that the existence of the entry is there.
# Also update_business and delete_business can fail with integrity errors so we need to handle them here.