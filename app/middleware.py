from django.conf import settings
from app.models import UserProfile
from django.contrib.auth import logout as auth_logout

class UserMiddleware(object):
    def process_request(self, request):
        user = request.user
        
        if user.is_authenticated():
            try:
                if 'HTTP_X_FORWARDED_FOR' in request.META:
                    ip_address = request.META['HTTP_X_FORWARDED_FOR']
                else:
                    if 'REMOTE_ADDR' in request.META:
                        ip_address = request.META['REMOTE_ADDR']
                    
                profile = UserProfile.objects.get(user=user, ip_address=ip_address)
                return None
            except UserProfile.DoesNotExist:
                auth_logout(request)
                
        else:
            return None
                
            