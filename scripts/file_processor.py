def read_from_file(file_path: str, chunk_size: int = 1000):
    """
    Generator function to read large files in chunks
    Args:
        file_path: Path to the file to read
        chunk_size: Number of lines to read at once
    Yields:
        List of lines from the file
    """
    with open(file_path, "r") as file:
        # Skip the header line
        next(file)
        
        chunk = []
        for line in file:
            chunk.append(line.strip())
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []
        if chunk:  # Don't forget the last chunk
            yield chunk 