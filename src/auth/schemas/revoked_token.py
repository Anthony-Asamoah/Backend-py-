from datetime import datetime

from pydantic import BaseModel


class RevokedTokenRepoCreate(BaseModel):
    token: str
    expires_on: datetime
