import fastapi
import uvicorn
import models
import settings
from routes import users, history

app = fastapi.FastAPI(
    title='Incomings Backend',
    description='Серверная часть для хранения информации о расходах и доходах пользователей.',
    debug=True,
    redirect_slashes=True
)


@app.on_event('startup')
async def on_startup():
    if not models.database.is_connected:
        await models.database.connect()


@app.on_event('shutdown')
async def on_shutdown():
    await models.database.disconnect()

app.include_router(users.router)
app.include_router(history.router)


if __name__ == '__main__':
    uvicorn.run(
        host=settings.HOST,
        port=settings.PORT,
        app=app,
    )

