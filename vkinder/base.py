import logging

from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import exc

from .config import DSN


Base = declarative_base()
engine = create_engine(DSN, echo=False)
Session = sessionmaker(bind=engine)
logger = logging.getLogger('vkinder')


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    sex_id = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    city = Column(String, nullable=False)
    relation_id = Column(Integer, nullable=False)

    def __init__(self, user_id: int, sex_id: int, age: int, city: str, relation_id: int):
        super().__init__()
        self.user_id = user_id
        self.sex_id = sex_id
        self.age = age
        self.city = city
        self.relation_id = relation_id

    def __repr__(self):
        return f'<{type(self).__name__}(id={self.id})>'


class View(Base):
    __tablename__ = 'view'
    id = Column(Integer, primary_key=True)
    viewed_user_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)

    user = relationship(User, backref='views')

    def __init__(self, viewed_user_id: int, user_id: int):
        super().__init__()
        self.viewed_user_id = viewed_user_id
        self.user_id = user_id

    def __repr__(self):
        return f'<{type(self).__name__}(id={self.id})>'


class Like(Base):
    __tablename__ = 'like'
    id = Column(Integer, primary_key=True)
    liked_user_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)

    user = relationship(User, backref='likes')

    def __init__(self, liked_user_id: int, user_id: int):
        super().__init__()
        self.liked_user_id = liked_user_id
        self.user_id = user_id

    def __repr__(self):
        return f'<{type(self).__name__}(id={self.id})>'


def session_add(cls: object) -> None:
    session = Session()
    try:
        session.add(cls)
        session.commit()
    except exc.SQLAlchemyError as error:
        session.rollback()
        logger.critical(error.__str__())
    finally:
        session.close()


def is_there_a_user(user_id: int) -> bool:
    """Whether the user is present in the database
    :param user_id: vk_user_id
    :return:
    """
    with Session() as session:
        users = session.query(User).filter(User.user_id == user_id).all()
    return True if users else False


def is_viewed(user_id: int, viewed_user_id: int) -> bool:
    """Whether this user was viewed by the user
    :param user_id: vk_user_id
    :param viewed_user_id: vk_user_id
    :return:
    """
    with Session() as session:
        views = session.query(View).filter(View.user_id == user_id, View.viewed_user_id == viewed_user_id).all()
    return True if views else False


def get_user(user_id: int) -> User:
    """Retrieve a user from the database
    :param user_id: vk_user_id
    :return: 'User'
    """
    with Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
    return user


def add_new_user(user_id: int, age: int, sex_id: int, relation_id: int, city: str) -> None:
    """Adding a new user to the database
    :param user_id: vk_user_id
    :param age: digital
    :param sex_id: digital
    :param relation_id: digital
    :param city: string example: 'Москва'
    :return:
    """
    user = User(user_id=user_id, age=age, sex_id=sex_id, city=city, relation_id=relation_id)
    session_add(user)


def add_view(user_id: int, viewed_user_id: int) -> None:
    """Enter the view in the database
    :param user_id: vk_user_id
    :param viewed_user_id: vk_user_id
    :return:
    """
    view = View(user_id=user_id, viewed_user_id=viewed_user_id)
    session_add(view)


def add_like(user_id: int, liked_user_id: int) -> None:
    """Enter the like in the database
    :param user_id: vk_user_id
    :param liked_user_id: vk_user_id
    :return:
    """
    like = Like(user_id=user_id, liked_user_id=liked_user_id)
    session_add(like)


def create_tables():
    Base.metadata.create_all(engine)
