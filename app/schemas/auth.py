"""
Authentication-related Pydantic schemas for API requests and responses
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class UserRegistrationRequest(BaseModel):
    """Schema for user registration request."""
    
    username: str = Field(..., min_length=3, max_length=80, description="Username for the account")
    password: str = Field(..., min_length=6, max_length=100, description="Password for the account")
    
    @validator("username")
    def validate_username(cls, v):
        """Validate username format."""
        if not v.strip():
            raise ValueError("Username cannot be empty or whitespace only")
        
        # Check for valid characters (alphanumeric, underscore, hyphen)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v.strip()):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        
        return v.strip().lower()
    
    @validator("password")
    def validate_password(cls, v):
        """Validate password strength."""
        if not v or len(v.strip()) < 6:
            raise ValueError("Password must be at least 6 characters long")
        
        # Check for at least one letter and one number
        import re
        if not re.search(r'[a-zA-Z]', v) or not re.search(r'\d', v):
            raise ValueError("Password must contain at least one letter and one number")
        
        return v


class UserLoginRequest(BaseModel):
    """Schema for user login request."""
    
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")
    
    @validator("username")
    def validate_username(cls, v):
        """Normalize username."""
        return v.strip().lower() if v else v


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: "UserResponse" = Field(..., description="User information")


class UserResponse(BaseModel):
    """Schema for user information response."""
    
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    is_admin: bool = Field(..., description="Whether user has admin privileges")
    is_active: bool = Field(..., description="Whether user account is active")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    
    class Config:
        from_attributes = True


class LogoutResponse(BaseModel):
    """Schema for logout response."""
    
    message: str = Field(default="Successfully logged out", description="Logout confirmation message")


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class PasswordChangeRequest(BaseModel):
    """Schema for password change request."""
    
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, max_length=100, description="New password")
    
    @validator("new_password")
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if not v or len(v.strip()) < 6:
            raise ValueError("New password must be at least 6 characters long")
        
        # Check for at least one letter and one number
        import re
        if not re.search(r'[a-zA-Z]', v) or not re.search(r'\d', v):
            raise ValueError("New password must contain at least one letter and one number")
        
        return v


# Update forward references
TokenResponse.model_rebuild()