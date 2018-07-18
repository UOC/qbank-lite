import json

from paste.fixture import AppError

from testing_utilities import BaseTestCase, get_managers, create_new_gradebook


class BaseGradingTestCase(BaseTestCase):
    def setUp(self):
        super(BaseGradingTestCase, self).setUp()
        self.url = '/api/v1/grading'

    def tearDown(self):
        super(BaseGradingTestCase, self).tearDown()

    def assertDisplayText(self, first, second):
        self.assertEqual(
            first['formatTypeId'],
            first['formatTypeId']
        )
        self.assertEqual(
            first['languageTypeId'],
            first['languageTypeId']
        )
        self.assertEqual(
            first['scriptTypeId'],
            first['scriptTypeId']
        )
        self.assertEqual(
            first['text'],
            first['text']
        )


class GradebookCrUDTests(BaseGradingTestCase):
    """Test basic CRUD operations on gradebook

    """
    def num_gradebooks(self, val):
        gm = get_managers()['gm']

        self.assertEqual(
            gm.gradebooks.available(),
            val
        )

    def setUp(self):
        super(GradebookCrUDTests, self).setUp()
        self.url += '/gradebooks'
        self.num_gradebooks(0)
        self.bad_gradebook_id = 'grading.Gradebook%3A55203f0be7dde0815228bb41%40ODL.MIT.EDU'

    def tearDown(self):
        super(GradebookCrUDTests, self).tearDown()

    def create_gradebook(self, payload):
        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        gradebook = self.json(req)
        self.num_gradebooks(1)
        return gradebook

    def test_can_create_gradebooks_name_as_string(self):
        payload = {
            'name': 'my new log',
            'description': 'for testing with',
            'genusTypeId': 'gradebook-genus-type%3Adefault-gradebook%40ODL.MIT.EDU'
        }
        gradebook = self.create_gradebook(payload)
        self.assertEqual(
            gradebook['displayName']['text'],
            payload['name']
        )
        self.assertEqual(
            gradebook['description']['text'],
            payload['description']
        )

    def test_can_create_gradebooks_name_as_dict(self):
        payload = {
            'displayName': {
                'formatTypeId': 'format.text%3APlain%40okapia.net',
                'languageTypeId': '639-2%3AENG%40iso.org',
                'scriptTypeId': '15924%3ALATN%40iso.org',
                'text': 'Default Gradebook'
            },
            'description': {
                'formatTypeId': 'format.text%3APlain%40okapia.net',
                'languageTypeId': '639-2%3AENG%40iso.org',
                'scriptTypeId': '15924%3ALATN%40iso.org',
                'text': 'for testing with'
            },
            'genusTypeId': 'gradebook-genus-type%3Adefault-gradebook%40ODL.MIT.EDU'
        }
        gradebook = self.create_gradebook(payload)
        self.assertDisplayText(
            gradebook['displayName'],
            payload['displayName']
        )
        self.assertDisplayText(
            gradebook['description'],
            payload['description']
        )

    def test_can_list_gradebooks(self):
        req = self.app.get(self.url,
                           headers={'content-type': 'application/json'})
        self.ok(req)
        gradebook_list = self.json(req)
        self.assertEqual(len(gradebook_list), 0)

        gradebook = create_new_gradebook()
        self.num_gradebooks(1)
        req = self.app.get(self.url,
                           headers={'content-type': 'application/json'})
        self.ok(req)
        gradebook_list = self.json(req)
        self.assertEqual(len(gradebook_list), 1)
        for attr, val in gradebook.object_map.iteritems():
            self.assertEqual(
                val,
                gradebook_list[0][attr]
            )

    def test_can_get_details_of_gradebooks(self):
        gradebook = create_new_gradebook()
        self.num_gradebooks(1)
        url = self.url + '/' + str(gradebook.ident)
        req = self.app.get(url)
        self.ok(req)
        gradebook_details = self.json(req)

        for attr, val in gradebook.object_map.iteritems():
            self.assertEqual(
                val,
                gradebook_details[attr]
            )

    def test_invalid_gradebook_id_throws_exception(self):
        create_new_gradebook()
        url = self.url + '/x'
        self.assertRaises(AppError, self.app.get, url)

    def test_bad_gradebook_id_throws_exception(self):
        create_new_gradebook()
        url = self.url + '/' + self.bad_gradebook_id
        self.assertRaises(AppError, self.app.get, url)

    def test_can_update_gradebook(self):
        gradebook = create_new_gradebook()
        self.num_gradebooks(1)

        url = self.url + '/' + str(gradebook.ident)

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
            updated_gradebook = self.json(req)

            if case[0] == 'name':
                self.assertEqual(
                    updated_gradebook['displayName']['text'],
                    case[1]
                )
            else:
                self.assertEqual(
                    updated_gradebook['description']['text'],
                    case[1]
                )

        self.num_gradebooks(1)

    def test_can_update_gradebook_with_dics(self):
        gradebook = create_new_gradebook()
        self.num_gradebooks(1)

        url = self.url + '/' + str(gradebook.ident)

        test_cases = [('displayName', {
                            'formatTypeId': 'format.text%3APlain%40okapia.net',
                            'languageTypeId': '639-2%3AENG%40iso.org',
                            'scriptTypeId': '15924%3ALATN%40iso.org',
                            'text': 'a new name'
                        }),
                      ('description', {
                          'formatTypeId': 'format.text%3APlain%40okapia.net',
                          'languageTypeId': '639-2%3AENG%40iso.org',
                          'scriptTypeId': '15924%3ALATN%40iso.org',
                          'text': 'foobar'
                      })]
        for case in test_cases:
            payload = {
                case[0]: case[1]
            }
            req = self.app.put(url,
                               params=json.dumps(payload),
                               headers={'content-type': 'application/json'})
            self.ok(req)
            updated_gradebook = self.json(req)

            if case[0] == 'name':
                self.assertDisplayText(
                    updated_gradebook['displayName'],
                    case[1]
                )
            else:
                self.assertDisplayText(
                    updated_gradebook['description'],
                    case[1]
                )

        self.num_gradebooks(1)

    def test_update_with_invalid_id_throws_exception(self):
        create_new_gradebook()

        self.num_gradebooks(1)

        url = self.url + '/' + self.bad_gradebook_id

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

        self.num_gradebooks(1)

    def test_update_with_no_params_throws_exception(self):
        gradebook = create_new_gradebook()

        self.num_gradebooks(1)

        url = self.url + '/' + str(gradebook.ident)

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

        self.num_gradebooks(1)
        req = self.app.get(url)
        gradebook_fresh = self.json(req)

        gradebook_map = gradebook.object_map
        params_to_test = ['id', 'displayName', 'description']
        for param in params_to_test:
            self.assertEqual(
                gradebook_map[param],
                gradebook_fresh[param]
            )
