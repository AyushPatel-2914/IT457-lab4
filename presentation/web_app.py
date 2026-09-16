"""Flask web UI.

A second presentation tier alongside the CLI. It talks to exactly the same
BookService and knows nothing about SQLite, SQL, or where books are stored.

Note that the HTML forms carry no `required`, `min`, `pattern` or `type=number`
attributes. That is deliberate: if the browser rejected bad input, a validation
rule would effectively live in the presentation tier. Every field is submitted as
a plain string and the business tier decides whether it is acceptable.
"""

import os

from flask import Flask, flash, redirect, render_template, request, url_for

from business.book_service import BookService
from business.errors import LibraryError

FIELDS = ("title", "author", "isbn", "year", "quantity")


def create_app(service: BookService, backend_name: str = "SQLite") -> Flask:
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    @app.context_processor
    def inject_backend():
        return {"backend_name": backend_name}

    @app.route("/")
    def index():
        query = request.args.get("q", "").strip()
        books = service.search_books(query) if query else service.list_books()
        return render_template("index.html", books=books, query=query)

    @app.route("/add", methods=["GET", "POST"])
    def add():
        if request.method == "GET":
            return render_template("form.html", mode="add", book=None, values={})

        values = {field: request.form.get(field, "") for field in FIELDS}
        try:
            book = service.add_book(**values)
        except LibraryError as error:
            flash(str(error), "error")
            return render_template("form.html", mode="add", book=None, values=values)

        flash(f"Added '{book.title}'.", "success")
        return redirect(url_for("index"))

    @app.route("/edit/<int:book_id>", methods=["GET", "POST"])
    def edit(book_id):
        try:
            book = service.get_book(book_id)
        except LibraryError as error:
            flash(str(error), "error")
            return redirect(url_for("index"))

        if request.method == "GET":
            return render_template("form.html", mode="edit", book=book, values={})

        values = {field: request.form.get(field, "") for field in FIELDS}
        try:
            service.update_book(book_id, **values)
        except LibraryError as error:
            flash(str(error), "error")
            return render_template("form.html", mode="edit", book=book, values=values)

        flash(f"Updated book {book_id}.", "success")
        return redirect(url_for("index"))

    @app.route("/checkout/<int:book_id>", methods=["POST"])
    def checkout(book_id):
        try:
            book = service.check_out_book(book_id)
        except LibraryError as error:
            flash(str(error), "error")
        else:
            flash(f"Checked out '{book.title}'. {book.quantity} left.", "success")
        return redirect(request.referrer or url_for("index"))

    @app.route("/delete/<int:book_id>", methods=["POST"])
    def delete(book_id):
        try:
            service.delete_book(book_id)
        except LibraryError as error:
            flash(str(error), "error")
        else:
            flash(f"Deleted book {book_id}.", "success")
        return redirect(url_for("index"))

    return app
