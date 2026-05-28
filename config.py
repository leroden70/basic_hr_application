from dotenv import dotenv_values
from pathlib import Path

curpath = str(Path(__file__).parent)
config = dotenv_values(curpath + "/database.ini")

