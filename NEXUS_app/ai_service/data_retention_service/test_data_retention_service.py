import datetime
import os

from .main import app

client = TestClient(app)


def test_apply_retention():
    test_dir = "test_retention_dir"
    os.makedirs(test_dir, exist_ok=True)

    # Create some files
    with open(os.path.join(test_dir, "new_file.txt"), "w") as f:
        f.write("new")

    old_file_path = os.path.join(test_dir, "old_file.txt")
    with open(old_file_path, "w") as f:
        f.write("old")

    # Set modification time of old_file.txt to be 3 days ago
    three_days_ago = datetime.datetime.now() - datetime.timedelta(days=3)
    os.utime(old_file_path, (three_days_ago.timestamp(), three_days_ago.timestamp()))

    # Apply retention policy for files older than 2 days
    response = client.post("/apply_retention", json={"path": test_dir, "days": 2})
    assert response.status_code == 200
    assert response.json()["deleted_files_count"] == 1

    # Check that the old file was deleted and the new one was not
    assert not os.path.exists(old_file_path)
    assert os.path.exists(os.path.join(test_dir, "new_file.txt"))

    # Clean up
    os.remove(os.path.join(test_dir, "new_file.txt"))
    os.rmdir(test_dir)
