import json
import web
import utilities

from urllib import quote

import commenting_utilities as cutils

urls = (
    "/books/(.*)/comments/(.*)/?", "CommentsDetails",
    "/books/(.*)/comments/?", "CommentsList",
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


class CommentsList(utilities.BaseClass):
    """
    Get or add comments to a book
    api/v1/commeting/books/<book_id>/comments/

    GET, POST
    GET to view current comments.
    POST to create a new comment

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"gradeSystemId" : "grading.GradeSystem%3A123%40MIT-ODL"}
    """
    @utilities.format_response
    def GET(self, book_id):
        try:
            cm = cutils.get_commenting_manager()
            book = cm.get_book(utilities.clean_id(book_id))

            inputs = self.data()

            if 'genusTypeId' in inputs or 'referenceId' in inputs or 'commentorId' in inputs:
                querier = book.get_comment_query()
                if 'genusTypeId' in inputs:
                    if utilities.unescaped(inputs['genusTypeId']):
                        querier.match_genus_type(quote(inputs['genusTypeId'], safe='/ '), match=True)
                    else:
                        querier.match_genus_type(inputs['genusTypeId'], match=True)
                if 'referenceId' in inputs:
                    if utilities.unescaped(inputs['referenceId']):
                        querier.match_reference_id(quote(inputs['referenceId'], safe='/ '), match=True)
                    else:
                        querier.match_reference_id(inputs['referenceId'], match=True)
                if 'commentorId' in inputs:
                    if utilities.unescaped(inputs['commentorId']):
                        querier.match_commentor_id(quote(inputs['commentorId'], safe='/ '), match=True)
                    else:
                        querier.match_commentor_id(inputs['commentorId'], match=True)

                commenting_comments = book.get_comments_by_query(querier)
            else:
                commenting_comments = book.get_comments()

            comments = utilities.extract_items(commenting_comments)
            return comments
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self, book_id):
        try:
            cm = cutils.get_commenting_manager()
            book = cm.get_book(utilities.clean_id(book_id))

            data = self.data()
            utilities.verify_keys_present(data, ['referenceId', 'text'])

            form = book.get_comment_form_for_create(utilities.clean_id(data['referenceId']), [])
            form = utilities.set_form_basics(form, data)
            form.set_text(utilities.create_display_text(data['text']))

            column = utilities.convert_dl_object(book.create_comment(form))

            return column
        except Exception as ex:
            utilities.handle_exceptions(ex)

class CommentsDetails(utilities.BaseClass):
    """
    Get comments details
    api/v1/commenting/books/<book_id>/comments/<comment_id>/

    GET, PUT, DELETE
    PUT to modify an existing comment (text.).
        Include only the changed parameters.
    DELETE to remove the comment.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"text" : "something"}
    """
    @utilities.format_response
    def GET(self, book_id, comment_id):
        try:
            cm = cutils.get_commenting_manager()
            book = cm.get_book(utilities.clean_id(book_id))
            commenting_comment = book.get_comment(utilities.clean_id(comment_id))
            comment = utilities.convert_dl_object(commenting_comment)
            return comment
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def PUT(self, book_id, comment_id):
        try:
            cm = cutils.get_commenting_manager()
            data = self.data()
            utilities.verify_at_least_one_key_present(data,
                                                      ['name', 'displayName', 'description', 'text'])

            book = cm.get_book(utilities.clean_id(book_id))
            commenting_comment = book.get_comment(utilities.clean_id(comment_id))

            form = book.get_comment_form_for_update(commenting_comment.ident)
            form = utilities.set_form_basics(form, data)
            if 'text' in data:
                form.set_text(utilities.create_display_text(data['text']))

            book.update_comment(form)

            comment = utilities.convert_dl_object(book.get_comment(commenting_comment.ident))
            return comment
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def DELETE(self, book_id, comment_id):
        try:
            cm = cutils.get_commenting_manager()
            book = cm.get_book(utilities.clean_id(book_id))
            data = book.delete_comment(utilities.clean_id(comment_id))
            return utilities.success()
        except Exception as ex:
            utilities.handle_exceptions(ex)


app_commenting = web.application(urls, locals())
