from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class ChatCreateSchema(BaseModel):
    agent_id: int
    name: str
    content: str


class ChatCreateResponseSchema(BaseModel):
    chat_id: int


class ChatUpdateSchema(BaseModel):
    user_id: int
    agent_id: int
    name: str


class MessageUpdateSchema(BaseModel):
    content: str


class MessageVariationCreateSchema(BaseModel):
    message_id: int
    content: str


class MessageVariationReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    message_id: int
    content: str


class MessageCreateSchema(BaseModel):
    chat_id: int
    content: str
    variations: List[MessageVariationReadSchema]


class MessageReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    chat_id: int
    content: str
    variations: List[MessageVariationReadSchema]


class ChatReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    user_id: int
    agent_id: int
    messages: Optional[List[MessageReadSchema]]


class MessageVariationUpdateSchema(BaseModel):
    content: str
