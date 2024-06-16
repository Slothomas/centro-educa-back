from storages.backends.azure_storage import AzureStorage

class AzureMediaStorage(AzureStorage):
    account_name = 'centroeducacuentaalmacen'  # Nombre de tu cuenta de Azure
    account_key = 'nF5/lpdsklwaoEWRDCetAL7sWq+biuYiu6mb2uLQdio8aN2LA9IEdD04TZjWNKSG7GC203AbksW+ASt3cNrVw=='  # Clave de tu cuenta de Azure
    azure_container = 'centro-educa-moduleeventos-images'  # Nombre de tu contenedor
    expiration_secs = None  # Opcional, puede ser None para no expirar
