from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()
engine = create_engine('postgresql://postgres:123456@localhost:5432/vkinder', echo=False)
Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True)
    sex = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    city = Column(String, nullable=False)
    relation = Column(Integer, nullable=False)


class View(Base):
    __tablename__ = 'view'
    id = Column(Integer, primary_key=True)
    viewed_user = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    user = relationship(User, backref='views')


class Like(Base):
    __tablename__ = 'like'
    id = Column(Integer, primary_key=True)
    liked_user = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    user = relationship(User, backref='likes')


def is_not_new_user(user_id):
    with Session() as session:
        users = session.query(User).filter(User.user_id == user_id).all()
    if users:
        return True
    return False


def is_viewed(user_id, viewed_user_id):
    with Session() as session:
        views = session.query(View).filter(View.user_id == user_id, View.viewed_user == viewed_user_id).all()
    if views:
        return True
    return False


def get_user(user_id):
    with Session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
    return user


def add_new_user(user_id, age, sex_id, relation_id, city):
    user = User(user_id=user_id, age=age, sex=sex_id, city=city, relation=relation_id)
    session = Session()
    session.add(user)
    session.commit()
    session.close()


def add_view(user_id, viewed_user_id):
    view = View(user_id=user_id, viewed_user=viewed_user_id)
    session = Session()
    session.add(view)
    session.commit()
    session.close()


def add_like(user_id, liked_user_id):
    like = Like(user_id=user_id, liked_user=liked_user_id)
    session = Session()
    session.add(like)
    session.commit()
    session.close()


def create_tables():
    Base.metadata.create_all(engine)
