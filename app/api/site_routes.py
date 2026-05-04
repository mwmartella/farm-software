from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from uuid import UUID

from app.db import get_db

from app.api.helpers import not_found, already_exists, delete_message, foreign_key_fail

from schema.site import SitesCreate, SitesRead, SitesUpdate

from app.repositories.site_repository import create_site as create_site_repo
from app.repositories.site_repository import list_sites as list_sites_repo
from app.repositories.site_repository import get_site_by_id as get_site_by_id_repo
from app.repositories.site_repository import update_site as update_site_repo
from app.repositories.site_repository import delete_site as delete_site_repo

router = APIRouter(prefix="/sites", tags=["Sites"])

@router.post("/", response_model=SitesRead, status_code=status.HTTP_201_CREATED)
def create_site(site_data: SitesCreate, db: Session = Depends(get_db)):
    try:
        site = create_site_repo(db, site_data)
        return site
    except IntegrityError as e:
        if "foreign key" in str(e.orig).lower():
            raise foreign_key_fail('Site + Business', site_data.business_id)
        raise already_exists('Site', site_data.code)

@router.get("/", response_model=list[SitesRead], status_code=status.HTTP_200_OK)
def list_sites(db: Session = Depends(get_db)):
    sites_lst = list_sites_repo(db)
    return sites_lst

@router.get("/{site_id}", response_model=SitesRead, status_code=status.HTTP_200_OK)
def get_site_by_id(site_id: UUID, db: Session = Depends(get_db)):
    site_row = get_site_by_id_repo(db, site_id)
    if site_row is None:
        not_found("Site", site_id)
    return site_row

@router.patch("/{site_id}", response_model=SitesRead)
def update_site(site_id: UUID, site_updates: SitesUpdate, db: Session = Depends(get_db)):
    site = get_site_by_id_repo(db, site_id)
    if site is None:
        not_found("Site", site_id)
    try:
        updated_site = update_site_repo(db, site, site_updates)
        return updated_site
    except IntegrityError as e:
        if "foreign key" in str(e.orig).lower():
            raise foreign_key_fail('Site + Business', site_updates.business_id)
        raise already_exists("Site", site_updates.code)

@router.delete("/{site_id}", status_code=status.HTTP_200_OK)
def delete_site(site_id: UUID, db: Session = Depends(get_db)):
    site = get_site_by_id_repo(db, site_id)
    if site is None:
        not_found("Site", site_id)
    delete_site_repo(db, site)
    return delete_message("Site", site.code)