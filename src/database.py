import pandas as pd
import os
from sqlalchemy import create_engine,text
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

DB_URL=os.getenv("DB_URL")
PROCESSED_DATA_PATH=Path("src/processed/indian_movies_clean.json")