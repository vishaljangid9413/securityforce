from django.apps import AppConfig


class OfficerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'officer'
    
    def ready(self):
        import officer.signals
