from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database

DATABASE_URL = "sqlite:///./test.db"
database = Database(DATABASE_URL)
metadata = MetaData()
Base = declarative_base()

# Define a SQLAlchemy ORM model with the new field
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    yearly_income = Column(Integer)
    anticipated_savings_percentage = Column(Integer, default=0)
    years_to_70 = Column(Integer)
    estimated_savings = Column(Integer)

    def calculate_years_to_70(self):
        return 70 - self.age

    def calculate_estimated_savings(self):
        self.years_to_70 = self.calculate_years_to_70()
        return self.years_to_70 * self.yearly_income * (self.anticipated_savings_percentage / 100)

        

# Create the database tables
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

# Create a session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/", response_class=HTMLResponse)
async def read_form():
    return """
    <html>
        <body>
          <html>
    <body>
        <form action="/submit" method="post">
            <label for="name">Name:</label>
            <input type="text" id="name" name="name" placeholder="Name" value="Bob Doe"><br>

            <label for="age">Age:</label>
            <input type="number" id="age" name="age" placeholder="Age" value="30"><br>

            <label for="yearly_income">Yearly Income:</label>
            <input type="number" id="yearly_income" name="yearly_income" placeholder="Yearly Income" value="50000"><br>

            <label for="anticipated_savings_percentage">Anticipated Savings Percentage:</label>
            <input type="number" id="anticipated_savings_percentage" name="anticipated_savings_percentage" placeholder="Percentage Saved" value="1"><br>

            <input type="submit">
        </form>
    </body>
</html>
   
    """

@app.post("/submit", response_class=HTMLResponse)
async def submit_form(name: str = Form(...), age: int = Form(...), yearly_income: int = Form(...), anticipated_savings_percentage: int = Form(0)):
    user = User(name=name, age=age, yearly_income=yearly_income, anticipated_savings_percentage=anticipated_savings_percentage)
    user.estimated_savings = user.calculate_estimated_savings()
    async with database.transaction():
        await database.execute(User.__table__.insert().values(name=user.name, 
                                                              age=user.age, 
                                                              years_to_70=user.years_to_70,
                                                              anticipated_savings_percentage=user.anticipated_savings_percentage,
                                                              yearly_income=user.yearly_income,
                                                              estimated_savings=user.estimated_savings))
    return f"""
    <html>
        <body>
            <h2>User Submitted:</h2>
            <p>Name: {user.name}</p>
            <p>Age: {user.age}</p>
            <p>Years to 70: {user.years_to_70}</p>
            <p>Yearly Income: {user.yearly_income}</p>
            <p>Anticipated Savings Percentage: {user.anticipated_savings_percentage}</p>
            <p>Estimated Savings: {user.estimated_savings}</p>
        </body>
    </html>
    """



# from fastapi import FastAPI, Form, Request
# from fastapi.responses import HTMLResponse
# from pydantic import BaseModel
# from sqlalchemy import create_engine, Column, Integer, String, MetaData
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from databases import Database

# DATABASE_URL = "sqlite:///./test.db"
# database = Database(DATABASE_URL)
# metadata = MetaData()
# Base = declarative_base()

# # Define a SQLAlchemy ORM model
# class User(Base):
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, index=True)
#     age = Column(Integer)

# # Create the database tables
# engine = create_engine(DATABASE_URL)
# Base.metadata.create_all(bind=engine)

# # Create a session local class
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# app = FastAPI()

# @app.on_event("startup")
# async def startup():
#     await database.connect()

# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()

# @app.get("/", response_class=HTMLResponse)
# async def read_form():
#     return """
#     <html>
#         <body>
#             <form action="/submit" method="post">
#                 <input type="text" name="name" placeholder="Name">
#                 <input type="number" name="age" placeholder="Age">
#                 <input type="submit">
#             </form>
#         </body>
#     </html>
#     """

# @app.post("/submit", response_class=HTMLResponse)
# async def submit_form(name: str = Form(...), age: int = Form(...)):
#     user = User(name=name, age=age)
#     async with database.transaction():
#         await database.execute(User.__table__.insert().values(name=user.name, age=user.age))
#     return f"""
#     <html>
#         <body>
#             <h2>User Submitted:</h2>
#             <p>Name: {user.name}</p>
#             <p>Age: {user.age}</p>
#         </body>
#     </html>
#     """
