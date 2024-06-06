from sqlalchemy.orm import class_mapper


def object_as_dict(obj):
    """
    Convert a SQLAlchemy model object into a dictionary.
    """
    return {c.key: getattr(obj, c.key)
            for c in class_mapper(obj.__class__).columns}
