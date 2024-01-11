from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

#create users model
class MyAccountManager(BaseUserManager):
	def create_user(self, email, username, password=None):
		if not email:
			raise ValueError('Users must have an email address')
		if not username:
			raise ValueError('Users must have a username')

		user = self.model(
			email=self.normalize_email(email),
			username=username,
		)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, username, password):
		user = self.create_user(
			email=self.normalize_email(email),
			password=password,
			username=username,
		)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user

#account model
class Account(AbstractBaseUser):
	email 					= models.EmailField(verbose_name="email", max_length=60, unique=True)
	username 				= models.CharField(max_length=30, unique=True)
	date_joined				= models.DateTimeField(verbose_name='date joined', auto_now_add=True)
	last_login				= models.DateTimeField(verbose_name='last login', auto_now=True)
	is_admin				= models.BooleanField(default=False)
	is_active				= models.BooleanField(default=True)
	is_staff				= models.BooleanField(default=False)
	is_superuser			= models.BooleanField(default=False)
	is_teacher				= models.BooleanField(default=True)
	
	#number grade
	reading_grade			= models.DecimalField(max_digits=5, decimal_places=2, default=0)
	math_grade				= models.DecimalField(max_digits=5, decimal_places=2, default=0)
	science_grade			= models.DecimalField(max_digits=5, decimal_places=2, default=0)
	history_grade			= models.DecimalField(max_digits=5, decimal_places=2, default=0)
	
	#letter grade
	reading_letter_grade	= models.CharField(max_length=1, blank=True, default="F")
	math_letter_grade		= models.CharField(max_length=1, blank=True, default="F")
	history_letter_grade	= models.CharField(max_length=1, blank=True, default="F")
	science_letter_grade	= models.CharField(max_length=1, blank=True, default="F")

	def update_letter_grade(self, grade_field, letter_grade_field):
		if grade_field >= 90:
			setattr(self, letter_grade_field, 'A')
		elif grade_field >= 80:
			setattr(self, letter_grade_field, 'B')
		elif grade_field >= 70:
			setattr(self, letter_grade_field, 'C')
		elif grade_field >= 60:
			setattr(self, letter_grade_field, 'D')
		else:
			setattr(self, letter_grade_field, 'F')

	def save(self, *args, **kwargs):
		#update letter grades based on number grades whenever a number grade changes
		if self.pk is not None:  #check if the instance exists in the database
			previous_instance = Account.objects.get(pk=self.pk)
			grade_fields = ['reading_grade', 'math_grade', 'science_grade', 'history_grade']

			for field in grade_fields:
				if getattr(self, field) != getattr(previous_instance, field):
					self.update_letter_grade(getattr(self, field), f"{field.split('_')[0]}_letter_grade")

		super().save(*args, **kwargs)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']

	objects = MyAccountManager()

	def __str__(self):
		return self.email

	def has_perm(self, perm, obj=None):
		return self.is_admin

	def has_module_perms(self, app_label):
		return True