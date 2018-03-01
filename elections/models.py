from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class UserType(models.Model):
    UserType = models.CharField(max_length=10)

    def __str__(self):
        return self.UserType

class Profile(models.Model):
    UserID = models.OneToOneField(User, on_delete=models.CASCADE)
    GENDERS = (("M","Male"), ("F","Female"))
    Gender = models.CharField(max_length=1, choices=GENDERS)
    UserTypeID = models.ForeignKey(UserType, on_delete=models.PROTECT, blank=True, null=True)
    # ProfilePicture = models.ImageField(default='default_profile.png', upload_to="imageposts/")
    EmailConfirmed = models.BooleanField(default=False)
    # For student number, can you have choices - Teacher or input()?

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(UserID=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Election(models.Model):
    Name = models.CharField(max_length=20)
    # Allow to register / vote when True
    CandidateReg = models.BooleanField(default=True)
    VotingOpen = models.BooleanField(default=False)
    Description = models.CharField(max_length=255, null=True, blank=True)
    GENDERS = (("M","Male"), ("F","Female"))
    Gender = models.CharField(max_length=1, choices=GENDERS, default="M")
    Seats = models.IntegerField(default=7)
    FlipGrid = models.URLField(null=True, blank=True)
    Complete = models.BooleanField(default=False)

    def __str__(self):
        return self.Name

class Candidate(models.Model):
    UserID = models.ForeignKey(User, on_delete=models.CASCADE)
    ElectionID = models.ForeignKey(Election, on_delete=models.CASCADE)
    # Bio = models.CharField(max_length=500, blank=True)
    # Poster = models.ImageField(upload_to="profilepics/", null=True, blank=True)

    def __str__(self):
        return "{}, {}".format(self.UserID.username, self.ElectionID.Name)


# class Post(models.Model):
#     Title = models.CharField(max_length=50)
#     Body = models.TextField()
#     Timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
#     # Approved = models.BooleanField()
#     Author = models.ForeignKey(Candidate, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.Title

#     def model_name(self): 
#         return self.__class__.__name__

# class ImagePost(models.Model):
#     Title = models.CharField(max_length=50)
#     Description = models.CharField(max_length=1000)
#     Image = models.ImageField(upload_to="imageposts/")
#     Timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
#     # Approved = models.BooleanField()
#     Author = models.ForeignKey(Candidate, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.Title

#     def model_name(self): 
#         return self.__class__.__name__

class AllowToVote(models.Model):
    UserTypeID = models.ForeignKey(UserType, on_delete=models.CASCADE)
    ElectionID = models.ForeignKey(Election, on_delete=models.CASCADE)

    def __str__(self):
        return "{} in {}".format(self.UserTypeID.UserType, self.ElectionID.Name)

class AllowToRegister(models.Model):
    UserTypeID = models.ForeignKey(UserType, on_delete=models.CASCADE)
    ElectionID = models.ForeignKey(Election, on_delete=models.CASCADE)

    def __str__(self):
        return "{} in {}".format(self.UserTypeID.UserType, self.ElectionID.Name)

class BallotCast(models.Model):
    UserID = models.ForeignKey(User, on_delete=models.CASCADE)
    ElectionID = models.ForeignKey(Election, on_delete=models.CASCADE)

class CompleteBallot(models.Model):
    ElectionID = models.ForeignKey(Election, on_delete=models.CASCADE)
    Vote = models.TextField(null=True)

class Result(models.Model):
    ElectionID = models.ForeignKey(Election, on_delete=models.CASCADE)
    Results = models.TextField()
    Public = models.BooleanField(default=False)

    def __str__(self):
        return "{} Result".format(self.ElectionID.Name)

    class Meta:
        permissions = (("can_view_results","Can view election results"),)