from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from FAP_App.views import (

    login, logout, registro, cuenta,

    editar, eliminar, panelA,

    tiendas, veterinarias, adopcion, reseñasV,
    add_location, edit_location, delete_location,

    ban_user, unban_user,
 
    landingP,

    foro, create_post, view_post, edit_post, delete_post,
    user_forum_activity, toggle_like_post, toggle_like_comment,
    
    add_category, edit_category, delete_category,
    lock_post, unlock_post
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('adopcion/', adopcion, name='adopcion'),
    path('editar/', editar, name='editar'),
    path('eliminar/', eliminar, name='eliminar'),
    path('foro/', foro, name='foro'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('panelA/', panelA, name='panelA'),
    path('registro/', registro, name='registro'),
    path('tiendas/', tiendas, name='tiendas'),
    path('veterinarias/', veterinarias, name='veterinarias'),
    path('landingP/', landingP, name='landingP'),
    path('cuenta/', cuenta, name='cuenta'),
    
    path('add_location/<str:location_type>/', add_location, name='add_location'),
    path('edit_location/<str:location_type>/<int:location_id>/', edit_location, name='edit_location'),
    path('delete_location/<str:location_type>/<int:location_id>/', delete_location, name='delete_location'),
    
    path('ban_user/<int:user_id>/', ban_user, name='ban_user'),
    path('unban_user/<int:user_id>/', unban_user, name='unban_user'),
    
    path('foro/crear/', create_post, name='create_post'),
    path('foro/post/<int:post_id>/', view_post, name='view_post'),
    path('foro/post/<int:post_id>/editar/', edit_post, name='edit_post'),
    path('foro/post/<int:post_id>/eliminar/', delete_post, name='delete_post'),
    path('foro/actividad/', user_forum_activity, name='user_forum_activity'),
    path('foro/actividad/<int:user_id>/', user_forum_activity, name='user_forum_activity_detail'),
    path('foro/post/<int:post_id>/like/', toggle_like_post, name='toggle_like_post'),
    path('foro/comentario/<int:comment_id>/like/', toggle_like_comment, name='toggle_like_comment'),
    
    path('foro/categoria/agregar/', add_category, name='add_category'),
    path('foro/categoria/<int:category_id>/editar/', edit_category, name='edit_category'),
    path('foro/categoria/<int:category_id>/eliminar/', delete_category, name='delete_category'),
    path('foro/post/<int:post_id>/bloquear/', lock_post, name='lock_post'),
    path('foro/post/<int:post_id>/desbloquear/', unlock_post, name='unlock_post'),
    
    path('', landingP, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)