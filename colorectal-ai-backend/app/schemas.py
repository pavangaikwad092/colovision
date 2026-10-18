from pydantic import BaseModel, EmailStr, Field
class RegisterIn(BaseModel): name: str; email: EmailStr; phone: str; username: str; password: str = Field(min_length=8)
class LoginIn(BaseModel): identifier: str; password: str
class PatientIn(BaseModel): patient_id: str; name: str; address: str; age: int = Field(ge=0, le=130); gender: str; contact: str
class TokenOut(BaseModel): access_token: str; token_type: str = "bearer"
