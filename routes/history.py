import fastapi

import auth
import exceptions
import models
import serializers

router = fastapi.APIRouter(
    prefix='/history',
    tags=['История записей'],
)


@router.get('/')
async def get_records(user: auth.UserType):
    return await models.IncomingHistory.objects.filter(
        from_user=user
    ).all()


@router.put('/create')
async def create_record(
    user: auth.UserType,
    form_data: serializers.IncomingCreateSerializer
):
    form_data_dumped = form_data.model_dump()

    record = await models.IncomingHistory.objects.create(
        **form_data_dumped,
        from_user=user,
    )

    return record


@router.delete('/{incoming_id}/')
async def remove_incoming(
    user: auth.UserType,
    incoming_id: int,
):
    record = await models.IncomingHistory.objects.get_or_none(
        from_user=user,
        id=incoming_id,
    )

    if not record:
        raise exceptions.INCOMING_HISTORY_NOT_FOUND

    await record.delete()

    return record



