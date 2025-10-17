import logging
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.domain.user import User, UserRepository

Base = declarative_base()


class UserModel(Base):
    """Modelo SQLAlchemy para usuário."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)


class UserSQLRepository(UserRepository):
    """Implementação do repositório de usuários com SQLAlchemy."""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.logger = logging.getLogger(__name__)

    def create(self, user: User) -> User:
        """Cria um novo usuário."""
        db = self.SessionLocal()
        try:
            db_user = UserModel(
                username=user.username,
                email=user.email,
                hashed_password=user.hashed_password,
                is_active=user.is_active
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return self._to_domain(db_user)
        finally:
            db.close()

    def get_by_username(self, username: str) -> Optional[User]:
        """Busca usuário por username."""
        db = self.SessionLocal()
        try:
            db_user = db.query(UserModel).filter(UserModel.username == username).first()
            return self._to_domain(db_user) if db_user else None
        finally:
            db.close()

    def get_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por email."""
        db = self.SessionLocal()
        try:
            db_user = db.query(UserModel).filter(UserModel.email == email).first()
            return self._to_domain(db_user) if db_user else None
        finally:
            db.close()

    def _to_domain(self, db_user: UserModel) -> User:
        """Converte modelo SQLAlchemy para entidade de domínio."""
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active
        )
