docker exec -it <82bdfa79909a> bash
docker exec -it 59e919546b98 python train_model.py

curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"flower":"1,2,3,7"}' \
  http://localhost:8000/get_info

curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"username":"xyz","password":"xyz"}' \
  http://localhost:3000/api/login


curl -X POST http://localhost:8000/get_iris \
   -H 'Content-Type: application/json' \
   -d '{"flower":"1,2,3,7"}'

curl -H "Content-Type: application/json" -X POST "http://localhost:8000/get_iris" -d {"""flower""":"""asd"""}