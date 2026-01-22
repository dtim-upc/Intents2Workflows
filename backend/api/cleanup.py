from pathlib import Path
from datetime import datetime, timedelta
import shutil
from models import DataProduct
from database.database import SessionLocal
#rom routes.data_product import UPLOAD_DIR, ANNOTATOR_DIR
UPLOAD_DIR = "datasets"
ANNOTATOR_DIR = "annotated_datasets"
RETENTION_DAYS = 1


def cleanup_old_sessions():
    cutoff = datetime.now() - timedelta(minutes=RETENTION_DAYS)

    with SessionLocal() as db:

        for session_folder in Path(UPLOAD_DIR).iterdir():
            if not session_folder.is_dir():
                continue

            folder_mtime = datetime.fromtimestamp(session_folder.stat().st_mtime)
            print(f"Folder {session_folder} -> mtime: {folder_mtime}, cutoff: {cutoff}")
            if folder_mtime < cutoff:
                session_id = session_folder.name

                # Delete DB entries
                print(f"Deleting session {session_id} from db")
                db.query(DataProduct).filter(DataProduct.session_id == session_id).delete()
                db.commit()

                print(f"Deleting session folder: {session_folder}")

                print(f"Deleting annotations of {session_id}")
                shutil.rmtree(Path(f"{ANNOTATOR_DIR}/{session_id}"))
                print(f"Deleting data files of of {session_id}")
                shutil.rmtree(Path(f"{UPLOAD_DIR}/{session_id}"))


#cleanup_old_sessions()
