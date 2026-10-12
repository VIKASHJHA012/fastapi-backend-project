from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import func,select
from schemas import PostCreate,PostResponse,PostUpdatePatch,TagResponse
from datetime import date
from models import Post,User,PostTag,Tag
from database import get_db
from .auth import get_current_user
from sqlalchemy.orm import selectinload
router = APIRouter()

@router.post("/Post",response_model=PostResponse)
async def posts(post : PostCreate,db = Depends(get_db), current_user = Depends(get_current_user)):

    details = Post(
        title = post.title,
        created = date.today()
    )

    details.user = current_user
    db.add(details)
    await db.commit()
    await db.refresh(details)

    return details

@router.get("/Post/{post_id}",response_model=list[TagResponse])
async def get_post_tags(post_id: int ,db = Depends(get_db)):
    # post_details = db.query(Post).filter(Post.id == post_id).first()
    statement = (select(Post)
                 .options(
                  selectinload(Post.post_tag)
                 .selectinload(PostTag.tag))
                 .filter(Post.id == post_id))
    result  = await db.execute(statement)

    post_details = result.scalars().first()

    if post_details is None:
        raise HTTPException (status_code=404,detail="Post not found")

    return post_details.tags
#     return [
#     {
#         "id": tag.id,
#         "tag_name": tag.tag_name
#     }
#     for tag in post_details.tags
# ]

@router.get("/Post/User/{input_email}",response_model=list[PostResponse])
async def get_post(input_email:str, db = Depends(get_db)):
    # user_posts = db.query(Post).join(User).filter(User.email == input_email).all()

    statement = select(Post).join(User).filter(User.email  == input_email)
    result = await db.execute(statement)

    user_posts = result.scalars().all()
    return user_posts


@router.get("/Posts/{id}",response_model=PostResponse)
async def get_posts(id:int ,db= Depends(get_db),current_user = Depends(get_current_user)):

    # post_details = db.query(Post).filter(Post.id == id).filter(Post.user_id == current_user.id).first()
    statement = select(Post).filter(Post.id == id).filter(Post.user_id == current_user.id)
    result = await db.execute(statement)

    post_details = result.scalars().first()

    if post_details is None:
        raise HTTPException(status_code=404,detail='Post or User doesnot exist')

    return post_details

@router.delete("/Post/{post_id}")
async def delete_posts(post_id :int, db = Depends(get_db),current_user = Depends(get_current_user)):

    #verifying if the user is deleting its post
    # post_details = db.query(Post).filter(
    #     Post.id == post_id
    # ).filter(
    #     Post.user_id == current_user.id
    # ).first()
    statement = select(Post).filter(Post.id == post_id).filter(Post.user_id == current_user.id)

    result = await db.execute(statement)

    post_details = result.scalars().first()

    if post_details is None:
        raise HTTPException(status_code=404,detail="Unauthorized acccess to delete the post or the Post is invalid")

    await db.delete(post_details)


    await db.commit()
    return {
        "Message":"Post deleted successfully"
    }

@router.patch("/Post/{post_id}",response_model=PostResponse)
async def post_update_patch (post_id :int, patching_data : PostUpdatePatch,current_user =Depends(get_current_user),db = Depends(get_db)):
    # post_details = db.query(Post).filter(Post.id == post_id).filter(Post.user_id == current_user.id).first()
    statement = select(Post).filter(Post.id == post_id).filter(Post.user_id == current_user.id)
    result = await db.execute(statement)

    post_details = result.scalars().first()


    if post_details is None:
        raise HTTPException(status_code=404,detail="Post not found or User is not autorized to update the post")

    post_update = patching_data.model_dump(exclude_unset=True)

    for key ,value in post_update.items():
        setattr(post_details,key,value)

    await db.commit()
    await db.refresh(post_details)

    return post_details

# returning the latest Post

# @router.get("/Post/User/{user_id}")
# async def latest_post(user_id : int,db = Depends(get_db)):

#     # user_details = db.query(User).filter(User.id == user_id).first()
#     statement = (
#         select(User)
#         .filter(User.id == user_id)
#     )
#     result = await db.execute(statement)
#     user_details = result.scalars().first()

