from fastapi import APIRouter,Depends
from models import Tag
from datetime import date
from schemas import TagCreate

from database import get_db

router = APIRouter()

@router.post("/Tag")
async def create_tag(details : TagCreate,db = Depends(get_db)):
    
    tag_details = Tag(
        tag_name = details.title,
        created = date.today()
    )
    db.add(tag_details)
    await db.commit()
    await db.refresh(tag_details)
    return tag_details