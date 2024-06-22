import pydantic
import models


UserRegistrationSerializer = models.User.get_pydantic(
    include={
        'username',
        'password',
        'email'
    }
)

UserLoginSerializer = models.User.get_pydantic(
    include={
        'username',
        'password',
    }
)

UserUpdateSerializer = models.User.get_pydantic_partial(
    include={
        'username',
        'password',
        'email',
    }
)


class UserPasswordChangeSerializer(pydantic.BaseModel):
    old_password: str
    new_password: str


IncomingCreateSerializer = models.IncomingHistory.get_pydantic(
    include={
        'title',
        'price',
        'category',
        'type',
    }
)