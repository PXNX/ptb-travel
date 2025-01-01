import os
from json import loads
from typing import Final, List

from dotenv import load_dotenv

load_dotenv()

TOKEN: Final[str] = os.getenv('TELEGRAM')
PORT: Final[int] = int(os.getenv("PORT", 8080))


LOG_GROUP: Final[str] = os.getenv('LOG_GROUP')
ADMINS: Final[List[str]] = loads(os.getenv('ADMINS'))




