from fastapi import HTTPException

def not_found(resource: str, identifier):
    raise HTTPException(status_code=404, detail=f"{resource} with ID '{identifier}' not found.")

def already_exists(resource: str, identifier):
    raise HTTPException(status_code=409, detail=f"{resource} with code '{identifier}' already exists.")

def delete_message(resource: str, identifier):
    return {"message": f"{resource} with code '{identifier}' deleted"}

def foreign_key_fail(resource: str, identifier):
    raise HTTPException(status_code=400, detail=f"'{resource}' with ID '{identifier}' does not exist.")

def foreign_key_remove_fail(resource: str):
    raise HTTPException(status_code=409, detail=f"Cannot delete '{resource}' as it has sites linked to it.")