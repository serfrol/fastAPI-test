from typing import Optional, Callable
from tempfile import NamedTemporaryFile
from fastapi import FastAPI, Request, Response, HTTPException, Form, UploadFile, File, Depends, Query
from fastapi.responses import FileResponse
import numpy as np
from sklearn import datasets
from joblib import dump, load
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Union
import json
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
import io
from schemas import BaseForm
import pandas as pd
import aiofiles
from pathlib import Path
import shutil

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates/")
knn = load('knn.pkl')


@app.get("/")
def read_root():
    print("hi")
    return 'Hello Friend'


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.api_route('/user/{username}')
def show_user_profile(username):
    return f'Hello, user {username}'

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

@app.api_route('/avg/{nums}')
def avg(nums):
    nums = nums.split(',')
    nums = [float(num) for num in nums]
    nums_mean = mean(nums)
    return str(nums_mean)

from fastapi.responses import HTMLResponse
@app.api_route('/iris/{param}', response_class=HTMLResponse)
def iris(param):
    param = param.split(',')
    param = [float(num) for num in param]

    param = np.array(param).reshape(1, -1)
    predict = knn.predict(param)
    
    if predict == 1:
        flower = 'setosa'
    elif predict == 2:
        flower = 'versicolor'
    else:
        flower = 'virginica'
    
    html_content=f"""
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>This is {flower} {predict}</h1>
            <img src="/static/{flower}.jpg" alt="{flower}">
        </body>
    </html>
    """
  
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/get_info")
async def get_info(info : Request):
    req_info = await info.json()
    print(req_info)
    return {
        "status" : "SUCCESS",
        "data" : req_info
    }



# @app.api_route('/get_iris', request_class=JSONResponse)
# async def get_iris(info : Request):
#     content_ = await info.json()
#     print(content_)
#     return JSONResponse(content=content_, media_type="application/json")

def predict_flower(param):
    '''expects {"flower":"1,2,3,4"} '''
    try:
        param = param.dict()
    except:
        param = dict(param)
    param = param['flower'].split(',')
    param = [float(num) for num in param]
    param = np.array(param).reshape(1, -1)
    predict = knn.predict(param)
    predict = {'class':str(predict[0])}
    # except:
        # raise HTTPException(status_code=200, detail="Bad Request")


    return predict

class Item(BaseModel):
    flower : str

@app.post("/get_iris")
async def get_iris(param: Item):
    predict = predict_flower(param)

    return predict


@app.post("/submit")
async def submit(request: Request, nums = Form()):
    nums_dict = {'flower':nums}
    result = predict_flower(nums_dict)
    return templates.TemplateResponse('submit.html', context={'request': request, 'result': result})

@app.get("/submit")
async def submit(request: Request):
    result = "Type 4 numbers (1,2,3,7)"
    return templates.TemplateResponse('submit.html', context={'request': request, 'result': result})


# @app.post("/upload")
# def upload(request: Request, file: UploadFile = File(...)):
#     try:
#         contents = file.file.read()
#         with open(file.filename, 'wb') as f:
#             f.write(contents)
#     except Exception:
#         return {"message": "There was an error uploading the file"}
#     finally:
#         file.file.close()

#     return templates.TemplateResponse('submit.html', context={'request': request, 'result': file.filename})


@app.get('/upload', response_class=HTMLResponse)
def get_file(request: Request):
    return templates.TemplateResponse('upload.html', {"request": request})

# @app.post('/upload', response_class=HTMLResponse)
# async def post_file(request: Request, form_data: BaseForm = Depends(BaseForm.as_form)):
#     # content = await file.read()
#     result = form_data.file.read()
#     print(form_data)
#     print(form_data.file.read())
#     print(form_data.file.read().decode('utf-8'))
#     print(form_data.file.data)

#     return templates.TemplateResponse("upload.html", {"request": request, "result":result})

@app.post('/upload', response_class=HTMLResponse)
async def post_file(request: Request, result: str = "", filename: str = Form(...), file: UploadFile = File(...)):
    file_location = f"files/{filename}.csv"
    async with aiofiles.open(file_location, 'wb') as new_file:
        content = await file.read()
        # new_file = pd.read_csv(io.StringIO(content.decode('utf-8')))
        # print(type(new_file))
        # dict_ = {"flower" : new_file[0]}
        # result = predict_flower(dict_)
        # new_file['prediction'] = result['class']
        # df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        # predict = knn.predict(df)
        # predict = pd.DataFrame(predict)
        # predict.to_csv()
        await new_file.write(content)
        return FileResponse(file_location, media_type='application/octet-stream',filename=f'{filename}.csv')
    return templates.TemplateResponse("upload.html", {"request": request, "result": result})


@app.get('/upload2', response_class=HTMLResponse)
def get_file(request: Request):
    return templates.TemplateResponse('upload.html', {"request": request})

@app.post('/upload2', response_class=HTMLResponse)
def get_file(request: Request, result: str = "", filename: str = Form(...), file: UploadFile = File(...)):
    filepath = f"files/{filename}.csv"
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    df = pd.read_csv(filepath)
    pred = knn.predict(df)
    new_filepath = f'files/{filename}_pred.csv'
    pred = pd.DataFrame(pred, columns=['Prediciton'])
    pred.to_csv(f'files/{filename}_pred.csv')
    return FileResponse(new_filepath, media_type='application/octet-stream',filename=f'{filename}_pred.csv')


    
# async def return_file()

# async def post_endpoint(in_file: UploadFile=File(...)):
#     # ...
#     async with aiofiles.open(out_file_path, 'wb') as out_file:
#         content = await in_file.read()  # async read
#         await out_file.write(content)  # async write

#     return {"Result": "OK"}