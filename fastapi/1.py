from fastapi import FastAPI,Path,Query
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import time
import asyncio
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World999"}

@app.get("/user/hello")
async def read_root():
    return {"msg": "我正在学习FastAPI"}

@app.get("/book/{id}")
async def read_book(id:int):
    return {"id":f"访问第{id}本书"}

@app.get("/book/{name}")
async def read_book(name:str= Path(...,description="图书名称")):
    return {"name":f"访问{name}"}
@app.get("/letter/{id}")
async def read_letter(id:str= Path(...,description="新闻分类id")):
    return {"id":f"访问第{id}"}

@app.get("/letter/{name}")
async def read_letter_name(name:str= Path(...,ge=10,description="新闻分类名称")):
    return {"name":f"访问{name}"}
@app.get("/news/news_id")
async def read_news_id(skip:int=Query(0,description="跳过条数"), limit:int=10):
    return {"skip":f"跳过{skip}条新闻","limit":f"返回{limit}条新闻"}


class Add_book(BaseModel):
    name:str
    author:str
    price:int

@app.post("/book")
async def register(book:Add_book):
    return {"book":book}

@app.get(path="/html",response_class=HTMLResponse)
async def read_html():
    return "<h1>Hello World</h1>"

@app.get("/sync")
def read_root():
    t1=time.time()
    time.sleep(1)
    t2=time.time()
    return {"time": f"耗时: {t2-t1}"}


@app.get("/async")
async def read_root1():
    t1=time.time()
    await asyncio.sleep(1)
    t2=time.time()
    return {"time": f"耗时: {t2-t1}"}
