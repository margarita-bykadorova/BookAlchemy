"""Database models for the digital library application."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    """
    Represents an author in the digital library.

    Attributes:
        id (int): Primary key.
        name (str): Full name of the author. Must be unique.
        birth_date (str): Birth date in YYYY-MM-DD format.
        date_of_death (str): Optional death date in YYYY-MM-DD format.
        books (list[Book]): Relationship to all books written by this author.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    birth_date = db.Column(db.String(10))
    date_of_death = db.Column(db.String(10))

    # Cascade ensures deleting an Author removes all their books
    books = db.relationship(
        "Book",
        backref="author",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Author id={self.id} name='{self.name}'>"

    def __str__(self) -> str:
        return self.name


class Book(db.Model):
    """
    Represents a book in the digital library.

    Attributes:
        id (int): Primary key.
        isbn (str): Unique ISBN identifier. Required.
        title (str): Book title.
        publication_year (int): Year the book was published.
        rating (int): Optional rating (1–10).
        author_id (int): Foreign key linking to Author.
    """

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), nullable=False, unique=True)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    author_id = db.Column(
        db.Integer,
        db.ForeignKey("author.id"),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<Book id={self.id} title='{self.title}'>"

    def __str__(self) -> str:
        return self.title
