from pydantic import BaseModel
from typing import Optional

class ColorScheme(BaseModel):
    font_color: Optional[str]
    background_color: Optional[str]

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "font_color": "#37D9C8",
                "background_color": "rgb(55, 217, 200)"
            }
        }