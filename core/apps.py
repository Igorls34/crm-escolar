from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
<<<<<<< HEAD
    
    def ready(self):
        # importa o módulo de signals para conectar os handlers
        import core.signals
=======
>>>>>>> 87dd47473da2f5106596a68cfea294ccf720d0c4
