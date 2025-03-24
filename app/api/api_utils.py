from sqlalchemy.orm import class_mapper
from datetime import datetime

def model_to_dict(obj):
    """Преобразует SQLAlchemy модель в словарь"""
    if isinstance(obj, datetime):
        return obj.isoformat()

    if hasattr(obj, '__dict__'):
        return {
            column.key: getattr(obj, column.key)
            for column in class_mapper(obj.__class__).columns
        }
    return obj