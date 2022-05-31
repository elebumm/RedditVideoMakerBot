import os


def cleanup() -> int:
    count = 0
    files = [f for f in os.listdir('.') if f.endswith('.mp4') and 'temp' in f.lower()]
    count += len(files)
    for f in files:
        os.remove(f)

    for file in os.listdir('./assets/temp/mp4'):
        count += 1
        os.remove('./assets/temp/mp4/' + file)
    for file in os.listdir('./assets/temp/mp3'):
        count += 1
        os.remove('./assets/temp/mp3/' + file)
    return count

