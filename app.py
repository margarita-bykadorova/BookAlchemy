"""Flask application for a simple digital library."""

import os

import markdown
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, render_template, request, redirect, url_for

from data_models import db, Author, Book

load_dotenv()

try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except TypeError:
    # Environment (like Codio) may have incompatible httpx/openai combo
    client = None

app = Flask(__name__)

BASEDIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(BASEDIR, 'data/library.sqlite')}"
)

db.init_app(app)


@app.route("/")
def home():
    """
    Render the home page with optional search and sorting.

    Supports:
    - search by book title (case-insensitive)
    - sorting by title or author name
    """
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

    return render_template(
        "home.html",
        books=books,
        message=message,
        sort_option=sort_option,
        search_query=search_query,
    )


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """
    Add a new author to the library.

    GET: render the author form.
    POST: create a new Author if the name is unique.
    """
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
            date_of_death=date_of_death,
        )
        db.session.add(new_author)
        db.session.commit()

        message = "Author added successfully!"
        return render_template("add_author.html", message=message)

    return render_template("add_author.html")


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """
    Add a new book to the library.

    GET: render the book form.
    POST: create a new Book if ISBN is unique (when provided).
    """
    if request.method == "POST":
        title = request.form["title"].strip()
        isbn = request.form["isbn"].strip()
        publication_year = request.form["publication_year"] or None
        rating = request.form.get("rating") or None
        author_id = request.form["author_id"]

        # Check for duplicate ISBN
        if isbn:
            existing_book = Book.query.filter_by(isbn=isbn).first()
            if existing_book:
                authors = Author.query.all()
                message = f"A book with ISBN {isbn} already exists."
                return render_template(
                    "add_book.html",
                    authors=authors,
                    message=message,
                )

        new_book = Book(
            title=title,
            isbn=isbn or None,
            publication_year=publication_year,
            rating=rating,
            author_id=author_id,
        )
        db.session.add(new_book)
        db.session.commit()

        message = "Book added successfully!"
        authors = Author.query.all()
        return render_template(
            "add_book.html",
            authors=authors,
            message=message,
        )

    authors = Author.query.all()
    return render_template("add_book.html", authors=authors)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    """
    Delete a single book.

    If the book's author has no remaining books afterwards,
    the author is deleted as well.
    """
    book = Book.query.get_or_404(book_id)
    author = book.author

    db.session.delete(book)
    db.session.commit()

    # If the author has no more books, delete the author too
    if not author.books:
        db.session.delete(author)
        db.session.commit()

    message = "Book deleted successfully!"
    return redirect(url_for("home", message=message))


@app.route("/author/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    """
    Delete an author and all of their books.

    This is a cascading delete implemented in Python code.
    """
    author = Author.query.get_or_404(author_id)

    # Delete all books by this author
    for book in author.books:
        db.session.delete(book)

    db.session.delete(author)
    db.session.commit()

    message = "Author and all their books deleted successfully!"
    return redirect(url_for("home", message=message))


@app.route("/book/<int:book_id>")
def book_detail(book_id):
    """Render a detail page for a single book."""
    book = Book.query.get_or_404(book_id)
    return render_template("book_detail.html", book=book)


@app.route("/suggest")
def suggest():
    """
    Generate a book recommendation using the AI model.

    Uses the list of books in the library as context and
    returns a markdown-formatted recommendation, which is
    rendered as HTML on the suggestion page.

    Falls back to a simple message if the AI client is not available.
    """
    if client is None:
        return render_template(
            "suggest.html",
            suggestion=(
                "AI suggestions are not available in this environment. "
                "Please run the app locally with a valid OpenAI setup "
                "to use this feature."
            ),
        )

    books = Book.query.all()
    titles = [book.title for book in books]

    if not books:
        suggestion = "Add some books first so I can recommend something!"
        return render_template("suggest.html", suggestion=suggestion)

    # Show only a few books in the visible intro text
    preview_titles = titles[:5]  # first five books
    preview_list = ", ".join(preview_titles)

    prompt = (
        "The user has read many books. Here is the FULL list:\n"
        f"{', '.join(titles)}\n\n"

        "Recommend ONE new book that is NOT in the list above.\n"
        "The output should still reference the user's taste, but "
        f"only mention these few example titles in the intro: {preview_list}.\n\n"

        "Start the answer with:\n"
        f"'Based on your interest in {preview_list}, I recommend:'\n\n"

        "Use headings, bold text, bullet points, and clean markdown formatting."
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    suggestion_md = response.output_text
    suggestion_html = markdown.markdown(suggestion_md)

    return render_template(
        "suggest.html",
        suggestion=suggestion_html,
    )


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
