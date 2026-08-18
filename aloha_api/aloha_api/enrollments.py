import logging
from typing import List

from .agentic_enrollment import AgenticEnrollment
from .end_points import EndPoints
from .base_http import BaseHttp
from .enrollment_enums import AgenticAction, ImageSource


class Enrollments(BaseHttp):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.end_points = EndPoints.from_api_key(api_key)

    @classmethod
    def from_api_key(cls, api_key: str):
        return cls(api_key)

    def get_active_enrollments(self, agentic_action: AgenticAction, image_source: ImageSource | None = None)\
            -> List[AgenticEnrollment]:

        function = '(aloha) Enrollments:get_active_enrollments'

        try:
            if not image_source:
               url = f'{self.end_points.social}/enrollment/active?action={agentic_action.name}'
            else:
               url = f'{self.end_points.social}/enrollment/active?action={agentic_action.name}&source={image_source.name}'

            json_result = self._get_json(url)
            if json_result is None:
                return []

            enrollments = []
            for d in json_result:
                enrollment = AgenticEnrollment(d)
                if enrollment.get_client_id() is None:
                    continue
                enrollments.append(enrollment)
            return enrollments
        except:
            logging.exception(f'{function}: failed to get enrollments for {agentic_action}, {image_source}')
            return []

    def get_enrollment_by_id(self, enrollment_id : str)  -> AgenticEnrollment | None:

        function = '(aloha) Enrollments:get_active_enrollments'

        try:
            url = f'{self.end_points.social}/enrollment/active/{enrollment_id}'
            json_result = self._get_json(url)
            if json_result is None:
                return None

            enrollment = AgenticEnrollment(json_result)
            return enrollment
        except:
            logging.exception(f'{function}: failed to get enrollment for {enrollment_id}')
            return None


