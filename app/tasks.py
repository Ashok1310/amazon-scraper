from celery import Celery
from scrapper import amazon_scrapper
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# Set up the Celery instance
celery_app = Celery('tasks', broker='pyamqp://guest@localhost//')


# Set up the SQLAlchemy engine and sessionmaker
engine = create_engine('sqlite:///data.db')
Session = sessionmaker(bind=engine)

# Define the SQLAlchemy model
Base = declarative_base()

class ProductsTable(Base):
    __tablename__ = 'task_results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, nullable=False)
    product_title = Column(String,nullable=False)
    product_discount_price = Column(String,nullable=False)
    product_discount_percent = Column(String,nullable=False)
    is_in_deal_of_day = Column(Integer,nullable=False)
    product_actual_price = Column(String,nullable=False)
    product_about = Column(String,nullable=False)
    keywords = Column(String,nullable=False) 

Base.metadata.create_all(bind=engine)



# Define the Celery task
@celery_app.task(bind=True)
def scrap_amazon_products(self, keywords,max_page,max_product):
    
    products_list = amazon_scrapper(
        keywords=keywords,
        max_page=max_page,
        max_product=max_product
    )

    print()
    print("product List")
    print(products_list)
    session = Session()  

    for product in products_list:
        result = ProductsTable(
                task_id=self.request.id,    
                product_title = product.get("product_title"),
                product_discount_price =  product.get("product_discount_price"),
                product_discount_percent = product.get("product_discount_percent"),
                is_in_deal_of_day = product.get("is_in_deal_of_day"),
                product_actual_price = product.get("product_actual_price"),
                product_about = product.get("product_about"),
                keywords = keywords
            )
        session.add(result)
        session.commit()
    return {'status': 'SUCCESS', 'task_id': self.request.id}
