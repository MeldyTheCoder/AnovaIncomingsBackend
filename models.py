import enum
import ormar
import sqlalchemy
import databases
import sqlalchemy_utils
from datetime import datetime
from typing import Union, Set, Dict, Type, Optional
import pydantic
import settings

if not sqlalchemy_utils.database_exists(settings.DATABASE_URL):
    sqlalchemy_utils.create_database(settings.DATABASE_URL)

engine = sqlalchemy.create_engine(url=settings.DATABASE_URL)
metadata = sqlalchemy.MetaData(bind=engine)
database = databases.Database(settings.DATABASE_URL)

ormar_config = ormar.OrmarConfig(
    metadata=metadata,
    database=database,
)


class IncomingHistoryTypes(enum.Enum):
    INCOMING = 'incoming'
    OUTCOMING = 'outcoming'


class IncomingCategories(enum.Enum):
    SUPERMARKETS = 'supermarkets'
    GAMES = 'games'
    TAXI = 'taxi'
    HOUSE = 'house'
    MARKETPLACES = 'marketplaces'
    ANOTHER = 'another'
    ANIMALS = 'animals'
    TRANSFERS = 'transfers'
    DEPOSIT = 'deposit'
    WITHDRAWAL = 'withdrawal'
    PURCHASE_RETURN = 'purchase_return'


class PartialMixin:
    """
    Mixin для создания сериализаторов без обязательных полей
    для возможности обновления данных без валидации.
    """

    @classmethod
    def get_pydantic_partial(
            cls,
            *,
            include: Union[Set, Dict, None] = None,
            exclude: Union[Set, Dict, None] = None,
    ) -> Type[pydantic.BaseModel]:
        model = cls.get_pydantic(include=include, exclude=exclude)

        new_fields = {
            name: (Optional[model.__annotations__.get(name)], None)
            for name in model.__fields__
        }

        new_model = pydantic.create_model(f"Partial{cls.__name__}", **new_fields)
        return new_model


class User(PartialMixin, ormar.Model):
    """
    Модель пользователя
    """

    ormar_config = ormar_config.copy(
        tablename='users',
    )

    id = ormar.BigInteger(
        minimum=1,
        nullable=False,
        primary_key=True,
        autoincrement=True,
    )

    username = ormar.String(
        max_length=50,
        regex="^[a-zA-Z0-9_.-]+$",
        min_length=3,
        nullable=False,
    )

    password = ormar.String(
        max_length=256,
        encrypt_secret=settings.SECRET,
        encrypt_backend=ormar.EncryptBackends.HASH,
        nullable=False,
    )

    email = ormar.String(
        min_length=5,
        max_length=255,
        regex=r'[\w.-]+@[\w.-]+.\w+',
        nullable=False,
    )

    date_joined = ormar.DateTime(
        default=datetime.now,
        nullable=False,
    )


class IncomingHistory(PartialMixin, ormar.Model):
    ormar_config = ormar_config.copy(
        tablename='history'
    )

    id = ormar.BigInteger(
        minimum=1,
        nullable=False,
        primary_key=True,
        autoincrement=True,
    )

    title = ormar.String(
        max_length=50,
        nullable=False,
    )

    category = ormar.Enum(
        nullable=False,
        enum_class=IncomingCategories,
    )

    type = ormar.Enum(
        nullable=False,
        enum_class=IncomingHistoryTypes,
    )

    price = ormar.Integer(
        minimum=1,
        nullable=False,
    )

    date = ormar.DateTime(
        default=datetime.now,
        nullable=False,
    )

    from_user = ormar.ForeignKey(
        to=User,
        nullable=False,
        on_delete=ormar.ReferentialAction.CASCADE,
        on_upadte=ormar.ReferentialAction.CASCADE,
    )


metadata.create_all(bind=engine)
