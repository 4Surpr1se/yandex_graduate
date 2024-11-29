from enum import Enum


class ChannelType(Enum):
    EMAIL = 1
    BROWSER = 2


class NotificationType(Enum):
    MASS_MAILING = 1
    WEEKLY_REPORT = 2
    REGISTRATION = 3
    BILLING = 4
