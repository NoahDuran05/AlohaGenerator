from enum import Enum

class AgenticAction(Enum):
    Unknown = 0
    PostSocialMedia = 1
    SendEmail = 2
    PostBlogEntry = 3

class ImageSource(Enum):
    Unknown = 0
    NONE = 1
    Gallery = 2
    Generate = 3

class OptionType(Enum):
    Unknown = 0
    FacebookPage = 1
    LinkedInPage = 2
    ImagePromptTemplate = 3
    TextPromptTemplate = 4
    SchedulingPromptTemplate = 5
    Author = 6
    Password = 7
    Username = 8
    Website = 9
    BlogPostStatus = 10

class SocialPlatform(Enum):
    Unknown = 0
    Facebook = 1
    Instagram = 2
    LinkedIn = 3

def string_to_social_platform(s: str) -> SocialPlatform:
    if s is None:
        return SocialPlatform.Unknown

    for p in SocialPlatform:
        if p.name.lower() == s.lower():
            return p
    return SocialPlatform.Unknown
