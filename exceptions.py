import fastapi


INCORRECT_LOGIN_DATA_EXCEPTION = fastapi.HTTPException(
    detail='Неверные данные для входа.',
    status_code=400,
)

INCORRECT_REGISTRATION_DATA_EXCEPTION = fastapi.HTTPException(
    detail='Неверные данные для регистрации.',
    status_code=405,
)

USER_ALREADY_REGISTERED_EXCEPTION = fastapi.HTTPException(
    detail='Данный пользователь уже зарегистрирован.',
    status_code=405,
)

PASSWORD_INVALID = fastapi.HTTPException(
    detail='Неверный старый пароль!',
    status_code=400,
)

INCOMING_HISTORY_NOT_FOUND = fastapi.HTTPException(
    detail='Данные о запрашиваемой записи не были найдены.',
    status_code=404,
)
