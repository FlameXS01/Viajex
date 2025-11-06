import tkinter as tk
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from infrastructure.database.session import Base, engine
from infrastructure.database.repositories.user_repository import UserRepositoryImpl
from infrastructure.security.password_hasher import BCryptPasswordHasher

# Use Cases
from core.use_cases.users.create_user import CreateUserUseCase
from core.use_cases.users.update_user import UpdateUserUseCase
from core.use_cases.users.update_user_role import UpdateUserRoleUseCase
from core.use_cases.users.update_user_password import UpdateUserPasswordUseCase
from core.use_cases.users.toggle_user_active import ToggleUserActiveUseCase
from core.use_cases.users.delete_user import DeleteUserUseCase
from core.use_cases.auth.login import LoginUseCase

# Services
from application.services.user_service import UserService
from application.services.auth_service import AuthService
from application.services.card_service import CardService

# GUI
from presentation.gui.login_window import LoginWindow
from presentation.gui.main_dashboard import MainDashboard

# Entities
from core.entities.user import User, UserRole
from infrastructure.database.repositories.card_repository import CardRepositoryImpl
from core.use_cases.cards.create_card import CreateCardUseCase
from core.use_cases.cards.update_card import UpdateCardUseCase
from core.use_cases.cards.toggle_card_active import ToggleCardActiveUseCase
from core.use_cases.cards.delete_card import DeleteCardUseCase
from core.use_cases.cards.get_card_use_case import GetCardUseCase

def initialize_admin_user(user_service, password_hasher):
    """
    Crea el usuario administrador por defecto si no existe
    """
    admin_user = user_service.get_user_by_username("admin")
    if not admin_user:
        try:
            # Crear usuario admin por defecto
            admin_user = user_service.create_user(
                username="admin",
                email="admin@dietasapp.com",
                password="admin01*",
                role=UserRole.ADMIN
            )
            print("Usuario administrador creado por defecto")
        except Exception as e:
            print(f"Error creando usuario admin: {e}")

def main():
    """Función principal que inicializa la aplicación completa"""
    # Configuración de la base de datos
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = SessionLocal()

    try:
        # Inicializar dependencias
        user_repository = UserRepositoryImpl(db_session)
        password_hasher = BCryptPasswordHasher()
        card_repository = CardRepositoryImpl(db_session)
        
        # Inicializar casos de uso de usuarios
        create_user_use_case = CreateUserUseCase(user_repository, password_hasher)
        update_user_use_case = UpdateUserUseCase(user_repository)
        update_user_role_use_case = UpdateUserRoleUseCase(user_repository)
        update_user_password_use_case = UpdateUserPasswordUseCase(user_repository, password_hasher)
        toggle_user_active_use_case = ToggleUserActiveUseCase(user_repository)
        delete_user_use_case = DeleteUserUseCase(user_repository)
        
        # Inicializar casos de uso de card
        create_card_use_case = CreateCardUseCase(card_repository)
        update_card_use_case = UpdateCardUseCase(card_repository)
        toggle_card_active_use_case = ToggleCardActiveUseCase(card_repository)
        get_card_use_case=GetCardUseCase(card_repository)
        delete_card_use_case = DeleteCardUseCase(card_repository)

        # Inicializar servicio de usuarios
        user_service = UserService(
            user_repository=user_repository,
            create_user_use_case=create_user_use_case,
            update_user_use_case=update_user_use_case,
            update_user_role_use_case=update_user_role_use_case,
            update_user_password_use_case=update_user_password_use_case,
            toggle_user_active_use_case=toggle_user_active_use_case,
            delete_user_use_case=delete_user_use_case
        )
        
        # Inicializar servicio de card
        card_service = CardService(
            card_repository=card_repository,
            create_card_use_case=create_card_use_case,
            update_card_use_case=update_card_use_case,
            toggle_card_active_use_case=toggle_card_active_use_case,
            delete_card_use_case=delete_card_use_case,
            get_card_use_case=get_card_use_case
        )

        # Crear usuario admin por defecto
        initialize_admin_user(user_service, password_hasher)

        # Inicializar casos de uso de autenticación
        login_use_case = LoginUseCase(user_repository, password_hasher)

        # Inicializar servicio de autenticación
        auth_service = AuthService(user_repository, login_use_case)

        # Función que se ejecuta cuando el login es exitoso
        def on_login_success(user):
            """Callback que se ejecuta después de un login exitoso"""
            dashboard = MainDashboard(user, user_service, auth_service, card_service)
            dashboard.run()

        # Ciclo principal de la aplicación
        while True:
            # Mostrar ventana de login
            login_window = LoginWindow(auth_service, on_login_success)
            login_window.run()
            
            # Después de cerrar el dashboard, preguntar si quiere salir completamente
            if not auth_service.is_authenticated():
                response = tk.messagebox.askyesno(
                    "Salir", 
                    "¿Desea salir completamente de la aplicación?"
                )
                if response:
                    break

    except Exception as e:
        print(f"Error crítico en la aplicación: {e}")
        tk.messagebox.showerror("Error", f"Error crítico: {e}")
    finally:
        db_session.close()

if __name__ == "__main__":
    main()