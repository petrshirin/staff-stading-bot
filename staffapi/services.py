from rest_framework.views import Response
from django.http import HttpRequest
from .serializers import CitySerializer, RestaurantBranchSerializer, \
    StudentSerializer, MinimalStudentSerializer, \
    AnswerSerializer, OpenedQuestionSerializer, \
    AnswerPostSerializer, StudentPostSerializer, \
    TheoryTopicListSerializer
from .models import *
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict
from typing import Optional, List, Dict, Any, Union
from rest_framework.request import Request


def get_all_cities() -> ReturnList:
    """
    Get all cities and create
    :return:
    """
    cities = City.objects.all()
    cities_serializer = CitySerializer(cities, many=True)
    return cities_serializer.data


def get_all_restaurant_branches_in_city(city: City) -> ReturnList:
    """
    This function get all restaurant branches in city
    :param city:
    :return:
    """
    branches = RestaurantBranch.objects.filter(city=city).all()
    branches_serializer = RestaurantBranchSerializer(branches, many=True)
    return branches_serializer.data


def validate_city_to_pk(pk: int) -> Optional[City]:
    """
    This function validate city to exist in Data Base
    :param pk:
    :return:
    """
    try:
        city = City.objects.get(pk=pk)
        return city
    except City.DoesNotExist:
        return None


def validate_restaurant_branch_to_pk(pk: int) -> Optional[RestaurantBranch]:
    """
    This function validate restaurant branch to exist in Data Base
    :param pk:
    :return:
    """
    try:
        restaurant_branch = RestaurantBranch.objects.get(pk=pk)
        return restaurant_branch
    except RestaurantBranch.DoesNotExist:
        return None


def validate_student_to_pk(pk: int) -> Optional[Student]:
    """
    This function validate student to exist in Data Base
    :param pk:
    :return:
    """
    try:
        student = Student.objects.get(pk=pk)
        return student
    except Student.DoesNotExist:
        return None


def get_minimal_info_about_students(restaurant_branch: RestaurantBranch) -> List:
    """
    This function generate list of students and not view actions
    :param restaurant_branch:
    :return:
    """
    students = Student.objects.filter(staff__restaurant_branch=restaurant_branch).all()
    results = []
    for student in students:
        students_serializer = MinimalStudentSerializer(data={"id": student.pk,
                                                             "first_name": student.studentinfo.first_name,
                                                             "second_name": student.studentinfo.second_name,
                                                             "third_name": student.studentinfo.third_name,
                                                             "actions": _calculate_student_not_process_actions(student)})
        if students_serializer.is_valid():
            results.append(students_serializer.data)
    return results


def _calculate_student_not_process_actions(student: Student):
    """
    This function calculate last student actions which need check Staff
    :param student:
    :return:
    """
    return StudentTest.objects.filter(student=student, is_finished=True, is_check_staff=False).count()


def get_full_student_info(staff: Staff, restaurant: RestaurantBranch = None, pk: int = None, many: bool = False) -> Optional[List]:
    """
    This function get one ore all instanses of students
    :param staff:
    :param restaurant:
    :param pk: if not many
    :param many: if True return all
    :return:
    """
    if many:
        if restaurant:
            students = Student.objects.filter(staff__restaurant_branch=restaurant).all()
        else:
            students = Student.objects.filter(staff=staff).all()

        results = []
        for student in students:
            photo = student.studentinfo.profile_photo.url if student.studentinfo.profile_photo else None
            students_serializer = StudentSerializer(data={"id": student.pk,
                                                          "token": student.studentsettings.token,
                                                          "position": student.studentinfo.position,
                                                          "first_name": student.studentinfo.first_name,
                                                          "second_name": student.studentinfo.second_name,
                                                          "third_name": student.studentinfo.third_name,
                                                          "date_work_start": student.studentinfo.date_start,
                                                          "date_birth": student.studentinfo.date_birth,
                                                          "phone": student.studentinfo.phone,
                                                          "email": student.studentinfo.email,
                                                          "profile_photo": photo})
            if students_serializer.is_valid():
                results.append(students_serializer.data)
        return results
    else:
        try:
            student = Student.objects.get(pk=pk)
            photo = student.studentinfo.profile_photo.url if student.studentinfo.profile_photo else None
            students_serializer = StudentSerializer(data={"id": student.pk,
                                                          "token": student.studentsettings.token,
                                                          "position": student.studentinfo.position,
                                                          "first_name": student.studentinfo.first_name,
                                                          "second_name": student.studentinfo.second_name,
                                                          "third_name": student.studentinfo.third_name,
                                                          "date_work_start": student.studentinfo.date_start,
                                                          "date_birth": student.studentinfo.date_birth,
                                                          "phone": student.studentinfo.phone,
                                                          "email": student.studentinfo.email,
                                                          "profile_photo": photo})
            if students_serializer.is_valid():
                return students_serializer.data
        except Student.DoesNotExist:
            return None


def get_all_students_answers(restaurant_branch: RestaurantBranch) -> Optional[List]:
    """
    Get info about all students answers in restaurant branch
    :param restaurant_branch:
    :return:
    """
    students = Student.objects.filter(staff__restaurant_branch=restaurant_branch).all()
    results = []
    for student in students:
        results.append(get_current_student_answers(student))
    return results


