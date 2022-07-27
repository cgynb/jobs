import numpy as np
import json
from bson import ObjectId


def recommend_ids(choicetextid):
    try:
        loadData = np.load('../test.txt.npy')
    except FileNotFoundError:
        return []
    path = '../article.json'
    f = open(path, 'r', encoding='utf-8')
    datatotal = json.load(f)
    totaltext = len(datatotal)  # 文章总数
    for i in range(totaltext):
        if datatotal[i].get("_id").get("$oid") == choicetextid:
            t = i + 1
            break
    textsimtotal = loadData[t]
    temp = []
    for one in np.argsort(-textsimtotal)[1:6]:
        temp.append(ObjectId(datatotal[one].get("_id").get("$oid")))
    return temp


if __name__ == '__main__':
    print(recommend_ids('62d7a58c19fae38131a83870'))
