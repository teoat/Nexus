import datetime
import os

def apply_retention_policy(path: str, days: int) -> int:
    """
    Applies a data retention policy to a directory.
    Deletes files older than the specified number of days.
    Returns the number of files deleted.
    """
    deleted_files_count = 0
    now = datetime.datetime.now()
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        if os.path.isfile(file_path):
            file_mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            if (now - file_mod_time).days > days:
                os.remove(file_path)
                deleted_files_count += 1
    return deleted_files_count
