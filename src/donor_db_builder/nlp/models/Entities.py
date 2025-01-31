# from typing import List
# from pydantic import BaseModel, Field
#
# from relik import Relik
# from relik.inference.data.objects import RelikOutput
# from llama_index.llms.openai import OpenAI
#
#
# class Donor(BaseModel):
#     """
#     Represents a donor of campaign contributions
#     """
#
#     name: str
#     type: str  # 'Individual' or 'Organization'
#     address: str
#     city: str
#     state: str
#     zip: str
