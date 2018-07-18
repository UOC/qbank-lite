import json

from dlkit.runtime.primordium import Id

from paste.fixture import AppError

from testing_utilities import BaseTestCase, get_managers, create_new_gradebook


class BaseGradingTestCase(BaseTestCase):
    def setUp(self):
        super(BaseGradingTestCase, self).setUp()
        self.url = '/api/v1/grading'

    def tearDown(self):
        super(BaseGradingTestCase, self).tearDown()

    def setup_gradesystem(self, gradebook, text):
        gm = get_managers()['gm']

        gradebook = gm.get_gradebook(gradebook.ident)

        form = gradebook.get_grade_system_form_for_create([])
        form.set_display_name(text)

        new_grade_system = gradebook.create_grade_system(form)

        return new_grade_system

    def create_new_gradebook_column(self, gradebook, grade_system):
        gm = get_managers()['gm']

        gradebook = gm.get_gradebook(gradebook.ident)

        form = gradebook.get_gradebook_column_form_for_create([])
        form.set_display_name("for testing only")
        form.set_grade_system(grade_system.ident)

        new_column = gradebook.create_gradebook_column(form)

        return new_column

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


class GradebookCRUDTests(BaseGradingTestCase):
    """Test basic CRUD operations on gradebook

    """
    def num_gradebooks(self, val):
        gm = get_managers()['gm']

        self.assertEqual(
            gm.gradebooks.available(),
            val
        )

    def setUp(self):
        super(GradebookCRUDTests, self).setUp()
        self.url += '/gradebooks'
        self.num_gradebooks(0)
        self.bad_gradebook_id = 'grading.Gradebook%3A55203f0be7dde0815228bb41%40ODL.MIT.EDU'

    def tearDown(self):
        super(GradebookCRUDTests, self).tearDown()

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
            'name': 'my new gradebook',
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
            'displayName': self.display_text('Default Gradebook'),
            'description': self.display_text('for testing with'),
            'genusTypeId': 'gradebook-genus-type%3Adefault-gradebook%40ODL.MIT.EDU'
        }
        gradebook = self.create_gradebook(payload)
        for key in ['displayName', 'description']:
            self.assertDisplayText(
                gradebook[key],
                payload[key]
            )

    def test_can_list_gradebooks(self):
        req = self.app.get(self.url)
        self.ok(req)
        gradebook_list = self.json(req)
        self.assertEqual(len(gradebook_list), 0)

        gradebook = create_new_gradebook()
        self.num_gradebooks(1)
        req = self.app.get(self.url)
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

    def test_can_delete_gradebook(self):
        gradebook = create_new_gradebook()

        self.num_gradebooks(1)

        url = self.url + '/' + str(gradebook.ident)
        req = self.app.delete(url)
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        self.num_gradebooks(0)

    def test_trying_to_delete_gradebook_with_invalid_id_throws_exception(self):
        create_new_gradebook()

        self.num_gradebooks(1)

        url = self.url + '/' + self.bad_gradebook_id
        self.assertRaises(AppError, self.app.delete, url)

        self.num_gradebooks(1)


class GradeSystemCRUDTests(BaseGradingTestCase):
    """Test basic CRUD operations on GradeSystems

    """
    def num_gradesystems(self, val):
        gm = get_managers()['gm']

        gradebook = gm.get_gradebook(self.gradebook.ident)
        self.assertEqual(
            gradebook.get_grade_systems().available(),
            val
        )

    def setup_gradesystem(self, text):
        return super(GradeSystemCRUDTests, self).setup_gradesystem(self.gradebook, text)

    def setUp(self):
        super(GradeSystemCRUDTests, self).setUp()
        self.gradebook = create_new_gradebook()
        self.bad_gradebook_id = 'grading.Gradebook%3A55203f0be7dde0815228bb41%40ODL.MIT.EDU'
        self.bad_gradesystem_id = 'grading.GradeSystem%3A55203f0be7dde0815228bb41%40ODL.MIT.EDU'
        self.bad_gradebook_url = self.url + '/gradebooks/{0}/gradesystems'.format(str(self.bad_gradebook_id))
        self.gradebook_url = self.url + '/gradebooks/{0}'.format(str(self.gradebook.ident))
        self.url += '/gradebooks/{0}/gradesystems'.format(str(self.gradebook.ident))
        self.num_gradesystems(0)

    def tearDown(self):
        super(GradeSystemCRUDTests, self).tearDown()

    def test_can_get_gradesystems(self):
        req = self.app.get(self.url)
        self.ok(req)
        gradesystem_list = self.json(req)
        self.assertEqual(len(gradesystem_list), 0)

        gradesystem = self.setup_gradesystem('foo')
        self.num_gradesystems(1)

        req = self.app.get(self.url)
        self.ok(req)
        gradesystem_list = self.json(req)
        self.assertEqual(
            len(gradesystem_list),
            1
        )
        for attr, val in gradesystem.object_map.iteritems():
            self.assertEqual(
                val,
                gradesystem_list[0][attr]
            )

    def test_can_create_gradesystem_not_based_on_scores(self):
        payload = {
            'displayName': self.display_text('Scored based grade system'),
            'description': self.display_text('for testing with'),
            'genusTypeId': 'grade-system%3Apercentage%40UOC.EDU',
            'basedOnGrades': False,
            'highestNumericScore': 100,
            'lowestNumericScore': 0,
            'numericScoreIncrement': 10
        }

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

        data = self.json(req)
        self.assertIsNotNone(data['id'])
        for attr, val in payload.iteritems():
            if attr == 'displayName' or attr == 'description':
                self.assertDisplayText(val, data[attr])
            else:
                self.assertEqual(
                    val,
                    data[attr]
                )
        self.num_gradesystems(1)

    def test_trying_to_create_gradesystem_on_invalid_gradebook_throws_exception(self):
        payload = {
            'displayName': self.display_text('Scored based grade system'),
            'description': self.display_text('for testing with'),
            'genusTypeId': 'grade-system%3Apercentage%40UOC.EDU',
            'basedOnGrades': False,
            'highestNumericScore': 100,
            'lowestNumericScore': 0,
            'numericScoreIncrement': 10
        }
        self.assertRaises(AppError,
                          self.app.post,
                          self.bad_gradebook_url,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

        self.num_gradesystems(0)

    def test_trying_to_create_gradesystem_not_based_on_scores_with_no_numeric_scores_throws_exception(self):
        test_cases = [('highestNumericScore', 100),
                      ('lowestNumericScore', 0),
                      ('numericScoreIncrement', 10)]
        for case in test_cases:
            payload = {
                'displayName': self.display_text('Scored based grade system'),
                'description': self.display_text('for testing with'),
                'genusTypeId': 'grade-system%3Apercentage%40UOC.EDU',
                'basedOnGrades': False,
                case[0]: case[1]
            }
            self.assertRaises(AppError,
                              self.app.post,
                              self.url,
                              params=json.dumps(payload),
                              headers={'content-type': 'application/json'})

        self.num_gradesystems(0)

    def test_can_create_gradesystem_based_on_scores(self):
        payload = {
            'displayName': self.display_text('Scored based grade system'),
            'description': self.display_text('for testing with'),
            'genusTypeId': 'grade-system%3Apercentage%40UOC.EDU',
            'basedOnGrades': True,
            'grades': [
                {
                    "inputScoreStartRange": 0,
                    "inputScoreEndRange": 25,
                    "outputScore": 0,
                    "name": "No Assoliment",
                    "description": "No Assoliment"
                },
                {
                    "inputScoreStartRange": 25,
                    "inputScoreEndRange": 50,
                    "outputScore": 0,
                    "name": "Assolit Parcialment",
                    "description": "Assolit Parcialment"
                }
            ]
        }

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

        data = self.json(req)
        self.assertIsNotNone(data['id'])
        self.assertEqual(len(data['grades']), len(payload['grades']))
        for attr, val in payload.iteritems():
            if attr == 'displayName' or attr == 'description':
                self.assertDisplayText(val, data[attr])
            elif attr == 'grades':
                pass
            else:
                self.assertEqual(
                    val,
                    data[attr]
                )
        self.num_gradesystems(1)

    def test_trying_to_create_gradesystem_based_on_scores_with_grades_throws_exception(self):
        payload = {
            'displayName': self.display_text('Scored based grade system'),
            'description': self.display_text('for testing with'),
            'genusTypeId': 'grade-system%3Apercentage%40UOC.EDU',
            'basedOnGrades': True
        }

        self.assertRaises(AppError,
                          self.app.post,
                          self.url,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

        self.num_gradesystems(0)

        payload['grades'] = True

        self.assertRaises(AppError,
                          self.app.post,
                          self.url,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

        self.num_gradesystems(0)

    def test_can_get_gradesystem_details(self):
        grade_system = self.setup_gradesystem("testing")

        self.num_gradesystems(1)

        url = self.url + '/' + str(grade_system.ident)

        req = self.app.get(url)
        self.ok(req)
        gradesystem_details = self.json(req)

        for attr, val in grade_system.object_map.iteritems():
            self.assertEqual(
                val,
                gradesystem_details[attr]
            )

    def test_invalid_gradesystem_id_throws_exception(self):
        self.setup_gradesystem("testing")
        self.num_gradesystems(1)

        url = self.url + '/x'
        self.assertRaises(AppError, self.app.get, url)

    def test_bad_gradesystem_id_throws_exception(self):
        self.setup_gradesystem("testing")
        self.num_gradesystems(1)

        url = self.url + '/' + self.bad_gradesystem_id
        self.assertRaises(AppError, self.app.get, url)

    def test_bad_gradebook_id_throws_exception(self):
        grade_system = self.setup_gradesystem("testing")
        self.num_gradesystems(1)

        url = self.bad_gradebook_url + '/' + str(grade_system.ident)
        self.assertRaises(AppError, self.app.get, url)

    def test_can_update_gradesystem(self):
        grade_system = self.setup_gradesystem("test")

        self.num_gradesystems(1)

        url = self.url + '/' + str(grade_system.ident)

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
            updated_grade_system = self.json(req)

            if case[0] == 'name':
                self.assertEqual(
                    updated_grade_system['displayName']['text'],
                    case[1]
                )
            else:
                self.assertEqual(
                    updated_grade_system['description']['text'],
                    case[1]
                )

        self.num_gradesystems(1)

    def test_can_update_gradesystem_with_dics(self):
        grade_system = self.setup_gradesystem("test")

        self.num_gradesystems(1)

        url = self.url + '/' + str(grade_system.ident)

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
            updated_grade_system = self.json(req)

            if case[0] == 'displayName':
                self.assertDisplayText(
                    updated_grade_system['displayName'],
                    case[1]
                )
            else:
                self.assertDisplayText(
                    updated_grade_system['description'],
                    case[1]
                )

        self.num_gradesystems(1)

    def test_update_with_invalid_id_throws_exception(self):
        self.setup_gradesystem("Test")

        self.num_gradesystems(1)

        url = self.url + '/' + self.bad_gradesystem_id

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

        self.num_gradesystems(1)

    def test_update_with_no_params_throws_exception(self):
        grade_system = self.setup_gradesystem("Test")

        self.num_gradesystems(1)

        url = self.url + '/' + str(grade_system.ident)

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

        self.num_gradesystems(1)
        req = self.app.get(url)
        grade_system_fresh = self.json(req)

        grade_system_map = grade_system.object_map
        params_to_test = ['id', 'displayName', 'description']
        for param in params_to_test:
            self.assertEqual(
                grade_system_map[param],
                grade_system_fresh[param]
            )

    def test_can_delete_gradesystem(self):
        grade_system = self.setup_gradesystem("Test")

        self.num_gradesystems(1)

        url = self.url + '/' + str(grade_system.ident)
        req = self.app.delete(url)
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        self.num_gradesystems(0)

    def test_trying_to_delete_gradesystem_with_invalid_id_throws_exception(self):
        self.setup_gradesystem("Test")

        self.num_gradesystems(1)

        url = self.url + '/' + self.bad_gradesystem_id
        self.assertRaises(AppError, self.app.delete, url)

        self.num_gradesystems(1)

    def test_trying_to_delete_gradesystem_with_invalid_gradebook_id_throws_exception(self):
        grade_system = self.setup_gradesystem("Test")

        self.num_gradesystems(1)

        url = self.bad_gradebook_url + '/' + str(grade_system.ident)
        self.assertRaises(AppError, self.app.delete, url)

        self.num_gradesystems(1)

    def test_trying_to_delete_gradebook_with_gradesystems_id_throws_exception(self):
        self.setup_gradesystem("Test")

        self.num_gradesystems(1)

        self.assertRaises(AppError, self.app.delete, self.gradebook_url)

        self.num_gradesystems(1)


class GradebookColumnCRUDTests(BaseGradingTestCase):
    def num_columns(self, val):
        gm = get_managers()['gm']

        gradebook = gm.get_gradebook(self.gradebook.ident)
        self.assertEqual(
            gradebook.get_gradebook_columns().available(),
            val
        )

    def create_new_gradebook_column(self):
        return super(GradebookColumnCRUDTests, self).create_new_gradebook_column(self.gradebook, self.grade_system)

    def setUp(self):
        super(GradebookColumnCRUDTests, self).setUp()
        self.gradebook = create_new_gradebook()
        self.grade_system = self.setup_gradesystem(self.gradebook, "for testing only")
        self.bad_gradebook_id = 'grading.Gradebook%3A55203f0be7dde0815228bb41%40ODL.MIT.EDU'
        self.bad_grade_system_id = 'grading.GradebookSystem%3A55203f0be7dde0815228bb41%40ODL.MIT.EDU'
        self.bad_gradebook_column_id = 'grading.GradebookColumn%3A55203f0be7dde0815228bb41%40ODL.MIT.EDU'
        self.bad_gradebook_url = self.url + '/gradebooks/{0}/columns'.format(str(self.bad_gradebook_id))
        self.url += '/gradebooks/{0}/columns'.format(str(self.gradebook.ident))
        self.num_columns(0)

    def tearDown(self):
        super(GradebookColumnCRUDTests, self).tearDown()

    def test_can_list_gradebook_columns(self):
        req = self.app.get(self.url)
        self.ok(req)
        gradebook_column_list = self.json(req)
        self.assertEqual(len(gradebook_column_list), 0)

        gradebook_column = self.create_new_gradebook_column()
        self.num_columns(1)
        req = self.app.get(self.url)
        self.ok(req)
        gradebook_column_list = self.json(req)
        self.assertEqual(len(gradebook_column_list), 1)
        for attr, val in gradebook_column.object_map.iteritems():
            self.assertEqual(
                val,
                gradebook_column_list[0][attr]
            )

    def test_trying_to_get_gradecolumns_with_invalid_gradebook_id_throws_exception(self):
        self.assertRaises(AppError, self.app.get, self.bad_gradebook_url)

        self.num_columns(0)

    def test_trying_to_create_grade_column_with_invalid_gradebook_id_throws_exception(self):
        payload = {
            'name': 'my new grade column',
            'description': 'for testing with',
            'genusTypeId': 'gradecolumn-genus-type%3Adefault-gradecolumn%40ODL.MIT.EDU',

        }
        self.assertRaises(AppError,
                          self.app.post,
                          self.bad_gradebook_url,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

        self.num_columns(0)

    def test_trying_to_create_grade_column_without_grade_system_throws_exception(self):
        payload = {
            'name': 'my new grade column',
            'description': 'for testing with',
            'genusTypeId': 'gradecolumn-genus-type%3Adefault-gradecolumn%40ODL.MIT.EDU',

        }
        self.assertRaises(AppError,
                          self.app.post,
                          self.url,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

        self.num_columns(0)

    def test_trying_to_create_grade_column_with_bad_grade_system_throws_exception(self):
        payload = {
            'name': 'my new grade column',
            'description': 'for testing with',
            'genusTypeId': 'gradecolumn-genus-type%3Adefault-gradecolumn%40ODL.MIT.EDU',
            'gradeSystemId': self.bad_grade_system_id

        }
        self.assertRaises(AppError,
                          self.app.post,
                          self.url,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

        self.num_columns(0)

    def create_grade_column(self, payload):
        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        gradebook_column = self.json(req)
        self.num_columns(1)
        for key in ['gradeSystemId', 'genusTypeId']:
            self.assertEqual(
                gradebook_column[key],
                payload[key]
            )
        return gradebook_column

    def test_can_create_grade_column_name_as_string(self):
        payload = {
            'name': 'my new grade column',
            'description': 'for testing with',
            'genusTypeId': 'gradecolumn-genus-type%3Adefault-gradecolumn%40ODL.MIT.EDU',
            'gradeSystemId': str(self.grade_system.ident)
        }
        gradebook_column = self.create_grade_column(payload)
        self.assertEqual(
            gradebook_column['displayName']['text'],
            payload['name']
        )
        self.assertEqual(
            gradebook_column['description']['text'],
            payload['description']
        )

    def test_can_create_grade_column_name_as_dict(self):
        payload = {
            'displayName': self.display_text('my new grade column'),
            'description': self.display_text('for testing with'),
            'genusTypeId': 'gradecolumn-genus-type%3Adefault-gradecolumn%40ODL.MIT.EDU',
            'gradeSystemId': str(self.grade_system.ident)
        }
        gradebook_column = self.create_grade_column(payload)
        for key in ['displayName', 'description']:
            self.assertDisplayText(
                gradebook_column[key],
                payload[key]
            )

    def test_can_get_gradecolumns_details(self):
        gradebook_column = self.create_new_gradebook_column()

        self.num_columns(1)

        url = self.url + '/' + str(gradebook_column.ident)

        req = self.app.get(url)
        self.ok(req)
        gradebook_column_details = self.json(req)

        for attr, val in gradebook_column.object_map.iteritems():
            self.assertEqual(
                val,
                gradebook_column_details[attr]
            )

    def test_invalid_gradebook_column_id_throws_exception(self):
        self.create_new_gradebook_column()
        self.num_columns(1)

        url = self.url + '/x'
        self.assertRaises(AppError, self.app.get, url)

    def test_bad_gradebook_column_id_throws_exception(self):
        self.create_new_gradebook_column()
        self.num_columns(1)

        url = self.url + '/' + self.bad_gradebook_column_id
        self.assertRaises(AppError, self.app.get, url)

    def test_bad_gradebook_id_throws_exception(self):
        grade_book_column = self.create_new_gradebook_column()
        self.num_columns(1)

        url = self.bad_gradebook_url + '/' + str(grade_book_column.ident)
        self.assertRaises(AppError, self.app.get, url)

    def test_can_update_gradebook_columns(self):
        gradebook_column = self.create_new_gradebook_column()
        self.num_columns(1)

        url = self.url + '/' + str(gradebook_column.ident)

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
            updated_gradebook_column = self.json(req)

            if case[0] == 'name':
                self.assertEqual(
                    updated_gradebook_column['displayName']['text'],
                    case[1]
                )
            else:
                self.assertEqual(
                    updated_gradebook_column['description']['text'],
                    case[1]
                )

        self.num_columns(1)

    def test_can_update_gradebook_columns_with_dics(self):
        gradebook_column = self.create_new_gradebook_column()
        self.num_columns(1)

        url = self.url + '/' + str(gradebook_column.ident)

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
            updated_gradebook_column = self.json(req)

            if case[0] == 'displayName':
                self.assertDisplayText(
                    updated_gradebook_column['displayName'],
                    case[1]
                )
            else:
                self.assertDisplayText(
                    updated_gradebook_column['description'],
                    case[1]
                )

        self.num_columns(1)

    def test_update_with_invalid_id_throws_exception(self):
        self.create_new_gradebook_column()

        self.num_columns(1)

        url = self.url + '/' + self.bad_gradebook_column_id

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

        self.num_columns(1)

    def test_update_with_no_params_throws_exception(self):
        gradebook_column = self.create_new_gradebook_column()
        self.num_columns(1)

        url = self.url + '/' + str(gradebook_column.ident)

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

        self.num_columns(1)
        req = self.app.get(url)
        gradebook_column_fresh = self.json(req)

        gradebook_column_map = gradebook_column.object_map
        params_to_test = ['id', 'displayName', 'description']
        for param in params_to_test:
            self.assertEqual(
                gradebook_column_map[param],
                gradebook_column_fresh[param]
            )

    def test_can_delete_gradebook_column(self):
        gradebook_column = self.create_new_gradebook_column()
        self.num_columns(1)

        url = self.url + '/' + str(gradebook_column.ident)
        req = self.app.delete(url)
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        self.num_columns(0)

    def test_trying_to_delete_gradebook_column_with_invalid_id_throws_exception(self):
        self.create_new_gradebook_column()
        self.num_columns(1)

        url = self.url + '/' + self.bad_grade_system_id
        self.assertRaises(AppError, self.app.delete, url)

        self.num_columns(1)

    def test_trying_to_delete_gradebook_column_with_invalid_gradebook_id_throws_exception(self):
        gradebook_column = self.create_new_gradebook_column()
        self.num_columns(1)

        url = self.bad_gradebook_url + '/' + str(gradebook_column.ident)
        self.assertRaises(AppError, self.app.delete, url)

        self.num_columns(1)


class GradebookEntryCRUDTest(BaseGradingTestCase):
    def num_entries(self, column_id, val):
        gm = get_managers()['gm']

        gradebook = gm.get_gradebook(self.gradebook.ident)
        if column_id is None:
            grading_entries = gradebook.get_grade_entries()
        else:
            grading_entries = gradebook.get_grade_entries_for_gradebook_column(column_id)

        self.assertEqual(
            grading_entries.available(),
            val
        )

    def create_new_gradebook_entry(self, column):
        gm = get_managers()['gm']

        gradebook = gm.get_gradebook(self.gradebook.ident)

        form = gradebook.get_grade_entry_form_for_create(column.ident,
                                                         self.resource_id,
                                                         [])

        form.set_display_name("for testing only")

        entry = gradebook.create_grade_entry(form)

        return entry

    def create_new_grade(self):
        gm = get_managers()['gm']

        # add grades
        form = self.gradebook.get_grade_form_for_create(self.graded_based_grade_system.ident, [])
        form.inputScoreStartRange = 0.0
        form.inputScoreEndRange = 100.0
        form.outputScore = 50.0

        grade = self.gradebook.create_grade(form)
        return grade

    def create_new_graded_based_gradesystem(self):
        gm = get_managers()['gm']

        gradebook = gm.get_gradebook(self.gradebook.ident)

        form = gradebook.get_grade_system_form_for_create([])
        form.set_display_name("For testing")
        form.based_on_grades = True

        new_grade_system = gradebook.create_grade_system(form)

        return new_grade_system

    def setUp(self):
        super(GradebookEntryCRUDTest, self).setUp()
        self.gradebook = create_new_gradebook()
        self.grade_system = self.setup_gradesystem(self.gradebook, "Test")
        self.gradebook_column = self.create_new_gradebook_column(self.gradebook, self.grade_system)
        self.resource_id = Id('user:xaracil@UOC.EDU')

        self.graded_based_grade_system = self.create_new_graded_based_gradesystem()
        self.grade = self.create_new_grade()
        self.graded_based_gradebook_column = self.create_new_gradebook_column(self.gradebook,
                                                                              self.graded_based_grade_system)

        self.bad_gradebook_id = 'grading.Gradebook%3A55203f0be7dde0815228bb41%40ODL.MIT.EDU'
        self.bad_grade_system_id = 'grading.GradebookSystem%3A55203f0be7dde0815228bb41%40ODL.MIT.EDU'
        self.bad_gradebook_column_id = 'grading.GradebookColumn%3A55203f0be7dde0815228bb41%40ODL.MIT.EDU'
        self.bad_gradebook_url = self.url + '/gradebooks/{0}/entries'.format(str(self.bad_gradebook_id))
        self.bad_gradebook_and_gradebook_column_url = self.url + '/gradebooks/{0}/columns/{1}/entries'.format(str(self.bad_gradebook_id), str(self.bad_gradebook_column_id))
        self.bad_gradebook_column_url = self.url + '/gradebooks/{0}/columns/{1}/entries'.format(str(self.gradebook.ident), str(self.bad_gradebook_column_id))

        self.column_url = self.url + '/gradebooks/{0}/columns/{1}/entries'.format(str(self.gradebook.ident), str(self.gradebook_column.ident))
        self.graded_based_column_url = self.url + '/gradebooks/{0}/columns/{1}/entries'.format(str(self.gradebook.ident), str(self.graded_based_gradebook_column.ident))

        self.url += '/gradebooks/{0}/entries'.format(str(self.gradebook.ident))
        self.num_entries(None, 0)

    def tearDown(self):
        super(GradebookEntryCRUDTest, self).tearDown()

    def get_entries_and_assert(self, url):
        req = self.app.get(url)
        self.ok(req)
        entries_list = self.json(req)
        self.assertEqual(len(entries_list), 0)

        gradebook_entry = self.create_new_gradebook_entry(self.gradebook_column)
        self.num_entries(None, 1)
        self.num_entries(self.gradebook_column.ident, 1)
        req = self.app.get(url)
        self.ok(req)
        entries_list = self.json(req)
        self.assertEqual(len(entries_list), 1)
        for attr, val in gradebook_entry.object_map.iteritems():
            if attr == 'startDate' or attr == 'endDate':
                self.assertEqual(
                    val.isoformat(),
                    entries_list[0][attr]
                )
            else:
                self.assertEqual(
                    val,
                    entries_list[0][attr]
                )

    def test_can_list_grade_entries(self):
        self.get_entries_and_assert(self.url)

    def test_can_list_grade_entries_with_column_in_request(self):
        self.get_entries_and_assert(self.column_url)

    def test_trying_to_get_entries_with_invalid_gradebook_id_throws_exception(self):
        self.assertRaises(AppError, self.app.get, self.bad_gradebook_url)

        self.num_entries(None, 0)

    def test_trying_to_get_entries_with_invalid_gradebookcolumn(self):
        req = self.app.get(self.bad_gradebook_column_url)
        self.ok(req)
        entries_list = self.json(req)
        self.assertEqual(len(entries_list), 0)
        self.num_entries(None, 0)

    def create_invalid_entry_and_assert_exception(self, url, payload):
        self.assertRaises(AppError,
                          self.app.post,
                          url,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})
        self.num_entries(None, 0)

    def test_trying_to_create_grade_entry_with_invalid_gradebook_id_throws_exception(self):
        payload = {
            'name': 'my new grade entry',
            'description': 'for testing with',
            'ignoredForCalculations': True,
            'score': 25.0,
            'resourceId': str(self.resource_id)
        }
        self.create_invalid_entry_and_assert_exception(self.bad_gradebook_url, payload)

        payload['columnId'] = str(self.gradebook_column.ident)
        self.create_invalid_entry_and_assert_exception(self.bad_gradebook_and_gradebook_column_url, payload)

    def test_trying_to_create_grade_entry_without_resource_throws_exception(self):
        payload = {
            'name': 'my new grade entry',
            'description': 'for testing with',
            'ignoredForCalculations': True,
            'score': 25.0,

        }
        self.create_invalid_entry_and_assert_exception(self.column_url, payload)

        payload['columnId'] = str(self.gradebook_column.ident)
        self.create_invalid_entry_and_assert_exception(self.url, payload)

    def test_trying_to_create_grade_column_with_bad_column_throws_exception(self):
        payload = {
            'name': 'my new grade entry',
            'description': 'for testing with',
            'ignoredForCalculations': True,
            'score': 25.0,
            'resourceId': str(self.resource_id)
        }

        self.create_invalid_entry_and_assert_exception(self.bad_gradebook_column_url, payload)

        payload['columnId'] = str(self.bad_gradebook_id)
        self.create_invalid_entry_and_assert_exception(self.url, payload)
        self.num_entries(self.gradebook_column.ident, 0)

    def create_grade_entry(self, url, payload, expected):
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        entry = self.json(req)
        self.assertIsNotNone(entry['id'])
        # for key in ['gradeSystemId', 'genusTypeId']:
        #    self.assertEqual(
        #        entry[key],
        #        payload[key]
        #    )
        self.num_entries(None, expected)
        return entry

    def create_grade_entry_string(self, url, payload, expected):
        entry = self.create_grade_entry(url, payload, expected)
        self.assertEqual(
            entry['displayName']['text'],
            payload['name']
        )
        self.assertEqual(
            entry['description']['text'],
            payload['description']
        )
        return entry

    def create_grade_entry_display_text(self, url, payload, expected):
        entry = self.create_grade_entry(url, payload, expected)
        for key in ['displayName', 'description']:
            self.assertDisplayText(
                entry[key],
                payload[key]
            )
        return entry

    def test_can_create_entry_name_as_string(self):
        payload = {
            'name': 'my new grade entry',
            'description': 'for testing with',
            'ignoredForCalculations': True,
            'resourceId': str(self.resource_id)
        }
        self.create_grade_entry_string(self.column_url, payload, 1)
        self.num_entries(self.gradebook_column.ident, 1)

        payload['columnId'] = str(self.gradebook_column.ident)
        self.create_grade_entry_string(self.column_url, payload, 2)
        self.num_entries(self.gradebook_column.ident, 2)

    def test_can_create_entry_name_as_dict(self):
        payload = {
            'displayName': self.display_text('my new grade entry'),
            'description': self.display_text('for testing with'),
            'ignoredForCalculations': True,
            'resourceId': str(self.resource_id)
        }
        self.create_grade_entry_display_text(self.column_url, payload, 1)
        self.num_entries(self.gradebook_column.ident, 1)

        payload['columnId'] = str(self.gradebook_column.ident)
        self.create_grade_entry_display_text(self.column_url, payload, 2)
        self.num_entries(self.gradebook_column.ident, 2)

    def test_can_create_graded_based_entry_name_as_string(self):
        payload = {
            'name': 'my new grade entry',
            'description': 'for testing with',
            'grade': str(self.grade.ident),
            'resourceId': str(self.resource_id)
        }
        self.create_grade_entry_string(self.graded_based_column_url, payload, 1)
        self.num_entries(self.graded_based_gradebook_column.ident, 1)
        self.num_entries(self.gradebook_column.ident, 0)

        payload['columnId'] = str(self.graded_based_gradebook_column.ident)
        self.create_grade_entry_string(self.graded_based_column_url, payload, 2)
        self.num_entries(self.graded_based_gradebook_column.ident, 2)
        self.num_entries(self.gradebook_column.ident, 0)

    def test_can_create_graded_entry_name_as_dict(self):
        payload = {
            'displayName': self.display_text('my new grade entry'),
            'description': self.display_text('for testing with'),
            'grade': str(self.grade.ident),
            'resourceId': str(self.resource_id)
        }
        self.create_grade_entry_display_text(self.graded_based_column_url, payload, 1)
        self.num_entries(self.graded_based_gradebook_column.ident, 1)
        self.num_entries(self.gradebook_column.ident, 0)

        payload['columnId'] = str(self.graded_based_gradebook_column.ident)
        self.create_grade_entry_display_text(self.graded_based_column_url, payload, 2)
        self.num_entries(self.graded_based_gradebook_column.ident, 2)
        self.num_entries(self.gradebook_column.ident, 0)
