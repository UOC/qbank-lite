import json

from dlkit.runtime.primordium import Id

from paste.fixture import AppError

from testing_utilities import BaseTestCase, get_managers, create_new_book


class BaseCommentingTestCase(BaseTestCase):
    def setUp(self):
        super(BaseCommentingTestCase, self).setUp()
        self.url = '/api/v1/commenting'

    def tearDown(self):
        super(BaseCommentingTestCase, self).tearDown()

    def create_new_comment(self, book, reference_id):
        cm = get_managers()['cm']

        book = cm.get_book(book.ident)

        form = book.get_comment_form_for_create(reference_id, [])
        form.set_display_name("for testing only")
        form.set_text("text for testing only")

        new_comment = book.create_comment(form)

        return new_comment

    def display_text(self, text):
        return {
            'formatTypeId': 'TextFormats%3APLAIN%40okapia.net',
            'languageTypeId': '639-2%3AENG%40ISO',
            'scriptTypeId': '15924%3ALATN%40ISO',
            'text': text
        }

    def assertDisplayText(self, first, second):
        self.assertEqual(
            first['formatTypeId'],
            second['formatTypeId']
        )
        self.assertEqual(
            first['languageTypeId'],
            second['languageTypeId']
        )
        self.assertEqual(
            first['scriptTypeId'],
            second['scriptTypeId']
        )
        self.assertEqual(
            first['text'],
            second['text']
        )


