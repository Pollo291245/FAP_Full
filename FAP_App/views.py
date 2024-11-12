from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Count, Q, Max, Prefetch
from .models import Store, VeterinaryClinic, AdoptionCenter, ForumCategory, ForumPost, ForumComment, UserProfile

def is_admin(user):
    return hasattr(user, 'userprofile') and user.userprofile.is_admin()

def check_banned(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
            if request.user.userprofile.is_banned:
                messages.error(request, 'Tu cuenta está suspendida temporalmente')
                return redirect('logout')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            user = authenticate(username=user.username, password=password)
            if user is not None:
                if user.userprofile.is_banned:
                    messages.error(request, 'Tu cuenta está suspendida temporalmente')
                    return render(request, 'FAP_APP/login.html')
                auth_login(request, user)
                messages.success(request, '¡Bienvenido de vuelta!')
                return redirect('landingP')
            else:
                messages.error(request, 'Contraseña incorrecta')
        except User.DoesNotExist:
            messages.error(request, 'No existe una cuenta con ese correo electrónico')
    return render(request, 'FAP_APP/login.html')

def logout(request):
    auth_logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente')
    return redirect('login')

def registro(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'FAP_APP/registro.html')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Ya existe una cuenta con ese correo electrónico')
            return render(request, 'FAP_APP/registro.html')
            
        try:
            username = email.split('@')[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f'{base_username}{counter}'
                counter += 1
                
            user = User.objects.create_user(username=username, email=email, password=password1)
            UserProfile.objects.create(user=user)
            auth_login(request, user)
            messages.success(request, '¡Cuenta creada exitosamente!')
            return redirect('landingP')
        except Exception as e:
            messages.error(request, 'Error al crear la cuenta. Por favor, intenta de nuevo.')
            
    return render(request, 'FAP_APP/registro.html')

@login_required
@check_banned
def cuenta(request):
    if request.method == 'POST':
        profile = request.user.userprofile
        profile.bio = request.POST.get('bio', '')
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.notifications_enabled = request.POST.get('notifications_enabled') == 'on'
        profile.dark_mode = request.POST.get('dark_mode') == 'on'
        profile.save()
        messages.success(request, 'Perfil actualizado exitosamente')
        return redirect('cuenta')
    return render(request, 'FAP_APP/cuenta.html')

@login_required
@user_passes_test(is_admin)
@check_banned
def panelA(request):
    users = User.objects.prefetch_related(
        Prefetch(
            'forumpost_set',
            queryset=ForumPost.objects.select_related('category').order_by('-created_at')
        )
    ).all()

    stores = Store.objects.filter(is_active=True).order_by('-created_at')
    veterinaries = VeterinaryClinic.objects.filter(is_active=True).order_by('-created_at')
    adoption_centers = AdoptionCenter.objects.filter(is_active=True).order_by('-created_at')
    
    context = {
        'users': users,
        'stores': stores,
        'veterinaries': veterinaries,
        'adoption_centers': adoption_centers,
    }
    
    return render(request, 'FAP_APP/panelA.html', context)

@login_required
@user_passes_test(is_admin)
@check_banned
def editar(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        profile = user.userprofile
        
        user.email = request.POST.get('email', user.email)
        profile.role = request.POST.get('role', profile.role)
        profile.bio = request.POST.get('bio', profile.bio)
        profile.phone = request.POST.get('phone', profile.phone)
        profile.address = request.POST.get('address', profile.address)
        
        try:
            user.save()
            profile.save()
            messages.success(request, 'Usuario actualizado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar usuario: {str(e)}')
            
    users = User.objects.all().select_related('userprofile')
    return render(request, 'FAP_APP/editar.html', {'users': users})

@login_required
@user_passes_test(is_admin)
@check_banned
def eliminar(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        
        try:
            user.is_active = False
            user.save()
            messages.success(request, 'Usuario eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar usuario: {str(e)}')
            
    users = User.objects.filter(is_active=True).select_related('userprofile')
    return render(request, 'FAP_APP/eliminar.html', {'users': users})

def landingP(request):
    return render(request, 'FAP_APP/Landingpage.html')

def get_location_context(request, model_class, location_type, location_type_singular):
    search = request.GET.get('search', '')
    queryset = model_class.objects.filter(is_active=True)
    
    if search:
        queryset = queryset.filter(name__icontains=search)
    
    if location_type == 'tiendas':
        store_type = request.GET.get('store_type', '')
        if store_type:
            queryset = queryset.filter(store_type=store_type)
    elif location_type == 'veterinarias':
        clinic_type = request.GET.get('clinic_type', '')
        if clinic_type:
            queryset = queryset.filter(clinic_type=clinic_type)
    
    paginator = Paginator(queryset, 8)
    page = request.GET.get('page', 1)
    locations = paginator.get_page(page)
    
    return {
        'locations': locations,
        'location_type': location_type,
        'location_type_singular': location_type_singular,
        'page_title': location_type.title(),
    }

def tiendas(request):
    context = get_location_context(request, Store, 'tiendas', 'tienda')
    return render(request, 'FAP_APP/location_list.html', context)

def veterinarias(request):
    context = get_location_context(request, VeterinaryClinic, 'veterinarias', 'veterinaria')
    return render(request, 'FAP_APP/location_list.html', context)

def adopcion(request):
    context = get_location_context(request, AdoptionCenter, 'adopcion', 'centro de adopción')
    return render(request, 'FAP_APP/location_list.html', context)

def reseñasV(request):
    veterinaries = VeterinaryClinic.objects.filter(is_active=True)
    context = {
        'veterinaries': veterinaries,
        'page_title': 'Reseñas de Veterinarias',
    }
    return render(request, 'FAP_APP/reseñasV.html', context)

@login_required
@user_passes_test(is_admin)
@check_banned
def add_location(request, location_type):
    if request.method == 'POST':
        model_class = {
            'tiendas': Store,
            'veterinarias': VeterinaryClinic,
            'adopcion': AdoptionCenter
        }[location_type]
        
        try:
            location = model_class(
                name=request.POST['name'],
                address=request.POST['address'],
                phone=request.POST['phone'],
                email=request.POST['email'],
                website=request.POST.get('website', ''),
                description=request.POST['description'],
                created_by=request.user
            )
            
            if request.FILES.get('image'):
                location.image = request.FILES['image']
                
            if location_type == 'tiendas':
                location.store_type = request.POST['store_type']
                location.delivery = request.POST.get('delivery') == 'on'
            elif location_type == 'veterinarias':
                location.clinic_type = request.POST['clinic_type']
                location.emergency_service = request.POST.get('emergency_service') == 'on'
            elif location_type == 'adopcion':
                location.total_pets = request.POST['total_pets']
                location.requirements = request.POST['requirements']
                location.adoption_process = request.POST['adoption_process']
                location.needs_donations = request.POST.get('needs_donations') == 'on'
                
            location.save()
            messages.success(request, 'Ubicación agregada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al agregar la ubicación: {str(e)}')
            
    return redirect('panelA')

@login_required
@user_passes_test(is_admin)
@check_banned
def edit_location(request, location_type, location_id):
    model_class = {
        'tiendas': Store,
        'veterinarias': VeterinaryClinic,
        'adopcion': AdoptionCenter
    }[location_type]
    
    location = get_object_or_404(model_class, id=location_id)
    
    if request.method == 'POST':
        try:
            location.name = request.POST['name']
            location.address = request.POST['address']
            location.phone = request.POST['phone']
            location.email = request.POST['email']
            location.website = request.POST.get('website', '')
            location.description = request.POST['description']
            
            if request.FILES.get('image'):
                location.image = request.FILES['image']
                
            if location_type == 'tiendas':
                location.store_type = request.POST['store_type']
                location.delivery = request.POST.get('delivery') == 'on'
            elif location_type == 'veterinarias':
                location.clinic_type = request.POST['clinic_type']
                location.emergency_service = request.POST.get('emergency_service') == 'on'
            elif location_type == 'adopcion':
                location.total_pets = request.POST['total_pets']
                location.requirements = request.POST['requirements']
                location.adoption_process = request.POST['adoption_process']
                location.needs_donations = request.POST.get('needs_donations') == 'on'
                
            location.save()
            messages.success(request, 'Ubicación actualizada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar la ubicación: {str(e)}')
            
    return redirect('panelA')

@login_required
@user_passes_test(is_admin)
@check_banned
def delete_location(request, location_type, location_id):
    model_class = {
        'tiendas': Store,
        'veterinarias': VeterinaryClinic,
        'adopcion': AdoptionCenter
    }[location_type]
    
    location = get_object_or_404(model_class, id=location_id)
    
    try:
        location.is_active = False
        location.save()
        messages.success(request, 'Ubicación eliminada exitosamente')
    except Exception as e:
        messages.error(request, f'Error al eliminar la ubicación: {str(e)}')
        
    return redirect('panelA')

@login_required
@user_passes_test(is_admin)
@check_banned
def ban_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = user.userprofile
    
    if request.method == 'POST':
        try:
            profile.is_banned = True
            profile.ban_end_date = request.POST.get('ban_end_date')
            profile.save()
            messages.success(request, f'Usuario {user.username} baneado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al banear al usuario: {str(e)}')
            
    return redirect('panelA')

@login_required
@user_passes_test(is_admin)
@check_banned
def unban_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = user.userprofile
    
    try:
        profile.is_banned = False
        profile.ban_end_date = None
        profile.save()
        messages.success(request, f'Usuario {user.username} desbaneado exitosamente')
    except Exception as e:
        messages.error(request, f'Error al desbanear al usuario: {str(e)}')
        
    return redirect('panelA')

@login_required
@check_banned
def foro(request):
    category_id = request.GET.get('category')
    
    posts_queryset = ForumPost.objects.select_related('author', 'category').order_by('-created_at')
    
    if category_id:
        posts_queryset = posts_queryset.filter(category_id=category_id)
    
    pinned_posts = posts_queryset.filter(is_pinned=True, is_locked=False)
    
    regular_posts = posts_queryset.filter(is_pinned=False, is_locked=False)
    paginator = Paginator(regular_posts, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    categories = ForumCategory.objects.filter(is_active=True)
    
    user_posts = []
    user_comments = []
    if request.user.is_authenticated:
        user_posts = ForumPost.objects.filter(author=request.user).order_by('-created_at')[:5]
        user_comments = ForumComment.objects.filter(author=request.user).order_by('-created_at')[:5]
    
    context = {
        'categories': categories,
        'pinned_posts': pinned_posts,
        'page_obj': page_obj,
        'user_posts': user_posts,
        'user_comments': user_comments,
        'selected_category': category_id,
    }
    
    return render(request, 'FAP_APP/foro.html', context)

@login_required
@check_banned
def create_post(request):
    if request.method == 'POST':
        try:
            post = ForumPost.objects.create(
                title=request.POST['title'],
                content=request.POST['content'],
                author=request.user,
                category_id=request.POST['category'],
                tags=request.POST.getlist('tags[]')
            )
            messages.success(request, 'Publicación creada exitosamente')
            return redirect('view_post', post_id=post.id)
        except Exception as e:
            messages.error(request, f'Error al crear la publicación: {str(e)}')
            return redirect('foro')
    
    categories = ForumCategory.objects.filter(is_active=True)
    return render(request, 'FAP_APP/create_post.html', {'categories': categories})

@login_required
@check_banned
def view_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    comments = ForumComment.objects.filter(post=post, parent=None).prefetch_related('replies')
    
    if request.method == 'POST':
        try:
            parent_id = request.POST.get('parent_id')
            parent = ForumComment.objects.get(id=parent_id) if parent_id else None
            
            comment = ForumComment.objects.create(
                post=post,
                author=request.user,
                content=request.POST['content'],
                parent=parent
            )
            messages.success(request, 'Comentario agregado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al agregar el comentario: {str(e)}')
    
    post.views += 1
    post.save()
    
    context = {
        'post': post,
        'comments': comments,
    }
    
    return render(request, 'FAP_APP/view_post.html', context)

@login_required
@check_banned
def edit_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    
    if request.user != post.author and not request.user.userprofile.is_admin():
        messages.error(request, 'No tienes permiso para editar esta publicación')
        return redirect('view_post', post_id=post.id)
    
    if request.method == 'POST':
        try:
            post.title = request.POST['title']
            post.content = request.POST['content']
            post.category_id = request.POST['category']
            post.tags = request.POST.getlist('tags[]')
            post.save()
            messages.success(request, 'Publicación actualizada exitosamente')
            return redirect('view_post', post_id=post.id)
        except Exception as e:
            messages.error(request, f'Error al actualizar la publicación: {str(e)}')
    
    categories = ForumCategory.objects.filter(is_active=True)
    return render(request, 'FAP_APP/edit_post.html', {'post': post, 'categories': categories})

@login_required
@check_banned
def delete_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    
    if request.user != post.author and not request.user.userprofile.is_admin():
        messages.error(request, 'No tienes permiso para eliminar esta publicación')
        return redirect('view_post', post_id=post.id)
    
    try:
        post.delete()
        messages.success(request, 'Publicación eliminada exitosamente')
    except Exception as e:
        messages.error(request, f'Error al eliminar la publicación: {str(e)}')
    
    return redirect('foro')

@login_required
@check_banned
def user_forum_activity(request, user_id=None):
    user = get_object_or_404(User, id=user_id) if user_id else request.user
    
    posts = ForumPost.objects.filter(author=user).order_by('-created_at')
    comments = ForumComment.objects.filter(author=user).order_by('-created_at')
    
    context = {
        'profile_user': user,
        'posts': posts,
        'comments': comments,
    }
    
    return render(request, 'FAP_APP/user_forum_activity.html', context)

@login_required
def toggle_like_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes.count()
    })

@login_required
def toggle_like_comment(request, comment_id):
    comment = get_object_or_404(ForumComment, id=comment_id)
    
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': comment.likes.count()
    })

@login_required
@user_passes_test(is_admin)
@check_banned
def add_category(request):
    if request.method == 'POST':
        try:
            category = ForumCategory.objects.create(
                name=request.POST['name'],
                description=request.POST.get('description', ''),
                created_by=request.user
            )
            messages.success(request, 'Categoría agregada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al agregar la categoría: {str(e)}')
    return redirect('panelA')

@login_required
@user_passes_test(is_admin)
@check_banned
def edit_category(request, category_id):
    category = get_object_or_404(ForumCategory, id=category_id)
    
    if request.method == 'POST':
        try:
            category.name = request.POST['name']
            category.description = request.POST.get('description', '')
            category.save()
            messages.success(request, 'Categoría actualizada exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar la categoría: {str(e)}')
    return redirect('foro')

@login_required
@user_passes_test(is_admin)
@check_banned
def delete_category(request, category_id):
    category = get_object_or_404(ForumCategory, id=category_id)
    
    try:
        category.is_active = False
        category.save()
        messages.success(request, 'Categoría eliminada exitosamente')
    except Exception as e:
        messages.error(request, f'Error al eliminar la categoría: {str(e)}')
    return redirect('foro')

@login_required
@user_passes_test(is_admin)
@check_banned
def lock_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    
    try:
        post.is_locked = True
        post.save()
        messages.success(request, 'Publicación bloqueada exitosamente')
    except Exception as e:
        messages.error(request, f'Error al bloquear la publicación: {str(e)}')
    return redirect('view_post', post_id=post.id)

@login_required
@user_passes_test(is_admin)
@check_banned
def unlock_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    
    try:
        post.is_locked = False
        post.save()
        messages.success(request, 'Publicación desbloqueada exitosamente')
    except Exception as e:
        messages.error(request, f'Error al desbloquear la publicación: {str(e)}')
    return redirect('view_post', post_id=post.id)