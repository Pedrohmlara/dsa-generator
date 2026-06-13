"""Firestore Database integration for saving and retrieving guides."""

import datetime
import uuid
from typing import Any

from google.cloud import firestore

from app.config import settings

# Initialize Firestore client.
# It will use the GOOGLE_APPLICATION_CREDENTIALS environment variable
# or the default service account if deployed on GCP.
_db = None

def get_db() -> firestore.Client | None:
    """Return the Firestore client, initializing it if necessary."""
    global _db
    if _db is None:
        try:
            # If gcp_project_id is set in config, use it.
            if settings.gcp_project_id:
                _db = firestore.Client(project=settings.gcp_project_id, database=settings.gcp_firestore_database)
            else:
                _db = firestore.Client(database=settings.gcp_firestore_database)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("Failed to initialize Firestore: %s", e)
            return None
    return _db


def upsert_guide(
    request_data: dict[str, Any],
    outline: dict[str, Any],
    sections_content: list[str],
    sections_code: list[str],
    guide_id: str | None = None,
) -> str | None:
    """Save or update a generated guide in Firestore.

    Args:
        request_data: The original generation request (topics, style).
        outline: The parsed CurriculumOutline dictionary.
        sections_content: List of markdown content strings per section.
        sections_code: List of markdown code strings per section.
        guide_id: Existing guide ID to update, or None to create new.

    Returns:
        The generated guide ID, or None if Firestore is unavailable.
    """
    db = get_db()
    if not db:
        return None

    if not guide_id:
        guide_id = str(uuid.uuid4())
    
    # Merge the content and code back into the outline sections
    saved_sections = []
    for i, section in enumerate(outline.get("sections", [])):
        saved_sections.append({
            "title": section.get("title", ""),
            "topic": section.get("topic", ""),
            "subtopics": section.get("subtopics", []),
            "content": sections_content[i] if i < len(sections_content) else "",
            "code": sections_code[i] if i < len(sections_code) else "",
        })

    doc_ref = db.collection("guides").document(guide_id)
    doc_data = {
        "id": guide_id,
        "request": request_data,
        "outline": {"sections": saved_sections},
    }
    
    # Only set created_at if it doesn't exist (merge=True won't overwrite unless we tell it to)
    # But since we are setting, let's just update the timestamp every time or set on create.
    # We can just always set 'updated_at' and set 'created_at' on first create.
    doc_ref.set(doc_data, merge=True)
    
    # Set created_at only if it's new
    if not doc_ref.get().to_dict().get("created_at"):
        doc_ref.set({"created_at": firestore.SERVER_TIMESTAMP}, merge=True)
    
    return guide_id


def list_guides() -> list[dict[str, Any]]:
    """Retrieve metadata for all generated guides."""
    db = get_db()
    if not db:
        return []

    # Fetch ordered by created_at descending
    docs = db.collection("guides").order_by(
        "created_at", direction=firestore.Query.DESCENDING
    ).limit(50).stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        # Format the timestamp for JSON serialization
        if "created_at" in data and data["created_at"]:
            try:
                data["created_at"] = data["created_at"].isoformat()
            except AttributeError:
                pass
                
        # Only return metadata, not the full massive content array
        results.append({
            "id": data.get("id"),
            "request": data.get("request", {}),
            "created_at": data.get("created_at"),
            "sections_count": len(data.get("outline", {}).get("sections", [])),
        })
    return results


def get_guide(guide_id: str) -> dict[str, Any] | None:
    """Retrieve a single guide by ID."""
    db = get_db()
    if not db:
        return None

    doc = db.collection("guides").document(guide_id).get()
    if not doc.exists:
        return None

    data = doc.to_dict()
    if "created_at" in data and data["created_at"]:
        try:
            data["created_at"] = data["created_at"].isoformat()
        except AttributeError:
            pass
            
    return data
