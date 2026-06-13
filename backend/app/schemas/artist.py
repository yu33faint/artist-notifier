from pydantic import BaseModel

class ArtistRequest(BaseModel):
    artist_name: str
