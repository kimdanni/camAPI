import requests
res = requests.post('http://localhost:8080/getCat', json={'uid':"dfafd", 'cid':1, 'chattid':1})
print(res.json())
if res.ok:
    print(res)