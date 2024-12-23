from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import FieldOfficer
from business.models import UserInBusiness

@receiver(pre_save, sender = FieldOfficer)
def assign_default_manager(sender, instance, **kwargs):
    business_id = instance.user.business.business.id
    user_in_business = UserInBusiness.objects.filter(business=business_id, role='admin').first()
    admin_obj = user_in_business.user

    if instance.manager == None:
        instance.manager = admin_obj
        instance.manager.save()  
        print('Assigned the admin as a manager Successfully')  

# @receiver(pre_save, sender = FieldOfficer)
# def assign_default_manager(sender, instance, **kwargs):
#     business_id = instance.user.business.business.id
#     user_in_business = UserInBusiness.objects.filter(business=business_id, role='admin').first()
#     admin_obj = user_in_business.user

#     if instance.manager == None:
#         instance.manager = admin_obj
#         instance.manager.save()  
#         print('Assigned the admin as a manager Successfully')  
    