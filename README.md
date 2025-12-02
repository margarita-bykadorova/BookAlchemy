# BookAlchemy - Digital Library Application

This project is a simple digital library built with **Flask** and
**Flask-SQLAlchemy**.\
Users can add authors, add books, view book details, search and sort
books, and delete both books and authors.

------------------------------------------------------------------------

## Features

### 📚 Book Management

-   Add new books with:
    -   Title
    -   ISBN (optional)
    -   Publication year
    -   Linked author
-   View list of all books
-   View details of each book
-   Delete a book
-   Covers displayed using OpenLibrary when ISBN is available

------------------------------------------------------------------------

## ✍️ Author Management

-   Add authors with:
    -   Name
    -   Birth date
    -   Date of death (optional)
-   Delete an author
    -   Automatically deletes all books written by that author

------------------------------------------------------------------------

## 🔍 Search & Sort

-   Search books by title
-   Sort books by:
    -   Title
    -   Author name

------------------------------------------------------------------------

## 🧱 Technical Overview

### Technologies Used

-   Python 3
-   Flask
-   Flask-SQLAlchemy
-   SQLite
-   Jinja2 templating
-   OpenLibrary Covers API (for displaying book covers)

### Project Structure

    project/
    │── app.py
    │── data_models.py
    │── data/
    │   └── library.sqlite
    │── templates/
    │   ├── home.html
    │   ├── add_author.html
    │   ├── add_book.html
    │   └── book_detail.html
    └── README.md

------------------------------------------------------------------------

## ▶️ Running the App

### 1. Install dependencies

    pip install flask flask_sqlalchemy

### 2. Run the Flask server

    python app.py

### 3. Open in browser

    http://127.0.0.1:5000/

------------------------------------------------------------------------

## 📝 Notes

-   The SQLite database (`library.sqlite`) is ignored in Git for
    cleanliness.
-   The app automatically initializes the database tables on startup.
-   For ISBN-based cover images, OpenLibrary returns a cover *only if
    available for that ISBN*.

------------------------------------------------------------------------

## 🎉 Enjoy Your Digital Library!

Feel free to expand the project with additional features such as: 
- API-based ISBN auto-fill
- UI improvements
- Book ratings
- AI-powered book recommendations

---

## 🤝 License

This project is for educational use.

---

## 💡 Author

Created by **[margarita-bykadorova](https://github.com/margarita-bykadorova)**  
