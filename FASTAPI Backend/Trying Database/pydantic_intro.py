import re
from typing import List
from pydantic import BaseModel, Field, ValidationError, field_validator, EmailStr

# A mocked list of blacklisted or disposable domains for production safety
DISPOSABLE_DOMAINS = {"mailinator.com", "yopmail.com", "trashmail.com"}

class UserRegistration(BaseModel):
    # 1. Field manages basic limits, descriptions, and example data for API docs
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=20, 
        pattern=r"^[a-zA-Z0-9_]+$",
        description="A unique alphanumeric username."
    )
    email: EmailStr = Field(..., description="Primary user email address.")
    age: int = Field(..., gt=18, le=120, description="User must be an adult.")
    roles: List[str] = Field(default=["viewer"], description="Assigned application permissions.")

    # 2. Before Validator: Cleans and standardizes input before Pydantic processes it
    @field_validator("email", mode="before")
    @classmethod
    def clean_email_string(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip().lower()
        return value

    # 3. After Validator: Enforces strict infrastructure/security constraints
    @field_validator("email", mode="after")
    @classmethod
    def reject_disposable_emails(cls, value: EmailStr) -> EmailStr:
        # Extract domain safely
        domain = value.split("@")[-1]
        if domain in DISPOSABLE_DOMAINS:
            raise ValueError("Registration using disposable email addresses is forbidden.")
        return value

    # 4. Multi-field structural cleanup
    @field_validator("roles", mode="after")
    @classmethod
    def normalize_roles(cls, roles: List[str]) -> List[str]:
        # Deduplicate and force lower-case for database compatibility
        return list(set(role.strip().lower() for role in roles))

try:
    # Simulating a payload with a bad domain, invalid username characters, and a trailing space in email
    bad_payload = {
        "username": "admin user!",       # Invalid spaces and characters
        "email": " TEST@mailinator.com ", # Spaces will be stripped, but domain is blacklisted
        "age": 16,                        # Underaged constraint failure
        "roles": ["Admin", "admin "]     # Will be normalized if other fields pass
    }
    UserRegistration(**bad_payload)
except ValidationError as e:
    # Production logging architectures can directly ingest this JSON format
    print(e.json(indent=2))