from fastapi import APIRouter,Depends,HTTPException
from database import get_db
from datetime import date
from models import Post,Tag,PostTag
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

router = APIRouter()


@router.post("/Post/{post_id}/Tag/{tag_id}")
async def create_posttag(post_id : int , tag_id : int ,db = Depends(get_db)):
    # post = db.query(Post).filter(Post.id == post_id).first()
    statement = (
        select(Post)
        .filter(Post.id == post_id)
    )
    result  = await db.execute(statement)
    post = result.scalars().first()
    # tag = db.query(Tag).filter(Tag.id == tag_id).first()

    statement2 = (
        select(Tag)
        .filter(Tag.id == tag_id)
    )
    result2 = await db.execute(statement2)
    tag = result2.scalars().first()

    if post is None or tag is None :
        raise HTTPException(status_code=404,detail='Post/tag does not exist')

    posttag_details = PostTag(
        post = post,
        tag = tag,
        created = date.today()
    )
    try:
        db.add(posttag_details)
        await db.commit()
        await db.refresh(posttag_details)
        return posttag_details
    except IntegrityError:
        raise HTTPException(status_code=409,detail="Tag is already associated with Post")

@router.delete("/Post/{post_id}/Tag/{tag_id}")
async def remove_tag(post_id : int , tag_id : int ,db = Depends(get_db)):
    # details = db.query(PostTag).filter(PostTag.post_id ==post_id ).filter(PostTag.tag_id== tag_id).first()

    statement = (
        select(PostTag)
        .filter(PostTag.post_id == post_id)
        .filter(PostTag.tag_id == tag_id)
    )
    result = await db.execute(statement)

    details = result.scalars().first()
    if details is None:
        raise HTTPException(status_code=404,detail="Tag is not associated with this post")

    await db.delete(details)
    await db.commit()
    return {
        "Message":"Tag removed from the post"
    }