from sqlalchemy.orm import Session #this is the current session that is connected
from sqlalchemy.exc import IntegrityError #This is the error we get when the commit fails on a unique constraint

from models.business import Business
#memory jog: the model is the part of the program that lets it know what the columns are and
# what to expect them to contain, so we do not have to type in manual SQL commands over and over.
from schema.business import BusinessCreate
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