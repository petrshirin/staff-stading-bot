from django.shortcuts import render
from rest_framework.views import APIView, Response
from .services import \
    get_all_cities, \
    get_all_restaurant_branches_in_city, \
    validate_city_to_pk, \
    validate_restaurant_branch_to_pk, \
    get_minimal_info_about_students, \
    get_full_student_info, get_current_student_answers, \
    validate_student_to_pk, get_all_students_answers, \
    change_answer_status
from rest_framework.request import Request


# Create your views here.
class CityView(APIView):
    """
    View class to add and view City List
    """

    def get(self, request: Request) -> Response:
        """
        This method return full city list
        :param request:
        :return: Response({"data": CitySerializer, "success": True}, status=200)
        """
        return Response({"data": get_all_cities(), "success": True}, status=200)


class RestaurantBranchView(APIView):
    """
    View class to add and view restaurant branch list
    """

    def get(self, request: Request) -> Response:
        """
        This method return all restaurant branches current staff
        :param request:
        :return: Response({"data": RestaurantBranchSerializer, "success": True}, status=200)
        """
        city = validate_city_to_pk(request.query_params.get('city'))
        if city:
            return Response({"data": get_all_restaurant_branches_in_city(city), "success": True}, status=200)
        else:
            return Response({"success": False, "error": "invalid param `city`"}, status=422)


class ListStudentsWithActionsView(APIView):
    """
    View class to get list of students current restaurant branch
    """

    def get(self, request: Request, pk: int) -> Response:
        """
        This method return all list of student current pk
        :param pk: restaurant branch pk
        :param request:
        :return: Response({"data": [StudentSerializer], "success": True}, status=200)
        """
        restaurant_branch = validate_restaurant_branch_to_pk(pk)
        results = get_minimal_info_about_students(restaurant_branch)
        return Response({"data": results, "success": True}, status=200)


class StudentView(APIView):
    """
    Full info about students
    """
    def get(self, request: Request, pk=None) -> Response:
        """
        Get one instance of pk != None or all instances of Students with full info
        :param request:
        :param pk:
        :return:
        """
        if pk:
            data = get_full_student_info(request.user.staff, request.query_params.get('restaurant_branch'), pk=pk)
        else:
            data = get_full_student_info(request.user.staff, request.query_params.get('restaurant_branch'), many=True)
        return Response({"data": data, "success": True}, status=200)


class StudentAnswersView(APIView):
    """
    info about student answers and check opened answers
    """

    def get(self, request, pk=None) -> Response:
        """
        Get one instance of pk != None or all instances of StudentsAnswers and opened
        :param request:
        :param pk:
        :return:
        """
        if pk:
            student = validate_student_to_pk(pk)
            if student:
                data = get_current_student_answers(student)
                return Response({"data": data, 'success': True}, status=200)
            else:
                return Response({'success': False, "error": "student not found"}, status=422)
        else:
            rest_branch = validate_restaurant_branch_to_pk(request.query_params.get('restaurant_branch'))
            if rest_branch:
                data = get_all_students_answers(rest_branch)
                return Response({"data": data, 'success': True}, status=200)

    def post(self, request: Request) -> Response:
        """
        Change Status in student topic
        :param request:
        :return:
        """
        data = change_answer_status(request)
        if data.get('success'):
            return Response(data, status=200)
        else:
            return Response(data, status=422)

