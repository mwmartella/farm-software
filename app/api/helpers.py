from fastapi import HTTPException

def not_found(resource: str, identifier):
    raise HTTPException(status_code=404, detail=f"{resource} with ID '{identifier}' not found.")

def already_exists(resource: str, identifier):
    raise HTTPException(status_code=409, detail=f"{resource} with code '{identifier}' already exists.")

def delete_message(resource: str, identifier):
    return {"message": f"{resource} with code '{identifier}' deleted"}