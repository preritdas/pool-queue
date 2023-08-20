"""
This module defines Pydantic models for validating a YAML configuration file containing 
API keys and settings for various services such as OpenAI, Twilio, etc. Must define 
a final Keys model class which has class variables for each service, and each service
is a BaseModel class with the keys (and private settings) for that service.
"""
from pydantic import BaseModel


# Keys needed at least for Twilio and for OpenAI.


class MongoDBModel(BaseModel):
    """Credentials to connect to Pool Queue project and database."""
    connect_str: str


class Keys(BaseModel):
    """Overall keys."""
    MongoDB: MongoDBModel
