if file_storage and file_storage.filename:
    filename = secure_filename(file_storage.filename) or "upload.dat"
    stored_filename = f"{uuid4().hex}_{filename}"
    file_storage.save(upload_dir() / stored_filename)
