import fastapi
import models
import auth
import typing
import exceptions
import serializers
from fastapi.security import OAuth2PasswordRequestForm

router = fastapi.APIRouter(
    prefix='/users',
    tags=['Пользователи'],
)


async def check_for_username_availability(username: str):
    result_check = await models.User.objects.filter(username=username).exists()
    return bool(result_check)


@router.get('/')
async def get_users():
    users_queryset = models.User.objects.select_all(False)
    return await users_queryset.all()


@router.get('/me/', name='Получить авторизованного пользователя')
async def get_me(user: auth.UserType):
    return user


@router.post('/token/', name='Получение токена авторизации')
async def get_token_endpoint(form_data: typing.Annotated[OAuth2PasswordRequestForm, fastapi.Depends()]):
    """
    Генерирует Bearer-токен для авторизации.
    """

    if not form_data:
        raise exceptions.INCORRECT_LOGIN_DATA_EXCEPTION

    user = await auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise exceptions.INCORRECT_LOGIN_DATA_EXCEPTION

    return {'user': user, 'token': auth.create_token(user)}


@router.post('/register/', name='Регистрация пользователя')
async def register_user_endpoint(form_data: serializers.UserRegistrationSerializer):
    """
    Регистрирует пользователя в БД.
    """

    if not form_data:
        raise exceptions.INCORRECT_REGISTRATION_DATA_EXCEPTION

    if await check_for_username_availability(form_data.username):
        raise exceptions.USER_ALREADY_REGISTERED_EXCEPTION

    created_user = await models.User.objects.create(
        **form_data.model_dump()
    )

    return created_user


@router.post('/registration/username/{username}/', name='Проверка username на регистрацию')
async def validate_registration_email_endpoint(username: str):
    """
    Проверка username на его занятость другим пользователем.
    Данная функция нужна для валидации поля username на клиенте.
    """

    if not await check_for_username_availability(username):
        return {'detail': False}

    return {'detail': True}


@router.post('/change-password/', name='Изменить пароль для авторизованного пользователя')
async def change_user_password(
        user: auth.UserType,
        form_data: serializers.UserPasswordChangeSerializer
):
    old_password, new_password = form_data.old_password, form_data.new_password

    user_password = user.password
    if not auth.verify_password(old_password, user_password):
        raise exceptions.PASSWORD_INVALID

    await user.update(password=new_password)

    return user


@router.post('/edit', name='Редактировать профиль пользователя')
async def change_user_profile(
        user: auth.UserType,
        form_data: serializers.UserUpdateSerializer
):
    form_data_dumped = form_data.model_dump(
        exclude_unset=True,
        exclude_defaults=True,
    )

    await user.update(**form_data_dumped)
    return user