#     if user_details is None:
#         raise HTTPException(status_code= 404, detail="User doesn't exist")

#     # post_details = db.query(Post).filter(Post.user_id == user_id).order_by(Post.created.desc()).limit(5).all()
#     statement2 = (
#         select(Post)
#         .filter(Post.user_id  == user_id)
#         .order_by(Post.created.desc())
#         .limit(5)


#     )
#     result2 = await db.execute(statement2)
#     post_details = result2.scalars().all()
#     return post_details
    

# return the title

@router.get("/Post/Search/",response_model=list[PostResponse])
async def get_title(title : str , db = Depends(get_db)):

    # post_details = db.query(Post).filter(func.lower(Post.title).like(f"%{title.lower()}%")).order_by(Post.created.desc()).limit(10).all()
    statement = (
        select(Post)
        .filter(func.lower(Post.title).like(f"%{title.lower()}%"))
        .order_by(Post.created.desc())
        .limit(10)

    )
    result = await db.execute(statement)

    post_details = result.scalars().all()

    return post_details

# return all post via Tag

@router.get("/Post/Tag",response_model=list[PostResponse])

async def get_posts(tag_name : str,db = Depends(get_db)):

    # tag_details = db.query(Tag).filter(
    #     func.lower(Tag.tag_name) == tag_name.lower()
    # ).first()
    statement = (
        select(Tag)
        .filter(func.lower(Tag.tag_name) == tag_name.lower())
    )
    result = await db.execute(statement)

    tag_details = result.scalars().first()

    if tag_details is None:
        raise HTTPException (status_code=404, detail= "Tag does not exist")

    # post_details = db.query(Post).join(PostTag,PostTag.post_id == Post.id).join(
    #     Tag,Tag.id == PostTag.tag_id
    # ).filter(func.lower(Tag.tag_name)== (tag_name.lower())).order_by(Post.created.desc()).limit(10).all()

    statement2 = (
        select(Post)
        .join(PostTag, PostTag.post_id == Post.id)
        .join(Tag, Tag.id == PostTag.tag_id)
        .filter(func.lower(Tag.tag_name) == (tag_name.lower()))
        .order_by(Post.created.desc())
        .limit(10)
    )
    result2  = await db.execute(statement2)
    post_details =  result2.scalars().all()

    return post_details

@router.get("/Post/User/{user_id}/Search/{title}",response_model=list[PostResponse])
async def get_user(user_id : int ,title :str, db = Depends(get_db)):

    # user_details = db.query(User).filter(User.id == user_id).first()
    statement = (
        select(User)
        .filter(User.id == user_id)
    )
    result = await db.execute(statement)

    user_details = result.scalars().first()

    if user_details is None:
        raise HTTPException (status_code=404, detail="User does not exist")

    # post_details = db.query(Post).filter(Post.user_id == user_id).filter(func.lower(Post.title).like(f'%{title.lower()}%')).order_by(Post.created.desc()).limit(5).all()
    statement2 = (
        select(Post)
        .filter(Post.user_id == user_id)
        .filter(func.lower(Post.title).like(f"%{title.lower()}%"))
        .order_by(Post.created.desc())
        .limit(5)
    )

    result2 = await db.execute(statement2)

    post_details = result2.scalars().all()

    return post_details

@router.get("/Post/User/{user_id}/Count")
async def get_user_post(user_id : int,db = Depends(get_db)):

    # user_details = (
    #     db.query(User)
    #     .filter(User.id == user_id)
    #     .first()
    # )
    statement = (
       select(User) 
       .filter(User.id == user_id)
    )
    result = await db.execute(statement)
    user_details = result.scalars().first()

    if user_details is None:
        raise HTTPException (status_code=404,detail="User does not exist")

    # post_count  = (
    #    db.query(Post)
    #    .filter(Post.user_id == user_id)
    #    .count()
    # )
    statement2 = (
       select(func.count(Post.id)) 
       .filter(Post.user_id == user_id)
    )
    result2 = await db.execute(statement2)

    post_count = result2.scalar()

    return post_count