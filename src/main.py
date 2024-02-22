import openai 
import os 


class RequestGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        