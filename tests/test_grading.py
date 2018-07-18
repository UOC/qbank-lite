import json

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

    def tearDown(self):
        super(GradebookCrUDTests, self).tearDown()

    def test_can_create_gradebooks_name_as_string(self):
        self.num_gradebooks(0)
        payload = {
            'name': 'my new log',
            'description': 'for testing with',
            'genusTypeId': 'gradebook-genus-type%3Adefault-gradebook%40ODL.MIT.EDU'
        }
        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        gradebook = self.json(req)
        self.assertEqual(
            gradebook['displayName']['text'],
            payload['name']
        )
        self.assertEqual(
            gradebook['description']['text'],
            payload['description']
        )
        self.num_gradebooks(1)

    def test_can_create_gradebooks_name_as_dict(self):
        self.num_gradebooks(0)
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
        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        gradebook = self.json(req)
        self.assertDisplayText(
            gradebook['displayName'],
            payload['displayName']
        )
        self.assertDisplayText(
            gradebook['description'],
            payload['description']
        )
        self.assertDictEqual(
            gradebook['description'],
            payload['description']
        )
        self.num_gradebooks(1)

    def test_can_list_gradebooks(self):
        self.num_gradebooks(0)
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
