from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from FAP_App.views import (

    login, logout, registro, cuenta,

    editar, eliminar_cuenta, panelA,

    tiendas, veterinarias, adopcion,
    agregar_location, editar_location, borrar_location,

    ban_user, unban_user,
 
    landingP,

    foro, crear_post, ver_post, editar_post, borrar_post,
    user_forum_activity, like_post, like_comentario,
    
    agregar_categoria, editar_categoria, borrar_categoria,
    bloquear_post, desbloquear_post,borrar_comentario, foto_perfil,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('adopcion/', adopcion, name='adopcion'),
    path('editar/', editar, name='editar'),
    path('cuenta/eliminar/<int:user_id>/', eliminar_cuenta, name='eliminar_cuenta'),
    path('foro/', foro, name='foro'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('panelA/', panelA, name='panelA'),
    path('registro/', registro, name='registro'),
    path('tiendas/', tiendas, name='tiendas'),
    path('veterinarias/', veterinarias, name='veterinarias'),
    path('landingP/', landingP, name='landingP'),
    path('cuenta/', cuenta, name='cuenta'),
    
    path('add_location/<str:location_type>/', agregar_location, name='agregar_location'),
    path('edit_location/<str:location_type>/<int:location_id>/', editar_location, name='editar_location'),
    path('delete_location/<str:location_type>/<int:location_id>/', borrar_location, name='borrar_location'),
    
    path('ban_user/<int:user_id>/', ban_user, name='ban_user'),
    path('unban_user/<int:user_id>/', unban_user, name='unban_user'),
    
    path('foro/crear/', crear_post, name='crear_post'),
    path('foro/post/<int:post_id>/', ver_post, name='ver_post'),
    path('foro/post/<int:post_id>/editar/', editar_post, name='editar_post'),
    path('foro/post/<int:post_id>/eliminar/', borrar_post, name='borrar_post'),
    path('foro/actividad/', user_forum_activity, name='user_forum_activity'),
    path('foro/actividad/<int:user_id>/', user_forum_activity, name='user_forum_activity_detail'),
    path('foro/post/<int:post_id>/like/', like_post, name='like_post'),
    path('foro/comentario/<int:comment_id>/like/', like_comentario, name='like_comentario'),
    
    path('foro/categoria/agregar/', agregar_categoria, name='agregar_categoria'),
    path('foro/categoria/<int:category_id>/eliminar/', borrar_categoria, name='borrar_categoria'),
    path('foro/categoria/<int:category_id>/editar/', editar_categoria, name='editar_categoria'),
    path('foro/post/<int:post_id>/bloquear/', bloquear_post, name='bloquear_post'),
    path('foro/post/<int:post_id>/desbloquear/', desbloquear_post, name='desbloquear_post'),
    path('foro/comentario/<int:comment_id>/delete/', borrar_comentario, name='delete_comment'),
    path('foto_perfil/', foto_perfil, name='foto_perfil'),
    
    
    path('', landingP, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)