from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from uuid import UUID

from models.site import Sites
from schema.site import SitesCreate, SitesUpdate

def create_site(db: Session, site_data: SitesCreate) -> Sites:
    site = Sites(**site_data.model_dump())
    try:
        db.add(site)
        db.commit()
        db.refresh(site)
    except IntegrityError:
        db.rollback()
        raise
    return site

def list_sites(db: Session) -> list[Sites]:
    result = db.scalars(select(Sites).order_by(Sites.name)).all()
    return list(result)

def get_site_by_id(db: Session, site_id: UUID) -> Sites | None:
    return db.get(Sites, site_id)

def update_site(db: Session, site: Sites, update_data: SitesUpdate) -> Sites:
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(site, field, value)
    try:
        db.commit()
        db.refresh(site)
    except IntegrityError:
        db.rollback()
        raise
    return site

def delete_site(db: Session, site: Sites) -> None:
    try:
        db.delete(site)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise