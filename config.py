import os
from dotenv import load_dotenv
from sqlalchemy.engine import make_url

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET")
DATABASE_URL = os.getenv("DATABASE_URL")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


def prepare_async_url(url):
    if not url:
        return url

    parsed_url = make_url(url)

    if parsed_url.drivername == "postgresql":
        parsed_url = parsed_url.set(
            drivername="postgresql+asyncpg"
        )

    query = dict(parsed_url.query)

    # Convert Neon/libpq SSL parameter to asyncpg's SSL option.
    if "sslmode" in query:
        query["ssl"] = query.pop("sslmode")

    # asyncpg does not accept this libpq connection parameter.
    query.pop("channel_binding", None)

    return parsed_url.set(query=query)


DATABASE_URL = prepare_async_url(DATABASE_URL)