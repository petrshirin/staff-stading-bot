from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


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


class RestaurantBranch(models.Model):
    """
    Branch of Restaurant chain
    """
    main_restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
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
    user_id = models.IntegerField(default=None, null=True)
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
    token = models.CharField(max_length=16)
    language = models.CharField(max_length=4)


class StudentInfo(models.Model):
    """
    Student Info for staff interface
    """
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    position = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    second_name = models.CharField(max_length=255)
    third_name = models.CharField(max_length=255)
    date_start = models.DateField(default=now)
    date_birth = models.DateField(default=None, null=True, blank=True)
    phone = models.CharField(max_length=20, default=None, blank=True, null=True)
    email = models.EmailField()
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
    answers = models.ManyToManyField(TestAnswer)


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
    restaurant = models.ForeignKey(RestaurantBranch, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    text = NonStrippingTextField()
    test = models.OneToOneField(TheoryTest, on_delete=models.SET_NULL, null=True)
    blocks = models.ManyToManyField(TheoryBlock)
    finished = models.BooleanField(default=False)
    blocked = models.BooleanField(default=True)


class StudentAnswer(models.Model):
    """
    Student answer for check
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE)
    answer = models.ForeignKey(TestAnswer, on_delete=models.SET_NULL, null=True)
    text = models.TextField(null=True, blank=True)


class StudentTest(models.Model):
    """
    oppened test for student
    """
    test = models.ForeignKey(TheoryTest, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    answers = models.ManyToManyField(StudentAnswer)
    is_finished = models.BooleanField(default=False)
    points = models.PositiveSmallIntegerField(default=None, null=True, blank=True)
    max_points = models.PositiveSmallIntegerField(default=None, null=True, blank=True)
    opened_questions = models.PositiveSmallIntegerField(default=None, null=True, blank=True)
    max_opened_questions = models.PositiveSmallIntegerField(default=None, null=True, blank=True)








