from django.shortcuts import redirect
from django.urls import reverse

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        protected_routes = ['editar', 'foro', 'cuenta']
        
        admin_routes = [
            'panelA',
            'add_location',
            'edit_location',
            'delete_location',
            'ban_user',
            'unban_user'
        ]
        
        current_path = request.path.strip('/').split('/')[0]
        
        if current_path in protected_routes and not request.user.is_authenticated:
            return redirect('login')
        
        if current_path in admin_routes:
            if not request.user.is_authenticated:
                return redirect('login')
            if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_admin():
                return redirect('landingP')
            
        if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
            if request.user.userprofile.is_banned and current_path != 'logout':
                return redirect('logout')
        
        response = self.get_response(request)
        return response