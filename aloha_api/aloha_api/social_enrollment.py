import pydantic
from typing import List, Optional

from aloha_api.enrollment_enums import SocialPlatform


class SocialEnrollment(pydantic.BaseModel):
    enrollment_id: str
    client_id: str
    scheduling_template_id: str
    text_template_id: str
    image_template_id: Optional[str] = None
    facebook_page: Optional[str] = None
    linkin_page: Optional[str] = None

    def to_page(self, platform: SocialPlatform) -> str | None:
        if platform == SocialPlatform.Facebook:
            return self.facebook_page
        elif platform == SocialPlatform.LinkedIn:
            return self.linkin_page
        else:
            return None


