import json
import web
import utilities

import commenting_utilities as cutils

urls = (
    "/books/(.*)/?", "BookDetails",
    "/books/?", "BookList"
)

class BookList(utilities.BaseClass):
    """
    List all available books.
    api/v1/commenting/books/

    POST allows you to create a new book, requires two parameters:
      * name
      * description

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
      {"name" : "a new book",
       "description" : "this is a test"}

    """
    @utilities.format_response
    def GET(self):
        """
        List all available books
        """
        try:
            cm = cutils.get_commenting_manager()
            books = utilities.extract_items(cm.books)
            return books
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self):
        """
        Create a new book, if authorized

        """
        try:
            cm = cutils.get_commenting_manager()
            form = cm.get_book_form_for_create([])
            data = self.data()

            form = utilities.set_form_basics(form, data)

            new_book = utilities.convert_dl_object(cm.create_book(form))

            if 'aliasId' in data:
                cm.alias_bank(utilities.clean_id(json.loads(new_book)['id']),
                              utilities.clean_id(data['aliasId']))

            return new_book
        except Exception as ex:
            utilities.handle_exceptions(ex)


class BookDetails(utilities.BaseClass):
    """
    Shows details for a specific book.
    api/v1/commenting/books/<book_id>/

    GET, PUT, DELETE
    PUT will update the book. Only changed attributes need to be sent.
    DELETE will remove the book.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       PUT {"name" : "a new book"}
    """
    @utilities.format_response
    def GET(self, book_id):
        try:
            cm = cutils.get_commenting_manager()
            commenting_book = cm.get_book(utilities.clean_id(book_id))
            book = utilities.convert_dl_object(commenting_book)
            return book
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def PUT(self, book_id):
        try:
            cm = cutils.get_commenting_manager()
            data = self.data()

            form = cm.get_book_form_for_update(utilities.clean_id(book_id))

            utilities.verify_at_least_one_key_present(self.data(), ['name', 'description', 'displayName'])

            form = utilities.set_form_basics(form, data)
            updated_book = cm.update_book(form)

            if 'aliasId' in data:
                cm.alias_bank(updated_book.ident, utilities.clean_id(data['aliasId']))

            book = utilities.convert_dl_object(updated_book)
            return book
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def DELETE(self, book_id):
        try:
            cm = cutils.get_commenting_manager()
            data = cm.delete_book(utilities.clean_id(book_id))
            return utilities.success()
        except Exception as ex:
            utilities.handle_exceptions(ex)


app_commenting = web.application(urls, locals())
