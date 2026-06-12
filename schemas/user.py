"""
User schemas module.

IMPROVEMENTS:
- Separates request and response schemas (security: never return passwords)
- Adds email validation
- Adds password strength validation
- Uses Pydantic v2 features
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="User name")
    email: EmailStr = Field(..., description="User email address")


class UserCreate(UserBase):
    """
    Schema for creating a user.

    Used for POST requests.
    """

    password: str = Field(
        ..., min_length=8, max_length=100, description="User password (minimum 8 characters)"
    )

    # Pydantic v2 configuration
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "password": "securepassword123",
            }
        }
    )


class UserUpdate(BaseModel):
    """
    Schema for updating a user.

    All fields are optional for partial updates.
    """

    name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8, max_length=100)


class UserResponse(UserBase):
    """
    Schema for user responses.

    ⚠️ SECURITY: Never includes password field.
    Used for GET requests.
    """

    id: int = Field(..., description="User ID")

    # Pydantic v2 configuration
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {"id": 1, "name": "John Doe", "email": "john.doe@example.com"}
        },
    )


# Legacy schema for backward compatibility (deprecated)
class User(BaseModel):
    """
    ⚠️ DEPRECATED: Use UserCreate for creation and UserResponse for responses.
    This schema is kept for backward compatibility but should not be used in new code.
    """

    id: int | None = None
    name: str
    email: str
    password: str  # ⚠️ WARNING: Never return this in API responses


class UserCount(BaseModel):
    """Schema for user count response."""

    total: int = Field(..., description="Total number of users")

    # Pydantic v2 configuration
    model_config = ConfigDict(json_schema_extra={"example": {"total": 42}})
