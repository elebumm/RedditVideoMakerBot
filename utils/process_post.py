def process_post(reddit_thread_post):
    texts = reddit_thread_post
    threshold = 80
    for i in range(len(texts)):
        if len(texts[i]) > threshold:
            texts[i] = split_text(texts[i], threshold)
    return texts

def split_text(text, threshold):
    text = text.split(' ')
    new_text = ''
    texts = []

    for i in range(len(text)):
        if new_text == '':
            new_text = text[i]
            continue

        new_text += ' ' + text[i]
        if len(new_text) >= int(0.75 * threshold):
            go = True
            # Make sure that the text left is not so short
            if i < len(text) - 1:
                left = ' '.join(text[i+1:])
                if len(left) < int(0.25 * threshold):
                    go = False

            if go:
                texts.append(new_text)
                new_text = ''
    
    if new_text != '':
        texts.append(new_text)
    
    if len(texts) == 1: return texts[0]
    return tuple(texts)