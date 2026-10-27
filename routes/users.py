from fastapi import APIRouter,Depends,HTTPException
from database import get_db
from schemas import UserCreate,UserUpdate,UserResponse,UserUpdatePatch
from models import User,Post
from .auth import get_current_user
from sqlalchemy import select
from sqlalchemy.orm import selectinload

router = APIRouter()    


@router.get("/users",response_model = list[UserResponse])
async def get_users(db = Depends(get_db),current_user = Depends(get_current_user)):
        
        # users = db.query(User).all()
        statement = (select(User).options(selectinload(User.posts)))
        result = await db.execute(statement)
        users = result.scalars().all()
        return users
       

@router.get("/users/{id}",response_model = UserResponse)
async def get_user(id :int,db = Depends(get_db),current_user = Depends(get_current_user)):
        # user=db.query(User).filter(User.id==id).first()
        statement = select(User).options(selectinload(User.posts)).filter(User.id == id)
        result = await db.execute(statement)

        user = result.scalars().first()
        if user is None:
                raise HTTPException(status_code=404,detail='User Not Found')
        
        return user

 

@router.put("/users/{id}",response_model = UserResponse)
async def update_user(id :int ,user : UserUpdate, db =Depends(get_db),current_user = Depends(get_current_user)):
        
        # user_updated = db.query(User).filter(User.id ==id).first()

        statement = select(User).filter(User.id == id)
        result = await db.execute(statement)
        user_updated = result.scalars().first()

        if user_updated is None:
                raise HTTPException(status_code=404,detail='User Not Found')
        if user_updated.id != current_user.id:
                raise HTTPException(
                status_code=403,
                detail="You can only update your own account"
                 )        
        user_updated.name = user.name
        user_updated.email = user.email
        await db.commit()
        await db.refresh(user_updated)
        return user_updated

@router.patch("/users/{id}",response_model=UserResponse)
async def update_user_partially(id:int,user : UserUpdatePatch,db=Depends(get_db),current_user = Depends(get_current_user)):

        # user_updated = db.query(User).filter(User.id == id).first()
        statement = select(User).options(selectinload(User.posts)).filter(User.id == id)

        result = await db.execute(statement)

        user_updated = result.scalars().first()

        if user_updated is None:
                raise HTTPException(status_code=404,detail="User not found")
        if user_updated.id != current_user.id:
                raise HTTPException(
                status_code=403,
                detail="You can only update your own account"
                 )
        
        user_update = user.model_dump(exclude_unset=True)

        for key,value in user_update.items():
                setattr(user_updated,key,value)

        await db.commit()
        await db.refresh(user_updated, attribute_names=["posts"])
        return user_updated

@router.delete("/users/{id}")
async def delete_user(id :int,db = Depends(get_db),current_user = Depends(get_current_user)):

        # user_deleted = db.query(User).filter(User.id == id).first()
        statement = select(User).filter(User.id == id)
        result = await db.execute(statement)
        user_deleted = result.scalars().first()
        if user_deleted is None:
                raise HTTPException(status_code=404,detail='User Not Found')
        await db.delete(user_deleted)
        await db.commit()
        return{
                "Message": "User deleted successfully"
        }


######################## Deleting User's Post

@router.delete("/users/{id}/posts/{post_id}")
async def delete_post(id : int , post_id :int,db = Depends(get_db),current_user = Depends(get_current_user)):
        # user_details = db.query(User).filter(User.id == id).filter(current_user.id == User.id).first()
        statement = select(User).filter(User.id == id).filter(current_user.id == User.id)
        result  = await db.execute(statement)

        user_details = result.scalars().first()

        if user_details is None:
                raise HTTPException(status_code=404, detail="User not found")

        # post_details = db.query(Post).filter(Post.id == post_id).filter(User.id == user_details.id).first()
        statement2 = select(Post).filter(Post.id == post_id).filter(User.id == user_details.id)
        result2 = await db.execute (statement2)

        post_details = result2.scalars().first()

        if post_details is None:
                raise HTTPException(status_code= 404,detail="Post not found")

        user_details.posts.remove(post_details)
        await db.commit()
        return {
                "Message" : "Post deleted successfully"
        }