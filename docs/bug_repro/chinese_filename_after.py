def display_upload_filename(raw_filename):
    name = Path(raw_filename.replace("\\", "/")).name.strip()
    return name or "upload.dat"


def stored_upload_filename(display_name):
    safe_name = secure_filename(display_name)
    suffix = Path(display_name).suffix
    if suffix and safe_name == suffix.lstrip("."):
        safe_name = f"upload{suffix}"
    return f"{uuid4().hex}_{safe_name or 'upload.dat'}"


if file_storage and file_storage.filename:
    filename = display_upload_filename(file_storage.filename)
    stored_filename = stored_upload_filename(filename)
    file_storage.save(upload_dir() / stored_filename)
