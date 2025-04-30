import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

from handlers import router


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_WEBHOOK_URL = os.getenv("BASE_WEBHOOK_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", 5000))
WEB_SERVER_HOST = os.getenv("WEB_SERVER_HOST", "0.0.0.0")


logging.basicConfig(level=logging.INFO)


async def set_bot_commands(bot: Bot):
    """Set default bot commands."""
    commands = [
        BotCommand(command="/start", description="Start"),
        BotCommand(command="/menu", description="Subscriptions menu"),
    ]
    await bot.set_my_commands(commands)


async def on_startup(app: web.Application):
    """Webhook: on server startup."""
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
    """Webhook: on server shutdown."""
    logging.info("Removing webhook...")
    await app["bot"].delete_webhook()


async def health_check(request):
    """Health check endpoint."""
    return web.Response(status=200, text="Healthy")


def main():
    try:
        bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp = Dispatcher()
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

    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped manually or by the system.")
    except Exception as e:
        logging.exception("An unexpected error occurred:")
    finally:
        logging.info("Shutting down the server.")


if __name__ == "__main__":
    main()
