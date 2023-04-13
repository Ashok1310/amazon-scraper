import requests
from bs4 import BeautifulSoup
from pprint import pprint
from fastapi import FastAPI
from sqlalchemy import create_engine,or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


from tasks import scrap_amazon_products,ProductsTable
from scrapper import amazon_scrapper




# Create the FastAPI instance
app = FastAPI()

# Set up the SQLAlchemy engine and sessionmaker
engine = create_engine('sqlite:///data.db')
Session = sessionmaker(bind=engine)


# Define the API routes
@app.post('/scrap_products')
def scrap_products(keyword: str, max_page: int = None, max_product: int = None):
    task = scrap_amazon_products.delay(keyword, max_page,max_product)
    return {'status': 'STARTED', 'task_id': task.id}



@app.get('/products/task/{task_id}')
def get_products_by_task_id(task_id: str, result_size: int = None):
    session = Session()
    query = session.query(ProductsTable).filter(ProductsTable.task_id == task_id)
    if result_size is not None:
        query = query.limit(result_size)
    results = query.all()
    session.close()
    if results:
        data = [
                    {
                        'title': result.product_title, 
                        'discount_price': result.product_discount_price, 
                        'discount_percent': result.product_discount_percent,
                        'is_in_deal_of_day':result.is_in_deal_of_day,
                        'actual_price': result.product_actual_price,
                        'about': result.product_about,
                        "keywords": result.keywords
                    } 
                    for result in results
                ]
        return {'status': 'SUCCESS', 'data': data}
    else:
        return {'status': 'PENDING'}


@app.get('/products/keyword/{keywords}')
def get_products_by_keyword(keywords: str, result_size: int = None):
    session = Session()
    query = session.query(ProductsTable).filter(or_(
        ProductsTable.keywords == keywords,
        ProductsTable.keywords.like(f'%{keywords}%')
    ))
    if result_size is not None:
        query = query.limit(result_size)
    results = query.all()
    session.close()
    if results:
        data = [
                    {
                        'title': result.product_title, 
                        'discount_price': result.product_discount_price, 
                        'discount_percent': result.product_discount_percent,
                        'is_in_deal_of_day':result.is_in_deal_of_day,
                        'actual_price': result.product_actual_price,
                        'about': result.product_about,
                        "keywords": result.keywords
                    } 
                    for result in results
                ]
        return {'status': 'SUCCESS', 'data': data}
    else:
        return {'status': 'FAIL','msg':'data not found.'}
