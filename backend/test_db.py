import os
from pathlib import Path
import logging

# Ensure python path works
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.db import get_db, upsert_guide, list_guides

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_firestore():
    logger.info("Testing Firestore connection...")
    
    # 1. Print credentials path
    logger.info(f"Using GCP Project ID: '{settings.gcp_project_id}'")
    logger.info(f"Using Firestore DB Name: '{settings.gcp_firestore_database}'")
    logger.info(f"Using Credentials: '{os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'NOT SET')}'")
    
    db = get_db()
    if not db:
        logger.error("Failed to initialize get_db(). Check credentials.")
        return
        
    logger.info("Firestore client initialized successfully!")
    
    # 2. Test Write
    logger.info("Attempting to write a test guide...")
    try:
        guide_id = upsert_guide(
            request_data={"topics": ["test_topic"], "style": "speed_run"},
            outline={"sections": [{"title": "Test Section", "topic": "test_topic"}]},
            sections_content=["Hello World!"],
            sections_code=["print('Hello')"],
            guide_id=None
        )
        logger.info(f"Successfully saved guide with ID: {guide_id}")
    except Exception as e:
        logger.error(f"Failed to write to Firestore: {e}")
        return

    # 3. Test Read
    logger.info("Attempting to read from Firestore...")
    try:
        guides = list_guides()
        logger.info(f"Successfully retrieved {len(guides)} guides from DB.")
        for g in guides:
            if g.get('id') == guide_id:
                logger.info(f"Found our test guide in DB! Request: {g.get('request')}")
    except Exception as e:
        logger.error(f"Failed to read from Firestore: {e}")

if __name__ == "__main__":
    test_firestore()
