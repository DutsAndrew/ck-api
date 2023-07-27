from pydantic import BaseModel, Field
from typing import Optional, List

# Color Preferences should have color schemes for the following:
## teams can be set to a color, this will apply to all calendars, tasks under that team, etc
## user can be set to a color that user's calendar and personal tasks/notes will take that color
## chats can be set be the user to a preferred scheme
## events can have their own colors set, it will change for all that share the same name


class ColorScheme(BaseModel):
    apply_to_which_object_ids: Optional[str]
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

class UserColorPreferences(BaseModel):
    calendars: List[ColorScheme] = Field(default_factory=list, required=True)
    chats: List[ColorScheme] = Field(default_factory=list, required=True)
    events: List[ColorScheme] = Field(default_factory=list, required=True)
    teams: List[ColorScheme] = Field(default_factory=list, required=True)
    user: ColorScheme