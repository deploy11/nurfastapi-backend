import logging
from typing import Any, Union, List
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from .models import User, Todo
from .config import SessionLocal

object_type_hint = Union[User, Todo]
objects_type_hints = List[Union[User, Todo]]

class ORMBase:
    def __init__(self, model):
        self.model = model

    def get(self, db: Session, id: int) -> object_type_hint:
        return db.query(self.model).filter(self.model.id == id).first()

    def create(self, db: Session, **object_data: dict) -> object_type_hint:
        try:
            obj = self.model(**object_data)
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj
        except IntegrityError:
            logging.info("IntegrityError: Data already exists in the database.")
            db.rollback()
        except Exception as e:
            logging.error(f"An error occurred while creating the object: {e}")
            db.rollback()

    def update(self, db: Session, id: int, **updated_data) -> object_type_hint:
        try:
            obj = db.query(self.model).filter(self.model.id == id).first()
            if not obj:
                raise ValueError(f"Object with ID {id} not found")
            for key, value in updated_data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            db.commit()
            return obj
        except Exception as e:
            logging.error(f"An error occurred while updating the object: {e}")
            db.rollback()
            raise

    def delete(self, db: Session, id: int) -> Any:
        try:
            obj = db.query(self.model).filter(self.model.id == id).first()
            if obj:
                db.delete(obj)
                db.commit()
                return True
            return False
        except Exception as e:
            logging.error(f"An error occurred while deleting the object: {e}")
            db.rollback()
            return False

    def all(self, db: Session) -> objects_type_hints:
        return db.query(self.model).all()

    def filter(self, db: Session, **filters) -> objects_type_hints:
        try:
            query = db.query(self.model)
            conditions = []
            for key, value in filters.items():
                if hasattr(self.model, key):
                    conditions.append(getattr(self.model, key) == value)
            if "logic" in filters and filters["logic"].lower() == "or":
                query = query.filter(or_(*conditions))
            else:
                query = query.filter(and_(*conditions))
            return query.all()  # Return all results as a list
        except Exception as e:
            logging.error(f"An error occurred while filtering objects: {e}")
            raise

    def count(self, db: Session) -> int:
        return db.query(self.model).count()

    def get_or_create(self, db: Session, **data) -> object_type_hint:
        obj = self.get(db, data.get("id"))
        if obj is None:
            return self.create(db, **data)
        return obj

# Create specific ORM instances for User and Todo
UserDB = ORMBase(model=User)
TodoDB = ORMBase(model=Todo)

# Define utility functions for User
def create_user(db: Session, username: str, email: str, password: str) -> User:
    try:
        return UserDB.create(db, username=username, email=email, password=password)
    except Exception as e:
        logging.error(f"User creation failed: {e}")
        raise ValueError("User creation failed")


def get_user(db: Session, username: str) -> User:
    users = UserDB.filter(db, username=username)
    return users[0] if users else None  # Return the first user or None

def authenticate_user(db: Session, username: str, password: str) -> User:


    
    user = get_user(db, username)
    if user and user.password == password:
        return user
    return None

def create_access_token(data: dict) -> str:
    # Your implementation for creating access token
    pass
