import logging
import os

from aloha_api.enrollment_enums import AgenticAction, ImageSource
from aloha_api.social_poster_with_generated_image import SocialPosterWithGeneratedImage
from aloha_api.enrollments import Enrollments

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)

api_key = os.environ.get("ALOHA_INTERNAL_API_KEY")
if not api_key:
    logging.info('no api key provided')
    exit(1)

enrollments = Enrollments(api_key)
social_poster = SocialPosterWithGeneratedImage(api_key)

if not enrollments:
    logging.error("unable to initiate enrollments")
    exit(1)

if not social_poster:
    logging.error("unable to initiate social_poster")
    exit(1)


logging.info('starting social poster enrollments')
social_generated_image_enrollments = enrollments.get_active_enrollments(AgenticAction.PostSocialMedia, ImageSource.Generate)
if not social_generated_image_enrollments:
    logging.error('No enrollments')
    exit(1)


social_enrollment = None
for enrollment in social_generated_image_enrollments:
    client_id = enrollment.get_client_id()
    if client_id is None:
        logging.error('missing client_id')
        exit(1)
    if client_id.lower() == 'bb28f8a9-a43e-433b-b966-657ba998921e':
        social_enrollment = enrollment.to_social_enrollment()
        break

if social_enrollment is None:
    logging.error("oops, not test account")
    exit(1)

social_poster.execute_for_client(social_enrollment)

logging.info('social poster with generated image complete')
