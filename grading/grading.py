import json
import web
import utilities

import grading_utilities as gutils

urls = (
#    "/gradebooks/(.*)/gradesystems/(.*)/?", "GradebookGradeSystemDetails",
#    "/gradebooks/(.*)/gradesystems/?", "GradebookGradeSystemList",
#    "/gradebooks/(.*)/colums/(.*)/entries/?", "GradeEntriesList",
#    "/gradebooks/(.*)/colums/(.*)/summary/?", "GradebookColumnSummary",
#    "/gradebooks/(.*)/colums/(.*)/?", "GradebookColumnDetails",
#    "/gradebooks/(.*)/entries/(.*)/?", "GradeEntryDetails",
#    "/gradebooks/(.*)/colums/?", "GradebookColumnsList",
#    "/gradebooks/(.*)/entries/?", "GradeEntriesList",
#    "/gradebooks/(.*)/?", "GradebookDetails",
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


app_grading = web.application(urls, locals())
