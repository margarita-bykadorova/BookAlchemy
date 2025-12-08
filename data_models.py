"""Database models for the digital library application."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    """Model representing an author."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    birth_date = db.Column(db.String(10))
    date_of_death = db.Column(db.String(10))

    books = db.relationship(
        "Book",
        backref="author",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Author {self.name}>"

    def __str__(self):
        return self.name


class Book(db.Model):
    """Model representing a book."""

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), nullable=False, unique=True)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer)
    rating = db.Column(db.Integer)  # 1–10 rating
    author_id = db.Column(
        db.Integer,
        db.ForeignKey("author.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<Book {self.title}>"

    def __str__(self):
        return self.title
