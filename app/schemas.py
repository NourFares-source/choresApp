from pydantic import BaseModel , EmailStr , Field , ConfigDict
from typing import List , Optional
from datetime import datetime 


#Parent Schemas 

class ParentCreate(BaseModel):
    email : EmailStr
    fullName : str = Field(...,min_length = 4 , max_length = 50)
    password : str = Field(...,min_length = 10 , max_length=50)
    username : str = Field(...,min_length= 8 , max_length= 20)

class ParentResponse(BaseModel):
    id : int
    email : EmailStr
    username : str
    created_at : datetime
    model_config = ConfigDict(from_attributes=True)

#Child Schemas 

class ChildCreate(BaseModel):
    email : EmailStr
    fullName : str = Field(...,min_length = 4 , max_length = 50)
    childUsername :str = Field(...,min_length = 8 , max_length = 20)
    password : str = Field(...,min_length = 10 , max_length=50)
    parent_username : str = Field(...,min_length = 8 , max_length = 20)


class ChildResponse(BaseModel):
    id : int
    email : EmailStr
    username : str
    created_at : datetime
    parent_id : int
    model_config = ConfigDict(from_attributes=True)

#Task Schemas 

class TaskCreate(BaseModel):
    title : str = Field(...,min_length = 4 , max_length = 50)
    description : str = Field(... , max_length = 200)
    timer : int #hours or minutes to add to the created_at field so we get the due time 
    childUsername : str = Field(...,min_length = 8 , max_length = 20)
    

class TaskResponse(BaseModel):
    id : int 
    child_id : int 
    title : str    
    description : str
    due_time : datetime #calculated 
    status : str = "uncompleted"
    created_at : datetime
    model_config = ConfigDict(from_attributes=True)


class ReportResponse(BaseModel):
    id : int 
    child_id : int
    created_at : datetime
    notes : str 
    evaluation : float
    model_config = ConfigDict(from_attributes=True)    
        

class LoginRequest(BaseModel):
    email: EmailStr
    password: str