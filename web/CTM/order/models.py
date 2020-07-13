from django.db import models

# Create your models here.
class OrderDB(models.Model) :
    OrderID = models.IntegerField(null=False, unique=True, primary_key=True)
    product = models.CharField(max_length=255)
    date_regis = models.DateTimeField('Registed Date')
    people = (
        ('cee', 'Wandee Angkura'),
        ('yui', 'aaa bbb')
    )
    person = models.CharField(choices = people, max_length=8)

    def __int__(self) :
        return self.OrderID
