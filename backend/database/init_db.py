from database.session import Base, engine
from models.customer import Customer
from models.prediction import Prediction


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
