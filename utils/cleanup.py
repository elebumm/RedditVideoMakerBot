import os


def cleanup():
    files = [f for f in os.listdir('.') if f.endswith('.mp4') and 'temp' in f.lower()]
    for f in files:
        os.remove(f)

