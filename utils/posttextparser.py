import re
import spacy

#working good
def posttextparser(obj):

    text=re.sub("\n", "", obj )

    try:
        nlp=spacy.load('en_core_web_sm')
    except OSError :

        print("dev:please dowload the model with this command \npython -m spacy download en")
        exit()

    doc= nlp(text)

    newtext=[]
    
    for line in doc.sents:
        newtext.append(line.text)
        # print(line)
    
    return newtext