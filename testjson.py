import base64
import json
import cv2
import random

file_path = r'catAns\catting.json'
sample_path = 'sample/'

def chooseAnswer(isCat = True):
    with open(file_path, "r") as json_file:
        cat_data = json.load(json_file)
        textList = cat_data['3']

    textnum = random.randrange(0, len(textList))
    return textList[textnum]

for i in range(0,3):
    chosenAnswer = chooseAnswer()
    c = './catImg/cat' + str(i) + '.jpg'
    frame = cv2.imread(c)
    dstr = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode('utf8')
    cat_response = {'cat_id' : i, 'catImg': dstr, 'catAnswer': chosenAnswer}
    json_path = sample_path + str(i) + '.json'
    with open(json_path, 'w') as outfile:
        json.dump(cat_response, outfile, ensure_ascii=False)