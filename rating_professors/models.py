from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class Professor(models.Model):
    name = models.CharField(max_length = 100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length = 100)

    def get_average_rating(self):
        ratings = self.ratings.all()  # Use related_name
        if ratings.exists():
            avg = ratings.aggregate(Avg('rating'))['rating__avg']
            return round(avg)  # Round to the nearest integer
        return 0
    
    def get_average_rating_for_module(self, module_code):
        ratings = self.ratings.filter(module_instance__module__code = module_code)
        if ratings.exists():
            avg = ratings.aggregate(Avg('rating'))['rating__avg']
            return round(avg)  
        return 0

    def __str__(self):
        return f"{self.name} ({self.department})"


class Module(models.Model):
    code = models.CharField(max_length = 10, unique = True)
    title = models.CharField(max_length = 100)
    description = models.TextField(blank = True)
    credits = models.IntegerField(default = 10)

    def __str__(self):
        return f"{self.code}: {self.title}"


from django.contrib.auth.models import User

class ModuleInstance(models.Model):
    SEMESTER_CHOICES = [
        (1, "Semester One"),
        (2, "Semester Two")
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='instances')
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(2025)],
        help_text="Academic Year (e.g. 2018 for 2018-2019)"
    )
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    professors = models.ManyToManyField(Professor, related_name='module_instances')
    students = models.ManyToManyField(User, related_name='module_instances')  # New field for students

    class Meta:
        unique_together = ('module', 'year', 'semester')

    def __str__(self):
        return f"{self.module.code}: {self.module.title} ({self.year}/{self.year+1}, {dict(self.SEMESTER_CHOICES)[self.semester]})"
    
    def get_professors(self):
        return ", ".join([professor.name for professor in self.professors.all()])



class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    professor = models.ForeignKey('Professor', on_delete=models.CASCADE)
    module_instance = models.ForeignKey('ModuleInstance', on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'module_instance', 'professor')

    def __str__(self):
        return f"{self.user.username} rated {self.professor.name} {self.rating}/5"