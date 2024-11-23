import bcrypt
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Float
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import QueuePool
from sqlalchemy.sql import func

from winter.settings import DATABASE_URL, DB_POOL_CONFIG, SSL_CONFIG, POINTS_PER_ACTIVITY

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    activities = relationship("DailyActivity", back_populates="user", lazy='joined')
    weight_entries = relationship("WeightEntry", back_populates="user")


class DailyActivity(Base):
    __tablename__ = 'daily_activities'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(Date, nullable=False)
    physical_activity = Column(Boolean, default=False)
    diet_nutrition = Column(Boolean, default=False)
    rest_recovery = Column(Boolean, default=False)
    personal_development = Column(Boolean, default=False)

    # Relationship with User
    user = relationship("User", back_populates="activities")


class WeightEntry(Base):
    __tablename__ = 'weight_entries'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(Date, nullable=False)
    weight = Column(Float, nullable=False)

    # Relación con User
    user = relationship("User", back_populates="weight_entries")


def initialize_database():
    """
    Initializes the database by creating all tables.
    """
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=DB_POOL_CONFIG["pool_size"],
        max_overflow=DB_POOL_CONFIG["max_overflow"],
        pool_timeout=DB_POOL_CONFIG["pool_timeout"],
        pool_recycle=DB_POOL_CONFIG["pool_recycle"],
        connect_args=SSL_CONFIG
    )
    Base.metadata.create_all(engine)


def get_session():
    """
    Creates and returns a SQLAlchemy session.
    """
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=DB_POOL_CONFIG["pool_size"],
        max_overflow=DB_POOL_CONFIG["max_overflow"],
        pool_timeout=DB_POOL_CONFIG["pool_timeout"],
        pool_recycle=DB_POOL_CONFIG["pool_recycle"],
        connect_args=SSL_CONFIG
    )
    Session = sessionmaker(bind=engine)
    return Session()


def create_user(username: str, password: str):
    """
    Creates a new user with a hashed password.
    """
    session = get_session()
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = User(username=username, password_hash=hashed.decode('utf-8'))
    session.add(user)
    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error creating user: {e}")
    finally:
        session.close()


def verify_credentials(username: str, password: str) -> bool:
    """
    Verifies user credentials.
    """
    session = get_session()
    user = session.query(User).filter(User.username == username).first()
    session.close()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return True
    return False


def get_connection():
    """
    Creates and returns a database connection using SQLAlchemy.
    
    Returns:
        connection: SQLAlchemy connection object if successful, None otherwise
    """
    try:
        # Create the SQLAlchemy engine with connection pooling and SSL
        engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=DB_POOL_CONFIG["pool_size"],
            max_overflow=DB_POOL_CONFIG["max_overflow"],
            pool_timeout=DB_POOL_CONFIG["pool_timeout"],
            pool_recycle=DB_POOL_CONFIG["pool_recycle"],
            connect_args=SSL_CONFIG
        )

        # Establish and return a connection
        connection = engine.connect()
        return connection

    except SQLAlchemyError as e:
        print(f"Error connecting to the database: {e}")
        return None


def get_user_id(username: str) -> int:
    """
    Retrieves the user ID for a given username.
    """
    session = get_session()
    user = session.query(User).filter(User.username == username).first()
    session.close()
    if user:
        return user.id
    else:
        return None


def get_user_points(user_id: int) -> dict:
    """
    Calculates total points and rank for a given user.
    Returns a dictionary with points and rank information.
    """
    session = get_session()

    try:
        # Calculate points using the same logic as in ranking.py
        points_query = session.query(
            func.sum(
                func.coalesce(DailyActivity.physical_activity.cast(Integer) * POINTS_PER_ACTIVITY['physical_activity'],
                              0) +
                func.coalesce(DailyActivity.diet_nutrition.cast(Integer) * POINTS_PER_ACTIVITY['diet_nutrition'], 0) +
                func.coalesce(DailyActivity.rest_recovery.cast(Integer) * POINTS_PER_ACTIVITY['rest_recovery'], 0) +
                func.coalesce(
                    DailyActivity.personal_development.cast(Integer) * POINTS_PER_ACTIVITY['personal_development'], 0))
        ).filter(DailyActivity.user_id == user_id).scalar()

        total_points = points_query or 0

        # Determine rank based on points
        rank = get_user_rank(total_points)

        return {
            'points': total_points,
            'rank': rank
        }
    finally:
        session.close()


def get_user_rank(points: int) -> str:
    """
    Determines user rank based on points.
    """
    if points <= 30:
        return "👨‍🎓 Estudiante"
    elif points <= 60:
        return "🥋 Genin"
    elif points <= 90:
        return "🎯 Chunin"
    elif points <= 110:
        return "⚔️ Jounin"
    elif points <= 119:
        return "🏆 Sannin Legendario"
    else:
        return "👑 Hokage"
