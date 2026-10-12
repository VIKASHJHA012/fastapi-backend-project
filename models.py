from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column,Integer,String,ForeignKey,DATE,UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()

class User(Base):    
    __tablename__ ='users'
    id = Column(Integer,primary_key=True)
    name = Column(String,nullable=False)
    email = Column(String,nullable=False,unique=True)
    password = Column(String,nullable=False)
    posts = relationship("Post",back_populates="user", cascade="all, delete-orphan")
    

class Post(Base):
    __tablename__ ='post'
    id = Column(Integer,primary_key=True)
    title = Column(String,nullable=False)
    created=Column(DATE,nullable=False)
    # description = Column(String, nullable=True)
    user_id =Column(Integer,ForeignKey("users.id"),nullable=False)
    user = relationship("User",back_populates='posts')
    post_tag = relationship("PostTag",back_populates="post")
    tags = association_proxy("post_tag","tag")

class Tag(Base):
    __tablename__= 'tag'
    id =Column(Integer,primary_key=True)
    tag_name =Column(String,nullable=False)
    created = Column(DATE,nullable=False)
    post_tag = relationship("PostTag",back_populates="tag")

class PostTag(Base):
    __tablename__ =  'posttag'
    id = Column(Integer,primary_key=True)
    created =Column(DATE,nullable=False)
    tag_id = Column(Integer,ForeignKey("tag.id"),nullable=False)
    post_id =Column(Integer,ForeignKey("post.id"),nullable=False)
    __table_args__ = (
        UniqueConstraint(post_id,tag_id),
    )
    tag = relationship("Tag",back_populates="post_tag")
    post = relationship("Post",back_populates="post_tag")
