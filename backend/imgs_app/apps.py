from django.apps import AppConfig


class ImgsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'imgs_app'

    def ready(self):
        import imgs_app.signals
