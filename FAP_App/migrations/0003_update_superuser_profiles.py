from django.db import migrations

def update_superuser_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('FAP_App', 'UserProfile')
    
    # Actualizar todos los perfiles de superusuarios a admin
    for user in User.objects.filter(is_superuser=True):
        try:
            profile = UserProfile.objects.get(user=user)
            profile.role = 'admin'
            profile.save()
        except UserProfile.DoesNotExist:
            UserProfile.objects.create(user=user, role='admin')

def reverse_superuser_profiles(apps, schema_editor):
    # No hacemos nada en la reversión
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('FAP_App', '0002_forumcategory_userprofile_ban_end_date_and_more'),
    ]

    operations = [
        migrations.RunPython(update_superuser_profiles, reverse_superuser_profiles),
    ]