from sqlalchemy.orm import sessionmaker


class Manager:
    def __init__(self, engine):
        self.engine = engine
        self.SessionMaker = sessionmaker(bind=engine)
