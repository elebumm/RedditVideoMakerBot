def process_post(reddit_thread_post):
    texts = reddit_thread_post
    threshold = 60
    for i in range(len(texts)):
        if len(texts[i]) > threshold:
            texts[i] = split_text(texts[i], threshold)
    return texts

def split_text(text, threshold):
    text = text.split(' ')
    new_text = ''
    texts = []
    # for i in range(threshold+1,1,-1):
    #     if (len(text) / i) - (len(text) // i) >= 0.7:
    #         threshold = i
    #         # print("Found:", threshold)
    #         break

    for i in text:
        if new_text == '':
            new_text = i
            continue

        new_text += ' ' + i
        if len(new_text) >= threshold:
            texts.append(new_text)
            new_text = ''
    
    if new_text != '':
        texts.append(new_text)
    
    if len(texts) == 1: return texts[0]
    return tuple(texts)