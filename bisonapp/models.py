from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class TSUserManager(models.Manager):
  def get_user(self, user):
    return super().get_queryset().get(user=user)
  
class TSUser(models.Model):
  TEMPLATEMANAGER = 'TIF'
  BISON_SYSTEM = 'SI'
  MAJOR_CHOICES = (
    (TEMPLATEMANAGER, 'Template Manager'),
    (BISON_SYSTEM, 'Bison System')
  )

  BISONUSER = 'SK'
  BISONADMIN = 'SA'
  ROLE_CHOICES = (
    (BISONUSER, 'BisonUser'),
    (BISONADMIN, 'BisonAdmin')
  )

  objects = TSUserManager()

  
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tsuser')
    

  major = models.CharField(max_length=3, choices=MAJOR_CHOICES)
  role = models.CharField(max_length=2, choices=ROLE_CHOICES)

  def major_string(self):
    majors = dict(self.MAJOR_CHOICES)
    return majors[self.major]

  def role_string(self):
    roles = dict(self.ROLE_CHOICES)
    return roles[self.role]

  def __str__(self):
    return "%s - %s, %s" % (self.user.username, self.major, self.role)
  
  
  def is_admin(self):
    return self.role == TSUser.BISONADMIN
  

  @classmethod
  def get_user(cls, user):
        try:
            return cls.objects.get(user=user)
        except cls.DoesNotExist:
            return None

  
  
'''
  def is_admin(self):
    return self.role == self.BISONADMIN
'''
