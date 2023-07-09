"""
This module defines Pydantic models for validating a YAML configuration file containing 
API keys and settings for various services such as OpenAI, Twilio, etc. Must define 
a final Keys model class which has class variables for each service, and each service
is a BaseModel class with the keys (and private settings) for that service.
"""
from pydantic import BaseModel


class Keys(BaseModel):
    """Overall keys."""
