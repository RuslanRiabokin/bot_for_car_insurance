import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from ai_handler import router
#from aaaaaaaaaaaaaaa import router
from config import (BOT_TOKEN, BASE_WEBHOOK_URL, WEBHOOK_SECRET,
                    WEBHOOK_PATH, WEBHOOK_PORT, WEB_SERVER_HOST)
from aiogram.fsm.storage.memory import MemoryStorage

dp = Dispatcher(storage=MemoryStorage())


logging.basicConfig(level=logging.INFO)
logging.getLogger("fontTools").setLevel(logging.WARNING)


async def set_bot_commands(bot: Bot):
    """Set the default list of bot commands shown in the menu."""
    commands = [
        BotCommand(command="start", description="ШІ помічник")
    ]
    await bot.set_my_commands(commands)


async def on_startup(app: web.Application):
    """Execute tasks when the webhook server starts."""
    logging.info("Setting webhook...")
    await app["bot"].delete_webhook(drop_pending_updates=True)
    await app["bot"].set_webhook(
        url=f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
        secret_token=WEBHOOK_SECRET,
        allowed_updates=["message", "callback_query"]
    )
    await set_bot_commands(app["bot"])
    logging.info("Webhook successfully set.")


async def on_shutdown(app: web.Application):
    """Execute tasks when the webhook server shuts down."""
    logging.info("Removing webhook...")
    await app["bot"].delete_webhook()


async def health_check(request):
    """Health check endpoint to confirm server is running."""
    return web.Response(status=200, text="Healthy")


def main():
    """Main entry point: initialize and run the webhook server."""
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    app = web.Application()
    app["bot"] = bot

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/health", health_check)

    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    logging.info(f"Server starting on {WEB_SERVER_HOST}:{WEBHOOK_PORT}")
    web.run_app(app, host=WEB_SERVER_HOST, port=WEBHOOK_PORT)


if __name__ == "__main__":
    main()