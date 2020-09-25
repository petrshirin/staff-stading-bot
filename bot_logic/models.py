from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver
import string
import random


# Create your models here.
class NonStrippingTextField(models.TextField):
    """A TextField that does not strip whitespace at the beginning/end of
    it's value.  Might be important for markup/code."""

    def formfield(self, **kwargs):
        kwargs['strip'] = False
        return super(NonStrippingTextField, self).formfield(**kwargs)


def create_user_file_path(instance, filename):
    """
    create path for user avatars
    :param instance:
    :param filename:
    :return:
    """
    return f'avatars/user_{instance.pk}/{filename}'


class TelegramBot(models.Model):
    """
    Telegram bot for working other restaurants
    """
    name = models.CharField(max_length=255)
    token = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.pk} {self.name}"


class Restaurant(models.Model):
    """
    Restaurant chain, main essence
    """
    name = models.CharField(max_length=255)
    bot = models.OneToOneField(TelegramBot, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.pk}. {self.name} {self.bot.name}"


class City(models.Model):
    name = models.CharField(max_length=255, default="Иркутск")


class RestaurantBranch(models.Model):
    """
    Branch of Restaurant chain
    """
    main_restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=500)


class Staff(models.Model):
    """
    User who can create course for workers and check results
    """
    restaurant_branch = models.ForeignKey(RestaurantBranch, on_delete=models.SET_NULL, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    second_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.pk} {self.first_name} {self.second_name} "


class Student(models.Model):
    """
    Simple worker in restaurant, work with Telegram
    """
    user_id = models.IntegerField(default=None, null=True, blank=True)
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)
    telegram_bot = models.ForeignKey(TelegramBot, on_delete=models.CASCADE)
    step = models.IntegerField(default=0)
    current_test = models.IntegerField(null=True, blank=True, default=None)
    current_open_question = models.IntegerField(null=True, blank=True, default=None)


class StudentSettings(models.Model):
    """
    Student settings for change business logic
    """
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    token = models.CharField(max_length=16, default=None, null=True)
    language = models.CharField(max_length=4, default='ru')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.token:
            self.create_token()
        super(StudentSettings, self).save()

    def create_token(self):
        letters = string.ascii_lowercase
        self.token = ''.join(random.choice(letters) for i in range(32))


class StudentInfo(models.Model):
    """
    Student Info for staff interface
    """
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    position = models.CharField(max_length=255, default=None, null=True)
    first_name = models.CharField(max_length=255)
    second_name = models.CharField(max_length=255)
    third_name = models.CharField(max_length=255)
    date_start = models.DateField(default=now)
    date_birth = models.DateField(default=None, null=True, blank=True)
    education = models.CharField(max_length=255, default='Среднее')
    phone = models.CharField(max_length=20, default=None, blank=True, null=True)
    email = models.EmailField(default=None, null=True)
    profile_photo = models.ImageField(upload_to=create_user_file_path, null=True, blank=True, default=None)


class TelegramMessage(models.Model):
    """
    Message to change in some bot
    use message tag (see in lang.py) and add custom message
    """
    tag = models.CharField(max_length=255)
    text = NonStrippingTextField()
    bot = models.ForeignKey(TelegramBot, on_delete=models.CASCADE, default=None, null=True)


class TestAnswer(models.Model):
    """
    Variant answers for test
    """
    answer = models.CharField(max_length=30)
    is_right = models.BooleanField(default=False)


class TestQuestion(models.Model):
    """
    Question for some test
    """
    question = NonStrippingTextField()
    is_opened = models.BooleanField(default=False)
    answers = models.ManyToManyField(TestAnswer, blank=True)


class TheoryTest(models.Model):
    """
    Test, created staff
    """
    name = models.CharField(max_length=255)
    questions = models.ManyToManyField(TestQuestion)


class TheoryBlock(models.Model):
    """
    Block with info for worker studding
    """
    name = models.CharField(max_length=255)
    text = NonStrippingTextField()


class TheoryTopic(models.Model):
    """
    Big block in particular theme
    """
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    creator = models.ForeignKey(Staff, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    text = NonStrippingTextField()
    test = models.OneToOneField(TheoryTest, on_delete=models.SET_NULL, null=True)
    blocks = models.ManyToManyField(TheoryBlock)


class StudentTheoryTopic(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    theory_topic = models.ForeignKey(TheoryTopic, on_delete=models.CASCADE)
    complete_theory = models.BooleanField(default=None, null=True)
    complete_test = models.BooleanField(default=None, null=True)
    complete_opened_questions = models.BooleanField(default=None, null=True)
    finished = models.BooleanField(default=False)
    blocked = models.BooleanField(default=True)


class StudentAnswer(models.Model):
    """
    Student answer for check
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE)
    answer = models.ForeignKey(TestAnswer, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField(null=True, blank=True)


class StudentTest(models.Model):
    """
    opened test for student
    """
    test = models.ForeignKey(TheoryTest, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    answers = models.ManyToManyField(StudentAnswer)
    is_finished = models.BooleanField(default=False)
    is_check_staff = models.BooleanField(default=False)
    points = models.PositiveSmallIntegerField(default=0, null=True, blank=True)
    max_points = models.PositiveSmallIntegerField(default=0, null=True, blank=True)
    opened_questions = models.PositiveSmallIntegerField(default=0, null=True, blank=True)
    max_opened_questions = models.PositiveSmallIntegerField(default=0, null=True, blank=True)


@receiver(post_save, sender=TheoryTopic)
def create_student_topic(sender, instance, created, **kwargs):
    if created:
        staffs = Staff.objects.filter(restaurant_branch=instance.restaurant).all()
        for staff in staffs:
            students = Student.objects.filter(staff=staff).all()
            for student in students:
                StudentTheoryTopic.objects.create(student=student, theory_topic=instance)


@receiver(post_save, sender=Student)
def create_student_additional_tables(sender: Student, instance: Student, created: bool, **kwargs):
    if created:
        StudentInfo.objects.create(student=instance)
        student_settings = StudentSettings.objects.create(student=instance)
        student_settings.create_token()
        student_settings.save()
        # topics = TheoryTopic.objects.filter(restaurant__staff=instance.staff).all()
        # for topic in topics:
        #    StudentTheoryTopic.objects.create(student=instance, theory_topic=topic)


@receiver(post_save, sender=Student)
def save_student_additional_tables(sender: Student, instance: Student, **kwargs):
    instance.studentinfo.save()
    instance.studentsettings.save()