class BookCRUDTests(BaseCommentingTestCase):
    """Test basic CRUD operations on books

    """
    def num_books(self, val):
        cm = get_managers()['cm']

        self.assertEqual(
            cm.books.available(),
            val
        )

    def setUp(self):
        super(BookCRUDTests, self).setUp()
        self.url += '/books'
        self.num_books(0)
        self.bad_book_id = 'commenting.Book%3A55203f0be7dde0815228bb41%40ODL.MIT.EDU'

    def tearDown(self):
        super(BookCRUDTests, self).tearDown()

    def create_book(self, payload):
        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        book = self.json(req)
        self.num_books(1)
        return book

    def test_can_create_books_name_as_string(self):
        payload = {
            'name': 'my new book',
            'description': 'for testing with',
            'genusTypeId': 'book-genus-type%3Adefault-book%40ODL.MIT.EDU'
        }
        book = self.create_book(payload)
        self.assertEqual(
            book['displayName']['text'],
            payload['name']
        )
        self.assertEqual(
            book['description']['text'],
            payload['description']
        )

    def test_can_create_books_name_as_dict(self):
        payload = {
            'displayName': self.display_text('Default Book'),
            'description': self.display_text('for testing with'),
            'genusTypeId': 'book-genus-type%3Adefault-book%40ODL.MIT.EDU'
        }
        book = self.create_book(payload)
        for key in ['displayName', 'description']:
            self.assertDisplayText(
                book[key],
                payload[key]
            )

    def test_can_list_books(self):
        req = self.app.get(self.url)
        self.ok(req)
        book_list = self.json(req)
        self.assertEqual(len(book_list), 0)

        book = create_new_book()
        self.num_books(1)
        req = self.app.get(self.url)
        self.ok(req)
        book_list = self.json(req)
        self.assertEqual(len(book_list), 1)
        for attr, val in book.object_map.iteritems():
            self.assertEqual(
                val,
                book_list[0][attr]
            )

    def test_can_get_details_of_books(self):
        book = create_new_book()
        self.num_books(1)
        url = self.url + '/' + str(book.ident)
        req = self.app.get(url)
        self.ok(req)
        book_details = self.json(req)

        for attr, val in book.object_map.iteritems():
            self.assertEqual(
                val,
                book_details[attr]
            )

    def test_invalid_book_id_throws_exception(self):
        create_new_book()
        url = self.url + '/x'
        self.assertRaises(AppError, self.app.get, url)

    def test_bad_book_id_throws_exception(self):
        create_new_book()
        url = self.url + '/' + self.bad_book_id
        self.assertRaises(AppError, self.app.get, url)

    def test_can_update_book(self):
        book = create_new_book()
        self.num_books(1)

        url = self.url + '/' + str(book.ident)

        test_cases = [('name', 'a new name'),
                      ('description', 'foobar')]
        for case in test_cases:
            payload = {
                case[0]: case[1]
            }
            req = self.app.put(url,
                               params=json.dumps(payload),
                               headers={'content-type': 'application/json'})
            self.ok(req)
            updated_book = self.json(req)

            if case[0] == 'name':
                self.assertEqual(
                    updated_book['displayName']['text'],
                    case[1]
                )
            else:
                self.assertEqual(
                    updated_book['description']['text'],
                    case[1]
                )

        self.num_books(1)

    def test_can_update_book_with_dics(self):
        book = create_new_book()
        self.num_books(1)

        url = self.url + '/' + str(book.ident)

        test_cases = [('displayName', self.display_text('a new name')),
                      ('description', self.display_text('foobar'))]
        for case in test_cases:
            payload = {
                case[0]: case[1]
            }
            req = self.app.put(url,
                               params=json.dumps(payload),
                               headers={'content-type': 'application/json'})
            self.ok(req)
            updated_gradebook = self.json(req)

            if case[0] == 'displayName':
                self.assertDisplayText(
                    updated_gradebook['displayName'],
                    case[1]
                )
            else:
                self.assertDisplayText(
                    updated_gradebook['description'],
                    case[1]
                )

        self.num_books(1)

    def test_update_with_invalid_id_throws_exception(self):
        create_new_book()

        self.num_books(1)

        url = self.url + '/' + self.bad_book_id

        test_cases = [('name', 'a new name'),
                      ('description', 'foobar')]
        for case in test_cases:
            payload = {
                case[0]: case[1]
            }
            self.assertRaises(AppError,
                              self.app.put,
                              url,
                              params=json.dumps(payload),
                              headers={'content-type': 'application/json'})

        self.num_books(1)

    def test_update_with_no_params_throws_exception(self):
        book = create_new_book()

        self.num_books(1)

        url = self.url + '/' + str(book.ident)

        test_cases = [('foo', 'bar'),
                      ('bankId', 'foobar')]
        for case in test_cases:
            payload = {
                case[0]: case[1]
            }
            self.assertRaises(AppError,
                              self.app.put,
                              url,
                              params=json.dumps(payload),
                              headers={'content-type': 'application/json'})

        self.num_books(1)
        req = self.app.get(url)
        book_fresh = self.json(req)

        gradebook_map = book.object_map
        params_to_test = ['id', 'displayName', 'description']
        for param in params_to_test:
            self.assertEqual(
                gradebook_map[param],
                book_fresh[param]
            )

    def test_can_delete_book(self):
        book = create_new_book()

        self.num_books(1)

        url = self.url + '/' + str(book.ident)
        req = self.app.delete(url)
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        self.num_books(0)

    def test_trying_to_delete_book_with_invalid_id_throws_exception(self):
        create_new_book()

        self.num_books(1)

        url = self.url + '/' + self.bad_book_id
        self.assertRaises(AppError, self.app.delete, url)

        self.num_books(1)


