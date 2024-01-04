from pydantic import BaseModel, Field
from typing import Optional, List

# Color Preferences should have color schemes for the following:
## teams can be set to a color, this will apply to all calendars, tasks under that team, etc
## user can be set to a color that user's calendar and personal tasks/notes will take that color
## chats can be set be the user to a preferred scheme
## events can have their own colors set, it will change for all that share the same name

class UserColorScheme(BaseModel):
    font_color: Optional[str]
    background_color: Optional[str]

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "font_color": "#37D9C8",
                "background_color": "rgb(55, 217, 200)"
            }
        }
    }


class ColorScheme(BaseModel):
    object_id: Optional[str]
    background_color: Optional[str]


class UserColorPreferences(BaseModel):
    calendars: List[ColorScheme] = Field(default_factory=list)
    chats: List[ColorScheme] = Field(default_factory=list)
    teams: List[ColorScheme] = Field(default_factory=list)
    user: UserColorScheme = Field(default_factory=lambda: UserColorScheme(
        font_color=None,
        background_color=None,
    ))

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "calendars": [
                    {
                        "object_id": "calendar_id_1",
                        "background_color": "rgb(255, 0, 0)"
                    },
                    {
                        "object_id": "calendar_id_2",
                        "background_color": "rgb(0, 0, 255)"
                    }
                ],
                "chats": [
                    {
                        "object_id": "chat_id_1",
                        "background_color": "rgb(0, 255, 0)"
                    },
                    {
                        "object_id": "chat_id_2",
                        "background_color": "rgb(0, 255, 0)"
                    }
                ],
                "events": [
                    {
                        "object_id": "event_id_1",
                        "background_color": "rgb(255, 255, 0)"
                    },
                    {
                        "object_id": "event_id_2",
                        "background_color": "rgb(255, 255, 0)"
                    }
                ],
                "teams": [
                    {
                        "object_id": "team_id_1",
                        "background_color": "rgb(255, 0, 255)"
                    },
                    {
                        "object_id": "team_id_2",
                        "background_color": "rgb(255, 0, 255)"
                    }
                ],
                "user": {
                    "background_color": "#FFFFFF"
                },
            }
        }
    }