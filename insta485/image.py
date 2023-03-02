"""Insta485 image API."""
import uuid
import pathlib
import insta485


def save_img(file_obj):
    """Save image and returns the file name."""
    uuid_basename = "{stem}{suffix}".format(
        stem=uuid.uuid4().hex,
        suffix=pathlib.Path(file_obj.filename).suffix
    )
    # Save to disk
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    file_obj.save(path)
    return uuid_basename


def del_img(filename):
    """Delete image."""
    (insta485.app.config["UPLOAD_FOLDER"]/filename).unlink()
