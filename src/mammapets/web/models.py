from django.db import models
import datetime

# Create your models here.

class Person(models.Model):
    username = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.username


class Client(Person):
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.username


class Pet(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    owner = models.ForeignKey(Client, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class MammaPet(Person):
    phone = models.CharField(max_length=200)

    def __str__(self):
        return self.username


class Contract(models.Model):
    start_date = models.DateTimeField('date started')
    end_date = models.DateTimeField('date ended')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    mamma_pet = models.ForeignKey(MammaPet, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    price = models.FloatField(default=0)
    
    class ContractStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACTIVE = 'ACTIVE', 'Active'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    status = models.CharField(
        max_length=20,
        choices=ContractStatus.choices,
        default=ContractStatus.PENDING,
    )

    def __str__(self):
        return f"Contract for {self.pet.name} - {self.get_status_display()}"


class PetCareLog(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField(default=datetime.date.today)
    notes = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='pet_care_logs/%Y/%m/%d/')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.contract.pet.name} on {self.date}"

    class Meta:
        ordering = ['-date', '-timestamp'] # Order logs by date and then by time
