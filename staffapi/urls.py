from django.contrib import admin
from django.urls import path
from .views import CityView, RestaurantBranchView, \
    StudentView, ListStudentsWithActionsView, StudentAnswersView, TopicListView

urlpatterns = [
    path('cities/', CityView.as_view(), name="cities"),
    path('branches/', RestaurantBranchView.as_view(), name="branches"),
    path('student/', StudentView.as_view(), name="students"),
    path('student/<int:pk>', StudentView.as_view(), name="student"),
    path('liststudents/<int:pk>', ListStudentsWithActionsView.as_view(), name="list_students"),
    path('answers/', StudentAnswersView.as_view(), name="all_student_answers"),
    path('answers/<int:pk>', StudentAnswersView.as_view(), name="answers"),
    path('topic/list/', TopicListView.as_view(), name="topics"),

]
