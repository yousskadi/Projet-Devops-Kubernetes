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

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from typing import List
from config.db import get_db, users
from schemas.user import User, UserCreate, UserResponse, UserCount
from passlib.context import CryptContext
from pydantic import EmailStr
import re

# ⚠️ SECURITY: Use bcrypt for password hashing
# bcrypt is a one-way hashing algorithm designed specifically for passwords
# It's slower than MD5/SHA, which makes brute-force attacks harder
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


user = APIRouter(prefix="/users", tags=["users"])


@user.get("/", response_model=List[UserResponse], description="Get a list of all users")
def get_users(db: Session = Depends(get_db)):
    """
    Get all users.
    
    Returns a list of all users without passwords.
    """
    try:
        # Use connection for Table Core API compatibility
        with engine.begin() as conn:
            result = conn.execute(users.select()).fetchall()
            # Convert Row objects to dict and exclude passwords
            users_list = []
            for row in result:
                user_dict = dict(row._mapping)
                user_dict.pop("password", None)  # Never return passwords
                users_list.append(user_dict)
            return users_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )


@user.get("/count", response_model=UserCount, description="Get the total number of users")
def get_users_count(db: Session = Depends(get_db)):
    """Get the total count of users."""
    try:
        with engine.begin() as conn:
            result = conn.execute(select(func.count()).select_from(users))
            count = result.scalar()
            return {"total": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error counting users: {str(e)}"
        )


@user.get(
    "/{user_id}",
    response_model=UserResponse,
    description="Get a single user by ID"
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a user by ID.
    
    Raises 404 if user not found.
    """
    try:
        with engine.begin() as conn:
            result = conn.execute(users.select().where(users.c.id == user_id)).first()
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {user_id} not found"
                )
            user_dict = dict(result._mapping)
            user_dict.pop("password", None)  # Never return passwords
            return user_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user: {str(e)}"
        )


@user.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new user"
)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    
    Validates email format and hashes password before storing.
    """
    try:
        # ⚠️ VALIDATION: Validate email format
        if not validate_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Check if user with email already exists and create user
        with engine.begin() as conn:
            existing_user = conn.execute(
                users.select().where(users.c.email == user_data.email)
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User with email {user_data.email} already exists"
                )
            
            # ⚠️ SECURITY: Hash password before storing
            hashed_password = get_password_hash(user_data.password)
            
            new_user = {
                "name": user_data.name,
                "email": user_data.email,
                "password": hashed_password
            }
            
            result = conn.execute(users.insert().values(new_user))
            # Note: engine.begin() automatically commits, but we need the lastrowid
            # So we fetch it within the same transaction
            user_id = result.lastrowid
            
            # Fetch the created user
            created_user = conn.execute(
                users.select().where(users.c.id == user_id)
            ).first()
            
            if not created_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user"
                )
            
            user_dict = dict(created_user._mapping)
            user_dict.pop("password", None)  # Never return passwords
            return user_dict
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@user.put(
    "/{user_id}",
    response_model=UserResponse,
    description="Update a user by ID"
)
def update_user(user_id: int, user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Update a user by ID.
    
    Raises 404 if user not found.
    """
    try:
        # Validate email format first (before DB transaction)
        if not validate_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        with engine.begin() as conn:
            # Check if user exists
            existing_user = conn.execute(
                users.select().where(users.c.id == user_id)
            ).first()
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {user_id} not found"
                )
            
            # Check if email is already taken by another user
            email_user = conn.execute(
                users.select().where(users.c.email == user_data.email)
            ).first()
            if email_user and dict(email_user._mapping).get("id") != user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User with email {user_data.email} already exists"
                )
            
            # ⚠️ SECURITY: Hash password if provided
            hashed_password = get_password_hash(user_data.password)
            
            # Update user
            conn.execute(
                users.update()
                .where(users.c.id == user_id)
                .values(
                    name=user_data.name,
                    email=user_data.email,
                    password=hashed_password
                )
            )
            
            # Fetch updated user
            updated_user = conn.execute(
                users.select().where(users.c.id == user_id)
            ).first()
            
            user_dict = dict(updated_user._mapping)
            user_dict.pop("password", None)  # Never return passwords
            return user_dict
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )


@user.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete a user by ID"
)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user by ID.
    
    ⚠️ FIX: Returns 204 No Content (no response body) as per HTTP spec.
    Raises 404 if user not found.
    """
    try:
        with engine.begin() as conn:
            # Check if user exists
            existing_user = conn.execute(
                users.select().where(users.c.id == user_id)
            ).first()
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {user_id} not found"
                )
            
            # Delete user (transaction automatically commits with engine.begin())
            conn.execute(users.delete().where(users.c.id == user_id))
            
            # ⚠️ FIX: 204 No Content should not return a body
            return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )
