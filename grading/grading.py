import json
import web
import utilities

import grading_utilities as gutils

urls = (
#    "/gradebooks/(.*)/colums/(.*)/entries/?", "GradeEntriesList",
#    "/gradebooks/(.*)/colums/(.*)/summary/?", "GradebookColumnSummary",
#    "/gradebooks/(.*)/colums/(.*)/?", "GradebookColumnDetails",
#    "/gradebooks/(.*)/entries/(.*)/?", "GradeEntryDetails",
#    "/gradebooks/(.*)/colums/?", "GradebookColumnsList",
#    "/gradebooks/(.*)/entries/?", "GradeEntriesList",
    "/gradebooks/(.*)/gradesystems/(.*)/?", "GradebookGradeSystemDetails",
    "/gradebooks/(.*)/gradesystems/?", "GradebookGradeSystemList",
    "/gradebooks/(.*)/?", "GradebookDetails",
    "/gradebooks/?", "GradebookList"
)


class GradebookList(utilities.BaseClass):
    """
    List all available gradebooks.
    api/v1/grading/gradebooks/

    POST allows you to create a new gradebook, requires two parameters:
      * name
      * description

    Alternatively, if you provide an assessment bank ID,
    the gradebook will be orchestrated to have a matching internal identifier.
    The name and description will be set for you, but can optionally be set if
    provided.
      * bankId
      * name (optional)
      * description (optional)

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
      {"name" : "a new gradebook",
       "description" : "this is a test"}

       OR
       {"bankId": "assessment.Bank%3A5547c37cea061a6d3f0ffe71%40cs-macbook-pro"}
    """
    @utilities.format_response
    def GET(self):
        """
        List all available gradebooks
        """
        try:
            gm = gutils.get_grading_manager()
            gradebooks = utilities.extract_items(gm.gradebooks)
            return gradebooks
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self):
        """
        Create a new gradebook, if authorized

        """
        try:
            gm = gutils.get_grading_manager()
            form = gm.get_gradebook_form_for_create([])
            data = self.data()

            form = utilities.set_form_basics(form, data)

            new_gradebook = utilities.convert_dl_object(gm.create_gradebook(form))

            if 'aliasId' in data:
                gm.alias_bank(utilities.clean_id(json.loads(new_gradebook)['id']),
                              utilities.clean_id(data['aliasId']))

            return new_gradebook
        except Exception as ex:
            utilities.handle_exceptions(ex)


class GradebookDetails(utilities.BaseClass):
    """
    Shows details for a specific gradebook.
    api/v1/grading/gradebooks/<gradebook_id>/

    GET, PUT, DELETE
    PUT will update the gradebook. Only changed attributes need to be sent.
    DELETE will remove the gradebook.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       PUT {"name" : "a new gradebook"}
    """
    @utilities.format_response
    def GET(self, gradebook_id):
        try:
            gm = gutils.get_grading_manager()
            grading_gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))
            gradebook = utilities.convert_dl_object(grading_gradebook)
            return gradebook
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def PUT(self, gradebook_id):
        try:
            gm = gutils.get_grading_manager()
            data = self.data()

            form = gm.get_gradebook_form_for_update(utilities.clean_id(gradebook_id))

            form = utilities.set_form_basics(form, data)
            updated_gradebook = gm.update_gradebook(form)

            if 'aliasId' in data:
                gm.alias_bank(updated_gradebook.ident, utilities.clean_id(data['aliasId']))

            gradebook = utilities.convert_dl_object(updated_gradebook)
            return gradebook
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def DELETE(self, gradebook_id):
        try:
            gm = gutils.get_grading_manager()
            data = gm.delete_gradebook(utilities.clean_id(gradebook_id))
            return utilities.success()
        except Exception as ex:
            utilities.handle_exceptions(ex)


class GradebookGradeSystemList(utilities.BaseClass):
    """
    Get or add gradesystems to a gradebook
    api/v1/grading/gradebooks/<gradebook_id>/gradesystems/

    GET, POST
    GET to view current gradesystems.
    POST to create a new gradesystem

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"name" : "Letters", "description": "Letter grades A - F"}
    """
    @utilities.format_response
    def GET(self, gradebook_id):
        try:
            gm = gutils.get_grading_manager()
            gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))

            grading_grade_systems = gradebook.get_grade_systems()
            grade_systems = utilities.extract_items(grading_grade_systems)
            return grade_systems
        except Exception as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self, gradebook_id):
        try:
            gm = gutils.get_grading_manager()
            gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))

            form = gradebook.get_grade_system_form_for_create([])
            data = self.data()

            form = utilities.set_form_basics(form, data)

            check_scores = True

            if 'basedOnGrades' in data:
                form.set_based_on_grades(bool(data['basedOnGrades']))
                if data['basedOnGrades']:
                    check_scores = False

            if check_scores:
                gutils.check_numeric_score_inputs(data)

                form.set_highest_numeric_score(float(data['highestScore']))
                form.set_lowest_numeric_score(float(data['lowestScore']))
                form.set_numeric_score_increment(float(data['scoreIncrement']))

            grade_system = gradebook.create_grade_system(form)

            if not check_scores:
                gutils.check_grade_inputs(data)
                gutils.add_grades_to_grade_system(gradebook,
                                                   grade_system,
                                                   data)

            new_grade_system = utilities.convert_dl_object(gradebook.get_grade_system(grade_system.ident))

            return new_grade_system
        except Exception as ex:
            try:
                gradebook.delete_grade_system(grade_system.ident)
            except NameError:
                pass
            utilities.handle_exceptions(ex)


class GradebookGradeSystemDetails(utilities.BaseClass):
    """
    Get grade system details
    api/v1/grading/gradebooks/<gradebook_id>/gradesystems/<gradesystem_id>/

    GET, PUT, DELETE
    PUT to modify an existing grade system (name or settings). Include only the changed parameters.
    DELETE to remove the grade system.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"name" : "an updated item"}
    """
    @utilities.format_response
    def GET(self, gradebook_id, gradesystem_id):
        try:
            gm = gutils.get_grading_manager()
            gradebook = gm.get_gradebook(utilities.clean_id(gradebook_id))
            grading_grade_systems = gradebook.get_grade_system(utilities.clean_id(gradesystem_id))
            grade_system = utilities.convert_dl_object(grading_grade_systems)
            return grade_system
        except Exception as ex:
            utilities.handle_exceptions(ex)


app_grading = web.application(urls, locals())
