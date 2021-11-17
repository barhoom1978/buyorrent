from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    pass

class Scenario(models.Model):
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="scenarios")
    timestamp = models.DateTimeField(auto_now_add=True)
    houseprice = models.DecimalField(max_digits=8, decimal_places=0, default=0)
    deposit = models.DecimalField(max_digits=8, decimal_places=0, default=0)
    interest_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    buildingfees = models.DecimalField(max_digits=8, decimal_places=0, default=0)
    maintenancecosts = models.DecimalField(max_digits=8, decimal_places=0, default=0)
    rent = models.DecimalField(max_digits=8, decimal_places=0, default=0)
    rentersinsurance = models.DecimalField(max_digits=8, decimal_places=0, default=0)
    inflation = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    growth_ftse = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    growth_house = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    summary = models.CharField(max_length=512)

    def serialise(self):
        return [
                float(self.houseprice),
                float(self.deposit),
                float(self.interest_rate),
                float(self.buildingfees),
                float(self.maintenancecosts),
                float(self.rent),
                float(self.rentersinsurance),
                float(self.inflation),
                float(self.growth_ftse),
                float(self.growth_house)
        ]
