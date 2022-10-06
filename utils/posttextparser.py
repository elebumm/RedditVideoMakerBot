
MAX_CHARACTER= 200

#working good
def posttextparser(obj):
    text=obj#["thread_post"]
    newtext=[]
    # for text in text:
    if len(text)>MAX_CHARACTER:
        text2=text.split("\n")
        for dot in text2:
            if len(dot)>MAX_CHARACTER:
                text3=dot.split(".")
                for comma in text3:
                    if len(comma)> MAX_CHARACTER:
                        text4=comma.split(',')
                        newtext.extend(text4)
                    else:
                        newtext.append(comma)
            else:
                newtext.append(dot)
    else:
        newtext.append(text)        
    return remover(newtext)

def remover(List):
    reg=['',' ','.','\n',')',"''",'"',"'",'"','""'] #add if any any unwant value found
    lines=List
    lines1=[]
    lines2=[]
    
    for item in lines:
        for r in reg :
            if item==r:
                break
            else:
                continue
        else:
                lines1.append(item)

    for a in lines1: #Double check
        if a!='':
            aa=a.strip()
            lines2.append(aa)
            # print(f'"{a}"')            
    return lines2