class CommentCRUDTests(BaseCommentingTestCase):
    def num_comments(self, val):
        cm = get_managers()['cm']

        book = cm.get_book(self.book.ident)
        self.assertEqual(
            book.get_comments().available(),
            val
        )

    def create_new_comment(self):
        return super(CommentCRUDTests, self).create_new_comment(self.book, self.reference)

    def setUp(self):
        super(CommentCRUDTests, self).setUp()
        self.book = create_new_book()
        self.reference = Id('reference.id%3A55203f0be7dde0815228bb41%40ODL.MIT.EDU')
        self.bad_book_id = 'commenting.Book%3A55203f0be7dde0815228bb41%40ODL.MIT.EDU'
        self.bad_comment_id = 'commenting.Comment%3A55203f0be7dde0815228bb41%40ODL.MIT.EDU'
        self.bad_book_url = self.url + '/books/{0}/comments'.format(str(self.bad_book_id))
        self.url += '/books/{0}/comments'.format(str(self.book.ident))
        self.num_comments(0)

    def tearDown(self):
        super(CommentCRUDTests, self).tearDown()

    def test_can_list_book_comments(self):
        req = self.app.get(self.url)
        self.ok(req)
        comments_list = self.json(req)
        self.assertEqual(len(comments_list), 0)

        comment = self.create_new_comment()
        self.num_comments(1)
        req = self.app.get(self.url)
        self.ok(req)
        comments_list = self.json(req)
        self.assertEqual(len(comments_list), 1)
        for attr, val in comment.object_map.iteritems():
            if attr == 'startDate' or attr == 'endDate':
                self.assertEqual(
                    val.isoformat(),
                    comments_list[0][attr]
                )
            else:
                self.assertEqual(
                    val,
                    comments_list[0][attr]
                )

    def test_trying_to_get_comments_with_invalid_book_id_throws_exception(self):
        self.assertRaises(AppError, self.app.get, self.bad_book_url)

        self.num_comments(0)

    def test_trying_to_create_comment_with_invalid_book_id_throws_exception(self):
        payload = {
            'name': 'my new comment',
            'description': 'for testing with',
            'genusTypeId': 'comment-genus-type%3Adefault-comment%40ODL.MIT.EDU',

        }
        self.assertRaises(AppError,
                          self.app.post,
                          self.bad_book_url,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

        self.num_comments(0)

    def test_trying_to_create_comment_without_reference_throws_exception(self):
        payload = {
            'name': 'my new comment',
            'text': 'something',
            'description': 'for testing with',
            'genusTypeId': 'comment-genus-type%3Adefault-comment%40ODL.MIT.EDU',

        }
        self.assertRaises(AppError,
                          self.app.post,
                          self.url,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

        self.num_comments(0)

    def test_trying_to_create_comment_without_text_throws_exception(self):
        payload = {
            'name': 'my new comment',
            'description': 'for testing with',
            'genusTypeId': 'comment-genus-type%3Adefault-comment%40ODL.MIT.EDU',
            'referenceId': str(self.reference.identifier)
        }
        self.assertRaises(AppError,
                          self.app.post,
                          self.url,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

        self.num_comments(0)

    def create_comment(self, payload):
        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        comment = self.json(req)
        self.num_comments(1)
        for key in ['referenceId', 'genusTypeId']:
            self.assertEqual(
                comment[key],
                payload[key]
            )
        return comment

    def test_can_create_comment_name_as_string(self):
        payload = {
            'name': 'my new comment',
            'description': 'for testing with',
            'genusTypeId': 'comment-genus-type%3Adefault-comment%40ODL.MIT.EDU',
            'text': 'some text',
            'referenceId': str(self.reference.identifier)
        }
        comment = self.create_comment(payload)
        self.assertEqual(
            comment['displayName']['text'],
            payload['name']
        )
        self.assertEqual(
            comment['description']['text'],
            payload['description']
        )
        self.assertEqual(
            comment['text']['text'],
            payload['text']
        )

    def test_can_create_comment_name_as_dict(self):
        payload = {
            'displayName': self.display_text('my new comment'),
            'description': self.display_text('for testing with'),
            'genusTypeId': 'comment-genus-type%3Adefault-comment%40ODL.MIT.EDU',
            'text': self.display_text('some text'),
            'referenceId': str(self.reference.identifier)
        }
        comment = self.create_comment(payload)
        for key in ['displayName', 'description', 'text']:
            self.assertDisplayText(
                comment[key],
                payload[key]
            )

    def test_can_get_comment_details(self):
        comment = self.create_new_comment()

        self.num_comments(1)

        url = self.url + '/' + str(comment.ident)

        req = self.app.get(url)
        self.ok(req)
        comment_details = self.json(req)

        for attr, val in comment.object_map.iteritems():
            if attr == 'startDate' or attr == 'endDate':
                self.assertEqual(
                    val.isoformat(),
                    comment_details[attr]
                )
            else:
                self.assertEqual(
                    val,
                    comment_details[attr]
                )

    def test_invalid_comment_id_throws_exception(self):
        self.create_new_comment()
        self.num_comments(1)

        url = self.url + '/x'
        self.assertRaises(AppError, self.app.get, url)

    def test_bad_book_id_throws_exception(self):
        comment = self.create_new_comment()
        self.num_comments(1)

        url = self.bad_book_url + '/' + str(comment.ident)
        self.assertRaises(AppError, self.app.get, url)

    def test_can_update_comment(self):
        comment = self.create_new_comment()
        self.num_comments(1)

        url = self.url + '/' + str(comment.ident)

        test_cases = [('name', 'a new name'),
                      ('description', 'foobar'),
                      ('text', 'some text')]
        for case in test_cases:
            payload = {
                case[0]: case[1]
            }
            req = self.app.put(url,
                               params=json.dumps(payload),
                               headers={'content-type': 'application/json'})
            self.ok(req)
            updated_comment = self.json(req)

            if case[0] == 'name':
                self.assertEqual(
                    updated_comment['displayName']['text'],
                    case[1]
                )
            elif case[0] == 'description':
                self.assertEqual(
                    updated_comment['description']['text'],
                    case[1]
                )
            else:
                self.assertEqual(
                    updated_comment['text']['text'],
                    case[1]
                )

        self.num_comments(1)

    def test_can_update_comment_with_dics(self):
        comment = self.create_new_comment()
        self.num_comments(1)

        url = self.url + '/' + str(comment.ident)

        test_cases = [('displayName', self.display_text('a new name')),
                      ('description', self.display_text('foobar')),
                      ('text', self.display_text('some text'))]
        for case in test_cases:
            payload = {
                case[0]: case[1]
            }
            req = self.app.put(url,
                               params=json.dumps(payload),
                               headers={'content-type': 'application/json'})
            self.ok(req)
            updated_comment = self.json(req)

            if case[0] == 'displayName':
                self.assertDisplayText(
                    updated_comment['displayName'],
                    case[1]
                )
            elif case[0] == 'description':
                self.assertDisplayText(
                    updated_comment['description'],
                    case[1]
                )
            else:
                self.assertDisplayText(
                    updated_comment['text'],
                    case[1]
                )

        self.num_comments(1)

    def test_update_with_invalid_id_throws_exception(self):
        self.create_new_comment()

        self.num_comments(1)

        url = self.url + '/' + self.bad_comment_id

        test_cases = [('name', 'a new name'),
                      ('description', 'foobar'),
                      ('text', 'some text')]
        for case in test_cases:
            payload = {
                case[0]: case[1]
            }
            self.assertRaises(AppError,
                              self.app.put,
                              url,
                              params=json.dumps(payload),
                              headers={'content-type': 'application/json'})

        self.num_comments(1)

    def test_update_with_no_params_throws_exception(self):
        comment = self.create_new_comment()
        self.num_comments(1)

        url = self.url + '/' + str(comment.ident)

        test_cases = [('foo', 'bar'),
                      ('bankId', 'foobar')]
        for case in test_cases:
            payload = {
                case[0]: case[1]
            }
            self.assertRaises(AppError,
                              self.app.put,
                              url,
                              params=json.dumps(payload),
                              headers={'content-type': 'application/json'})

        self.num_comments(1)
        req = self.app.get(url)
        comment_fresh = self.json(req)

        comment_map = comment.object_map
        params_to_test = ['id', 'displayName', 'description', 'text']
        for param in params_to_test:
            self.assertEqual(
                comment_map[param],
                comment_fresh[param]
            )

    def test_can_delete_comment(self):
        comment = self.create_new_comment()
        self.num_comments(1)

        url = self.url + '/' + str(comment.ident)
        req = self.app.delete(url)
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        self.num_comments(0)

    def test_trying_to_delete_comment_with_invalid_id_throws_exception(self):
        self.create_new_comment()
        self.num_comments(1)

        url = self.url + '/' + self.bad_comment_id
        self.assertRaises(AppError, self.app.delete, url)

        self.num_comments(1)

    def test_trying_to_delete_comment_with_invalid_book_id_throws_exception(self):
        comment = self.create_new_comment()
        self.num_comments(1)

        url = self.bad_book_url + '/' + str(comment.ident)
        self.assertRaises(AppError, self.app.delete, url)

        self.num_comments(1)
