import hashlib

def contentHash(story: str):
    content_h = hashlib.sha256(story.encode('ascii')).digest()
    return content_h
