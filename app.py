"""Flask application for a simple digital library."""

import os

from flask import Flask, render_template, request, redirect, url_for

from data_models import db, Author, Book

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"

db.init_app(app)


@app.route("/")
def home():
    """Render the home page with optional search and sorting."""
    search_query = request.args.get("search")
    sort_option = request.args.get("sort")
    message = request.args.get("message")

    query = Book.query

    # Search filter
    if search_query:
        query = query.filter(Book.title.ilike(f"%{search_query}%"))

    # Sorting
    if sort_option == "title":
        query = query.order_by(Book.title)
    elif sort_option == "author":
        query = query.join(Author).order_by(Author.name)

    books = query.all()

    # No results message
    if search_query and not books:
        message = f"No books found matching '{search_query}'."

    return render_template("home.html", books=books, message=message)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        name = request.form["name"].strip()
        birth_date = request.form["birthdate"]
        date_of_death = request.form.get("date_of_death")

        # Check for duplicate author name
        existing_author = Author.query.filter_by(name=name).first()
        if existing_author:
            message = f"Author '{name}' already exists."
            return render_template("add_author.html", message=message)

        new_author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death
        )
        db.session.add(new_author)
        db.session.commit()

        message = "Author added successfully!"
        return render_template("add_author.html", message=message)

    return render_template("add_author.html")


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form["title"].strip()
        isbn = request.form["isbn"].strip()
        publication_year = request.form["publication_year"]
        rating = request.form.get("rating")  # may be empty
        author_id = request.form["author_id"]

        # Check for duplicate ISBN
        if isbn:
            existing_book = Book.query.filter_by(isbn=isbn).first()
            if existing_book:
                authors = Author.query.all()
                message = f"A book with ISBN {isbn} already exists."
                return render_template("add_book.html", authors=authors, message=message)

        new_book = Book(
            title=title,
            isbn=isbn,
            publication_year=publication_year,
            rating=rating,
            author_id=author_id
        )

        db.session.add(new_book)
        db.session.commit()

        message = "Book added successfully!"
        authors = Author.query.all()
        return render_template("add_book.html", authors=authors, message=message)

    authors = Author.query.all()
    return render_template("add_book.html", authors=authors)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    """Delete a book, and optionally its author if they have no other books."""
    book = Book.query.get_or_404(book_id)
    author = book.author  # Save for later check

    db.session.delete(book)
    db.session.commit()

    # If the author has no more books, delete the author too
    if len(author.books) == 0:
        db.session.delete(author)
        db.session.commit()

    message = "Book deleted successfully!"
    return redirect(url_for("home", message=message))


@app.route("/author/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    """Delete an author and all of their books."""
    author = Author.query.get_or_404(author_id)

    # Delete all books by this author
    for book in author.books:
        db.session.delete(book)

    # Delete the author
    db.session.delete(author)
    db.session.commit()

    message = "Author and all their books deleted successfully!"
    return redirect(url_for("home", message=message))


@app.route("/book/<int:book_id>")
def book_detail(book_id):
    """Render a detail page for a single book."""
    book = Book.query.get_or_404(book_id)
    return render_template("book_detail.html", book=book)


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
