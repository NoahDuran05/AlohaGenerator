
from .enrollment_enums import OptionType
from .social_enrollment import SocialEnrollment


class AgenticEnrollment:
    def __init__(self, json_response: dict):
        self.data = json_response
        self.options = self.data.get('options')

    def to_social_enrollment(self) -> SocialEnrollment:
        result = SocialEnrollment(
            client_id=self.get_client_id(),
            enrollment_id=self.get_enrollment_id(),
            scheduling_template_id=self.get_scheduling_template_id(),
            text_template_id=self.get_text_template_id(),
            image_template_id=self.get_image_template_id(),
            facebook_page=self.get_facebook_page(),
            linkin_page=self.get_linkedin_page()
        )
        return result


    def _get_option(self, template_type: OptionType) -> dict | None:
        if self.options is None:
            return None

        for o in self.options:
            option_type = o.get('type')
            if option_type is None:
                continue
            if option_type == template_type.name:
                return o

        return None

    def _get_option_value(self, option_type: OptionType) -> str | None:
        if self.options is None:
            return None
        option = self._get_option(option_type)
        if option is None:
            return None

        v = option.get('value')
        return v

    def _get(self, key: str) -> str | None:
        if self.data is None:
            return None
        return self.data.get(key)

    def get_client_id(self) -> str | None:
        return self._get('clientId')

    def get_enrollment_id(self) -> str | None:
        return self._get('enrollmentId')

    def get_facebook_page(self) -> str | None:
        return self._get_option_value(OptionType.FacebookPage)

    def get_linkedin_page(self) -> str | None:
        return self._get_option_value(OptionType.LinkedInPage)

    def get_image_template_id(self) -> str | None:
        return self._get_option_value(OptionType.ImagePromptTemplate)

    def get_text_template_id(self) -> str | None:
        return self._get_option_value(OptionType.TextPromptTemplate)

    def get_scheduling_template_id(self) -> str | None:
        return self._get_option_value(OptionType.SchedulingPromptTemplate)

    def get_author(self) -> str | None:
        return self._get_option_value(OptionType.Author)

    def get_password(self) -> str | None:
        return self._get_option_value(OptionType.Password)

    def get_username(self) -> str | None:
        return self._get_option_value(OptionType.Username)

    def get_website(self) -> str | None:
        return self._get_option_value(OptionType.Website)

    def get_blog_post_status(self) -> str | None:
        return self._get_option_value(OptionType.BlogPostStatus)

