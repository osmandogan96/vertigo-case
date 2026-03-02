import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.session import get_db
from db.models import Clan
from schemas.schemas import ClanCreate, ClanResponse, MessageResponse

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Clan API is running"}


@router.post("/clans/", response_model=ClanResponse, status_code=201)
def create_clan(body: ClanCreate, db: Session = Depends(get_db)):
    """Create a new clan with name and region."""
    clan = Clan(id=uuid.uuid4(), name=body.name, region=body.region)
    db.add(clan)
    db.commit()
    db.refresh(clan)
    return clan


@router.get("/clans/", response_model=list[ClanResponse])
def list_clans(db: Session = Depends(get_db)):
    """List all clans, newest first."""
    return db.query(Clan).order_by(Clan.created_at.desc()).all()


@router.get("/clans/search", response_model=list[ClanResponse])
def search_clans(
    name: str = Query(..., min_length=3, description="Min 3 chars, case-insensitive contains"),
    db: Session = Depends(get_db),
):
    """Find clans by name (min 3 letters, contains)."""
    pattern = f"%{name}%"
    return (
        db.query(Clan)
        .filter(func.lower(Clan.name).like(func.lower(pattern)))
        .order_by(Clan.created_at.desc())
        .all()
    )


@router.get("/clans/{clan_id}", response_model=ClanResponse)
def get_clan(clan_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a specific clan by UUID."""
    clan = db.query(Clan).filter(Clan.id == clan_id).first()
    if not clan:
        raise HTTPException(status_code=404, detail="Clan not found")
    return clan


@router.delete("/clans/{clan_id}", response_model=MessageResponse)
def delete_clan(clan_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete a specific clan by UUID."""
    clan = db.query(Clan).filter(Clan.id == clan_id).first()
    if not clan:
        raise HTTPException(status_code=404, detail="Clan not found")
    db.delete(clan)
    db.commit()
    return MessageResponse(message="Clan deleted successfully", id=clan_id)
