import sys
import os

# Añadir el directorio del proyecto al path de Python para asegurar
# que los módulos internos se encuentren correctamente.
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from carniceria_system.views.main_view import App

if __name__ == "__main__":
    print("Iniciando la aplicación...")
    # Instanciar la aplicación
    app = App()

    # Iniciar el bucle de eventos de la aplicación
    app.run()
