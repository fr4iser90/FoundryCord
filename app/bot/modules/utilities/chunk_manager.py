def chunk_message(content, chunk_size=1800):
    """Teilt eine Nachricht in kleinere Teile auf, wenn sie zu lang ist."""
    for i in range(0, len(content), chunk_size):
        yield content[i:i+chunk_size]   