def get_current_student_answers(student: Student) -> Optional[Dict[str, Union[list, Any]]]:
    """
    Get info about one student answers
    :param student:
    :return:
    """
    student_topics = StudentTheoryTopic.objects.filter(student=student).all()

    results = {"student_id": student.pk,
               'topics': []}

    for student_topic in student_topics:
        opened_questions = []
        if student_topic.complete_test:
            student_tests = StudentTest.objects.filter(student=student, test__theorytopic=student_topic.theory_topic, is_finished=True).all()
            if student_tests:

                student_tests = list(student_tests)
                student_test = student_tests[-1]
                for answer in student_test.answers.all():
                    if answer.question.is_opened:
                        print(answer.question.question)
                        print(answer.text)
                        opened_question = OpenedQuestionSerializer(data={"id": answer.pk,
                                                                         "question": answer.question.question,
                                                                         "answer": answer.text})
                        if opened_question.is_valid():
                            opened_questions.append(opened_question.data)

        answer_in_topic = AnswerSerializer(data={"id": student_topic.pk,
                                                 "name": student_topic.theory_topic.name,
                                                 "complete_theory": student_topic.complete_theory,
                                                 "complete_test": student_topic.complete_test,
                                                 "complete_opened_questions": student_topic.complete_opened_questions,
                                                 "opened_questions": opened_questions})
        if answer_in_topic.is_valid():
            results['topics'].append(answer_in_topic.data)
    return results


def change_answer_status(request: Request, pk: int):
    try:
        answer = StudentTheoryTopic.objects.get(pk=pk)
    except StudentTheoryTopic.DoesNotExist:
        return {"success": False, "error": "Answer not found"}
    post_ser = AnswerPostSerializer(answer, data={
        "complete_opened_questions": request.data.get('complete_opened_questions')
    })
    if post_ser.is_valid():
        post_ser.save()
        return {"success": True, "data": "ok"}
    else:
        return {"success": False, "error": post_ser.errors}


def register_new_student(request: Request) -> Dict:
    data = request.data
    course = request.data['course']
    try:
        topic = TheoryTopic.objects.get(pk=course)
    except TheoryTopic.DoesNotExist:
        return {"errors": "course does not exist", 'success': False}

    if StudentInfo.objects.filter(first_name=data['first_name'], second_name=data['second_name'], third_name=data['third_name'], student__staff=request.user.staff):
        return {"errors": "Student already exist", 'success': False}

    student_ser = StudentPostSerializer(data=data)
    if student_ser.is_valid():

        student = Student.objects.create(staff=request.user.staff, telegram_bot=request.user.staff.restaurant_branch.main_restaurant.bot)
        student_ser.update(student.studentinfo, student_ser.validated_data)

        created = add_course_to_user(topic, student)

        user_data = {"id": student.pk,
                     "token": student.studentsettings.token,
                     "position": student.studentinfo.position,
                     "first_name": student.studentinfo.first_name,
                     "second_name": student.studentinfo.second_name,
                     "third_name": student.studentinfo.third_name,
                     "date_work_start": student.studentinfo.date_start,
                     "date_birth": student.studentinfo.date_birth,
                     "education": student.studentinfo.education,
                     "phone": student.studentinfo.phone,
                     "email": student.studentinfo.email}

        if not created:
            user_data['course'] = None
        else:
            user_data['course'] = topic.pk

        students_serializer_return = StudentSerializer(data=user_data)

        if students_serializer_return.is_valid():
            return {'data': students_serializer_return.validated_data, 'success': True}
        print(students_serializer_return.errors)
        return {'data': student_ser.validated_data, 'success': True, 'access_token': student.studentsettings.token}
    else:
        return {'errors': student_ser.errors, 'success': False}


def update_student_info(request: Request, pk: int) -> Dict:
    try:
        student = Student.objects.get(pk=pk)
    except Student.DoesNotExist:
        return {'errors': 'user do not exists', 'success': True}

    student_ser = StudentPostSerializer(student.studentinfo, data=request.data)
    if student_ser.is_valid():
        print(student_ser.validated_data)
        student_ser.update(student.studentinfo, student_ser.validated_data)

        students_serializer_return = StudentSerializer(data={"id": student.pk,
                                                             "token": student.studentsettings.token,
                                                             "position": student.studentinfo.position,
                                                             "first_name": student.studentinfo.first_name,
                                                             "second_name": student.studentinfo.second_name,
                                                             "third_name": student.studentinfo.third_name,
                                                             "date_work_start": student.studentinfo.date_start,
                                                             "date_birth": student.studentinfo.date_birth,
                                                             "education": student.studentinfo.education,
                                                             "phone": student.studentinfo.phone,
                                                             "email": student.studentinfo.email,
                                                             })

        if students_serializer_return.is_valid():
            return {'data': students_serializer_return.validated_data, 'success': True}

        return {'data': students_serializer_return.validated_data, 'success': True}
    else:
        return {'errors': student_ser.errors, 'success': False}


def add_course_to_user(topic: TheoryTopic, student: Student) -> bool:
    if StudentTheoryTopic.objects.filter(theory_topic=topic, student=student):
        return False
    student_topic = StudentTheoryTopic(theory_topic=topic, student=student, blocked=False)
    student_topic.save()
    return True


def get_all_course(request: Request) -> Dict:
    topics = TheoryTopic.objects.filter(restaurant=request.user.staff.restaurant_branch.main_restaurant).all()
    topics_ser = TheoryTopicListSerializer(topics, many=True)
    return {"data": topics_ser.data, 'success': True}
