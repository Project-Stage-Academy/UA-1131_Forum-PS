from rest_framework.permissions import BasePermission

from authentication.models import CompanyAndUserRelation


class EditCompanyPermission(BasePermission):
    """
    Custom permission to allow editing company objects only for users who have a relation to the company.
    """
        
    def has_object_permission(self, request, view, obj):
        """
        Return `True` if the requesting user has a relation to the company (obj), `False` otherwise.
        """  
        try:
            relation = CompanyAndUserRelation.objects.get(user_id=request.user, company_id=obj.company_id)
            return True
        except CompanyAndUserRelation.DoesNotExist:
            return False
    
