import mimetypes
import os
import uuid


def generate_filename(name: str):
    uid_file = str(uuid.uuid4())[:8]
    filename = os.path.splitext(name)[0]
    ext = os.path.splitext(name)[-1]
    return uid_file + "_" + filename + ext


def check_mimetype(file_path: str):
    content_type, _ = mimetypes.guess_type(file_path)
    return content_type

