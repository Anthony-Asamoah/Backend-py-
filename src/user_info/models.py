import humanize
import pendulum
from django.db import models

from main.utils.base_classes import BaseModel
from user_info.schemas import GenderChoices


class UserInfo(BaseModel):
    title = models.CharField(max_length=10)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    other_names = models.CharField(max_length=100, blank=True, null=True)

    date_of_birth = models.DateField()
    gender = models.CharField(choices=GenderChoices, max_length=10)
    nationality = models.CharField(max_length=100)

    email = models.EmailField(max_length=250)
    phone_number = models.CharField(max_length=20)

    @property
    def age(self):
        return humanize.naturaldelta(
            pendulum.today().date() - pendulum.instance(self.date_of_birth)
        )

    class Meta:
        db_table = 'user_info'
        ordering = ['cursor']

    def __str__(self):
        return f'{self.title.strip()}. {self.first_name} {self.last_name}'
