from typing import List

from .enrollment_enums import SocialPlatform


def to_supported_platforms(text_dictionary: dict, property_type:str, platforms:List[SocialPlatform] = None) -> List[SocialPlatform]:
    if not text_dictionary:
        return []

    if not platforms:
        platforms = [SocialPlatform.LinkedIn, SocialPlatform.Facebook, SocialPlatform.Instagram]

    supported_platforms = []
    for platform in platforms:
        platform_name = platform.name.lower()
        social_scenario_key = f'{platform_name}_{property_type}'
        if social_scenario_key in text_dictionary:
            supported_platforms.append(platform)

    return supported_platforms

