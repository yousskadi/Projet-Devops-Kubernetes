"""
User routes module.

IMPROVEMENTS:
- Uses bcrypt for password hashing (secure, one-way hashing)
- Implements proper error handling with HTTPException
- Uses dependency injection for database sessions
- Validates email format
- Proper HTTP status codes
- Input validation and sanitization
"""

import re

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, insert, select
from sqlalchemy.orm import Session

from config.db import get_db
from models.user import users
from schemas.user import UserCount, UserCreate, UserResponse


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bool(bcrypt.checkpw(plain_password.encode(), hashed_password.encode()))


def get_password_hash(password: str) -> str:
    return str(bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode())


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


user = APIRouter(prefix="/users", tags=["users"])


@user.get("/", response_model=list[UserResponse], description="Get a list of all users")
def get_users(db: Session = Depends(get_db)):
    try:
        result = db.execute(select(users)).all()
        users_list = []
        for row in result:
            user_dict = dict(row._mapping)
            user_dict.pop("password", None)
            users_list.append(user_dict)
        return users_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}",
        ) from e


@user.get("/count", response_model=UserCount, description="Get the total number of users")
def get_users_count(db: Session = Depends(get_db)):
    try:
        count = db.execute(select(func.count()).select_from(users)).scalar()
        return {"total": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error counting users: {str(e)}",
        ) from e


@user.get("/{user_id}", response_model=UserResponse, description="Get a single user by ID")
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        result = db.execute(select(users).where(users.c.id == user_id)).first()
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found"
            )
        user_dict = dict(result._mapping)
        user_dict.pop("password", None)
        return user_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user: {str(e)}",
        ) from e


@user.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new user",
)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        if not validate_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format"
            )

        existing_user = db.execute(select(users).where(users.c.email == user_data.email)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email {user_data.email} already exists",
            )

        hashed_password = get_password_hash(user_data.password)
        new_user = {"name": user_data.name, "email": user_data.email, "password": hashed_password}

        stmt = insert(users).values(new_user).returning(users.c.id)
        result = db.execute(stmt)
        user_id = result.scalar()
        db.commit()

        created_user = db.execute(select(users).where(users.c.id == user_id)).first()
        if created_user is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User creation failed",
            )
        user_dict = dict(created_user._mapping)
        user_dict.pop("password", None)
        return user_dict

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
        ) from e


@user.put("/{user_id}", response_model=UserResponse, description="Update a user by ID")
def update_user(user_id: int, user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        if not validate_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format"
            )

        existing_user = db.execute(select(users).where(users.c.id == user_id)).first()
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found"
            )

        email_user = db.execute(select(users).where(users.c.email == user_data.email)).first()
        if email_user and dict(email_user._mapping).get("id") != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email {user_data.email} already exists",
            )

        hashed_password = get_password_hash(user_data.password)
        db.execute(
            users.update()
            .where(users.c.id == user_id)
            .values(name=user_data.name, email=user_data.email, password=hashed_password)
        )
        db.commit()

        updated_user = db.execute(select(users).where(users.c.id == user_id)).first()
        if updated_user is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User update failed",
            )
        user_dict = dict(updated_user._mapping)
        user_dict.pop("password", None)
        return user_dict

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}",
        ) from e


@user.delete(
    "/{user_id}", status_code=status.HTTP_204_NO_CONTENT, description="Delete a user by ID"
)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        existing_user = db.execute(select(users).where(users.c.id == user_id)).first()
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found"
            )

        db.execute(users.delete().where(users.c.id == user_id))
        db.commit()
        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}",
        ) from e
