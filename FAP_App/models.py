from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('user', 'Usuario'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    bio = models.TextField(max_length=500, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    notifications_enabled = models.BooleanField(default=True)
    dark_mode = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    ban_end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    foto_perfil = models.ImageField(upload_to='perfil/', default='perfil/default.jpg')
    

    def __str__(self):
        return f"{self.user.email} - {self.get_role_display()}"

    def is_admin(self):
        return self.role == 'admin'

class Location(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, null=True)
    email = models.EmailField(null=True)
    website = models.URLField(blank=True, null=True)
    description = models.TextField()
    image = models.ImageField(upload_to='locations/', blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        abstract = True

class Store(Location):
    TYPE_CHOICES = [
        ('pet_shop', 'Tienda de Mascotas'),
        ('vet_shop', 'Tienda Veterinaria'),
        ('food_shop', 'Tienda de Alimentos'),
    ]
    store_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    delivery = models.BooleanField(default=False)
    delivery_radius = models.IntegerField(default=0, help_text='Radio de entrega en kilómetros')
    opening_hours = models.JSONField(default=dict, help_text='Horario de atención')

    def __str__(self):
        return f"{self.name} - {self.get_store_type_display()}"

class VeterinaryClinic(Location):
    SERVICE_CHOICES = [
        ('general', 'Medicina General'),
        ('emergency', 'Emergencias'),
        ('surgery', 'Cirugía'),
        ('specialist', 'Especialista'),
    ]
    services = models.JSONField(default=list)
    emergency_service = models.BooleanField(default=False)
    clinic_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    veterinarians = models.JSONField(default=list, help_text='Lista de veterinarios')
    specialties = models.JSONField(default=list, help_text='Especialidades disponibles')

    def __str__(self):
        return f"{self.name} - {self.get_clinic_type_display()}"

class AdoptionCenter(Location):
    total_pets = models.IntegerField(default=0)
    requirements = models.TextField()
    adoption_process = models.TextField()
    needs_donations = models.BooleanField(default=False)
    donation_info = models.TextField(blank=True)
    available_species = models.JSONField(default=list, help_text='Especies disponibles')
    success_stories = models.JSONField(default=list, help_text='Historias de adopción exitosas')

    def __str__(self):
        return f"{self.name} - {self.total_pets} mascotas"

class ForumCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    icon = models.CharField(max_length=50, default='chat-dots')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Forum Categories'


class ForumPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    tags = models.JSONField(default=list)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-is_pinned', '-created_at']

class ForumComment(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_solution = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f"Comentario de {self.author.username} en {self.post.title}"

    class Meta:
        ordering = ['created_at']

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'admin' if instance.is_superuser else 'user'
        UserProfile.objects.create(user=instance, role=role)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.is_superuser and instance.userprofile.role != 'admin':
        instance.userprofile.role = 'admin'
    instance.userprofile.save()