import enum


class AuthError(str, enum.Enum):
    PASSWORD_DOES_NOT_MATCH = "PASSWORD_DOES_NOT_MATCH"


class AccountError(str, enum.Enum):
    USER_DOES_NOT_EXIST = "USER_DOES_NOT_EXIST"


class AccountEmailTokenError(str, enum.Enum):
    TOKEN_DOES_NOT_EXIST = "TOKEN_DOES_NOT_EXIST"
    TOKEN_IS_EXPIRED = "TOKEN_IS_EXPIRED"
