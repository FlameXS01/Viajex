import tkinter as tk
import pandas as pd
from application.dtos.request_user_dtos import RequestUserCreateDTO
from core.entities.department import Department
from core.entities.diet_service import DietService
from core.repositories.department_repository import DepartmentRepository
from core.use_cases.request_user import create_request_user, delete_request_user, get_request_user, update_user_request
from core.use_cases.request_user.list_users_request import ListRequestUsersUseCase
from infrastructure.database.repositories.department_repository import DepartmentRepositoryImpl
from infrastructure.database.repositories.diet_liquidation_repository import DietLiquidationRepositoryImpl
from infrastructure.database.repositories.diet_member_repository import DietMemberRepositoryImpl
from infrastructure.database.repositories.diet_repository import DietRepositoryImpl
from infrastructure.database.repositories.diet_service_repository import DietServiceRepositoryImpl
from infrastructure.database.repositories.request_user_repository import RequestUserRepositoryImpl
from infrastructure.database.repositories.user_repository import UserRepositoryImpl
from infrastructure.database.session import Base, engine
from infrastructure.security.password_hasher import BCryptPasswordHasher
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use Cases User
from core.use_cases.users.create_user import CreateUserUseCase
from core.use_cases.users.update_user import UpdateUserUseCase
from core.use_cases.users.update_user_role import UpdateUserRoleUseCase
from core.use_cases.users.update_user_password import UpdateUserPasswordUseCase
from core.use_cases.users.toggle_user_active import ToggleUserActiveUseCase
from core.use_cases.users.delete_user import DeleteUserUseCase
from core.use_cases.auth.login import LoginUseCase

# Use Cases department 
from core.use_cases.department.create_department import CreateDepartmentUseCase
from core.use_cases.department.update_department import UpdateDepartmentUseCase
from core.use_cases.department.get_department import GetDepartmentUseCase
from core.use_cases.department.delete_department import DeleteDepartmentUseCase
from core.use_cases.department.list_department import ListDepartmentUseCase

# Use Cases request user 
from core.use_cases.request_user.create_request_user import CreateRequestUserUseCase
from core.use_cases.request_user.update_user_request import UpdateRequestUserUseCase
from core.use_cases.request_user.get_request_user import GetRequestUserUseCase
from core.use_cases.request_user.delete_request_user import DeleteRequestUserUseCase
from core.use_cases.request_user.list_users_request import ListRequestUsersUseCase

# Use Case diets
# from core.use_cases.diets.calculate_diet_amount import CalculateDietAmountUseCase
# from core.use_cases.diets.list_diets import ListDietsUseCase
# from core.use_cases.diets.reset_counters import ResetCountersUseCase

# from core.use_cases.diets.diet_liquidations.create_diet_liquidation import CreateDietLiquidationUseCase
# from core.use_cases.diets.diet_liquidations.delete_diet_liquidation import DeleteDietLiquidationUseCase
# from core.use_cases.diets.diet_liquidations.get_diet_liquidation import GetDietLiquidationUseCase
# from core.use_cases.diets.diet_liquidations.get_last_liquidation_number import GetLastLiquidationNumberUseCase
# from core.use_cases.diets.diet_liquidations.get_liquidation_by_diet import GetLiquidationByDietUseCase
# from core.use_cases.diets.diet_liquidations.list_liquidations_by_date_range import ListLiquidationsByDateRangeUseCase
# from core.use_cases.diets.diet_liquidations.reset_liquidation_numbers import ResetLiquidationNumbersUseCase
# from core.use_cases.diets.diet_liquidations.update_diet_liquidation import UpdateDietLiquidationUseCase

# from core.use_cases.diets.diet_members.add_diet_member import AddDietMemberUseCase
# from core.use_cases.diets.diet_members.list_diet_members import ListDietMembersUseCase
# from core.use_cases.diets.diet_members.remove_diet_member import RemoveDietMemberUseCase

# from core.use_cases.diets.diet_services.get_diet_service_by_local import GetDietServiceByLocalUseCase
# from core.use_cases.diets.diet_services.list_all_diet_services import ListAllDietServicesUseCase

# from core.use_cases.diets.diets.create_diet import CreateDietUseCase
# from core.use_cases.diets.diets.delete_diet import DeleteDietUseCase
# from core.use_cases.diets.diets.get_diet import GetDietUseCase
# from core.use_cases.diets.diets.get_last_advance_number import GetLastAdvanceNumberUseCase
# from core.use_cases.diets.diets.list_diets_by_status import ListDietsByStatusUseCase
# from core.use_cases.diets.diets.list_diets_pending_liquidation import ListDietsPendingLiquidationUseCase
# from core.use_cases.diets.diets.reset_advance_numbers import ResetAdvanceNumbersUseCase
# from core.use_cases.diets.diets.update_diet import UpdateDietUseCase

# Services
from application.services.user_service import UserService
from application.services.auth_service import AuthService
from application.services.department_service import DepartmentService
from application.services.request_service import UserRequestService
from application.services.diet_service import DietAppService

# GUI
from presentation.gui.login_window import LoginWindow
from presentation.gui.main_dashboard import MainDashboard

# Entities
from core.entities.user import User, UserRole

def _departaments_by_file() -> list[str]:
    """
    
    Script para obtener los nombres de las unidades(departments)
    
    """
    # Se saltan las primeras 3 filas porque no brindan informacion
    df = pd.read_excel("Files/Maestro de trabajadores cierre septiembre.xlsx",skiprows=3)
    dirty_unidades = df['Unidad'].value_counts()  
    unidades =[]
    for value, unidad in enumerate(dirty_unidades.index):
        unidades.append(unidad.strip())
    return unidades

def _request_users_by_file() -> list[dict]:
    """
    
    Script para obtener los nombres de los solicitantes
    
    """
    # Se saltan las primeras 3 filas porque no brindan informacion
    df = pd.read_excel("Files/Maestro de trabajadores cierre septiembre.xlsx",skiprows=3)
    dirty_data = df[['Nomre y apellidos', 'CI', 'Unidad']]
    personas = []
    for index, fila in dirty_data.iterrows():
            nombre = str(fila['Nomre y apellidos']).strip()
            ci = str(fila['CI']).strip()
            unidad = str(fila['Unidad']).strip()
           
            if len(ci) > 11:
                continue

            persona = {
                'nombre': nombre,
                'ci': ci, 
                'unidad': unidad
            }
            personas.append(persona)
    return personas
    
def initialize_request_users(request_user_service: UserRequestService, personas: list[dict], department_service: DepartmentService):
    """
    Crea los solicitantes por defecto si no existen
    
    Args:
        request_user_service: Servicio para manejar usuarios
        personas: Lista de personas desde el archivo
        department_service: Servicio para manejar departamentos
    """
    for persona in personas:
        try:
            requ_user = request_user_service.get_user_by_ci(persona['ci'])
            if requ_user:
                continue

            department = department_service.get_department_by_name(name=persona['unidad'])
            if not department:
                print(f"  ❌ Departamento no encontrado: '{persona['unidad']}'")
                continue

            # Crear DTO y usuario
            user_data = RequestUserCreateDTO(
                username=None,
                fullname=persona['nombre'],
                email=None,
                ci=persona['ci'],
                department_id=department.id                                                                         # type: ignore
            )
            
            requ_user = request_user_service.create_user(user_data)
            
            if requ_user:
                continue
        except Exception as e:
            print(f"❌ Error creando {persona.get('nombre', 'N/A')}: {e}")
            import traceback
            traceback.print_exc()
    print('Solicitantes inicializados')

def initialize_admin_user(user_service: UserService):
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

def initializate_departments (department_service: DepartmentService, unidades: list[str]):
    """
    
    Crea los departamentos por defecto si no existen
    
    """
    for unidad in unidades:
        department = department_service.get_department_by_name(name=unidad)
        if not department:
            try:
                # Crear usuario admin por defecto
                department = department_service.create_department_f(
                    name=unidad
                )
            except Exception as e:
                print(f"Error creando departamento {unidad}: {e}")
    print('Departamentos inicializados')

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
        department_repository = DepartmentRepositoryImpl(db_session)
        request_user_repository = RequestUserRepositoryImpl(db_session)

        diet_liquidation_repository = DietLiquidationRepositoryImpl(db_session)
        diet_member_repository = DietMemberRepositoryImpl(db_session)
        diet_repository = DietRepositoryImpl(db_session)
        diet_service_repository = DietServiceRepositoryImpl(db_session)
        
        # Inicializar casos de uso de usuarios
        create_user_use_case = CreateUserUseCase(user_repository, password_hasher)
        update_user_use_case = UpdateUserUseCase(user_repository)
        update_user_role_use_case = UpdateUserRoleUseCase(user_repository)
        update_user_password_use_case = UpdateUserPasswordUseCase(user_repository, password_hasher)
        toggle_user_active_use_case = ToggleUserActiveUseCase(user_repository)
        delete_user_use_case = DeleteUserUseCase(user_repository)
        
        # Inicializar casos de uso de department
        create_department = CreateDepartmentUseCase(department_repository)
        update_department = UpdateDepartmentUseCase(department_repository)
        get_department = GetDepartmentUseCase(department_repository)
        delete_department = DeleteDepartmentUseCase(department_repository)
        get_department_list = ListDepartmentUseCase(department_repository)

        # Inicializar casos de uso de solicitantes
        create_request_user = CreateRequestUserUseCase(request_user_repository)
        update_user_request = UpdateRequestUserUseCase(request_user_repository)
        get_request_user = GetRequestUserUseCase(request_user_repository)
        delete_request_user = DeleteRequestUserUseCase(request_user_repository)
        get_request_user_list = ListRequestUsersUseCase(request_user_repository)

        # Inicializar casos de uso de dietas
        # calculate_diet_amount = CalculateDietAmountUseCase(diet_service_repository)
        # list_diets = ListDietsUseCase(diet_repository)
        # reset_counters = ResetCountersUseCase(diet_repository, diet_liquidation_repository)

        # create_diet_liquidation = CreateDietLiquidationUseCase(diet_repository, diet_liquidation_repository, diet_service_repository)
        # delete_diet_liquidation = DeleteDietLiquidationUseCase(diet_liquidation_repository, diet_repository)
        # get_diet_liquidation = GetDietLiquidationUseCase(diet_liquidation_repository)
        # get_last_liquidation_number = GetLastLiquidationNumberUseCase( diet_liquidation_repository)
        # get_liquidation_by_diet = GetLiquidationByDietUseCase(diet_liquidation_repository)
        # list_liquidations_by_date_range = ListLiquidationsByDateRangeUseCase(diet_liquidation_repository)
        # reset_liquidation_numbers = ResetLiquidationNumbersUseCase(diet_liquidation_repository)
        # update_diet_liquidation = UpdateDietLiquidationUseCase( diet_liquidation_repository)

        # add_diet_member = AddDietMemberUseCase(diet_repository,diet_member_repository, request_user_repository)
        # list_diet_members = ListDietMembersUseCase(diet_member_repository)
        # remove_diet_member = RemoveDietMemberUseCase(diet_member_repository)
        
        # get_diet_service_by_local = GetDietServiceByLocalUseCase(diet_service_repository)
        # list_all_diet_services = ListAllDietServicesUseCase(diet_service_repository)

        # create_diet = CreateDietUseCase(diet_repository, diet_service_repository, request_user_repository)
        # delete_diet = DeleteDietUseCase(diet_repository, diet_member_repository, diet_liquidation_repository)
        # get_diet = GetDietUseCase(diet_repository)
        # get_last_advance_number = GetLastAdvanceNumberUseCase(diet_repository)
        # list_diets_by_status = ListDietsByStatusUseCase(diet_repository)
        # list_diets_pending_liquidation = ListDietsPendingLiquidationUseCase(diet_repository)
        # reset_advance_numbers = ResetAdvanceNumbersUseCase(diet_repository)
        # update_diet = UpdateDietUseCase(diet_repository)

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

        # Inicializar servicio de departments
        department_service = DepartmentService(
            department_repository=department_repository,
            create_department=create_department,
            update_department=update_department,
            get_department=get_department,
            delete_department=delete_department,
            get_department_list=get_department_list
        )

        # Inicializar servicio de solicitantes
        request_user_service = UserRequestService(
            request_user_repository=request_user_repository,
            create_request_user=create_request_user,
            update_user_request=update_user_request,
            get_user_request=get_request_user,
            get_user_request_list=get_request_user_list,
            delete_user_request=delete_request_user
        )

        diet_service = DietAppService(
            diet_liquidation_repository=diet_liquidation_repository,
            diet_service_repository = diet_service_repository,
            diet_repository = diet_repository,
            diet_member_repository = diet_member_repository,
            request_user_repository = request_user_repository,
        )

        # Crear usuario admin por defecto
        initialize_admin_user(user_service)

        # Crear departamentos
        unidades = _departaments_by_file()
        initializate_departments(department_service, unidades)

        personas = _request_users_by_file()
        initialize_request_users(request_user_service, personas, department_service)

        # Inicializar casos de uso de autenticación
        login_use_case = LoginUseCase(user_repository, password_hasher)

        # Inicializar servicio de autenticación
        auth_service = AuthService(user_repository, login_use_case)

        # Función que se ejecuta cuando el login es exitoso
        def on_login_success(user):
            """Callback que se ejecuta después de un login exitoso"""
            dashboard = MainDashboard(
                user,
                user_service,
                auth_service, 
                department_service, 
                request_user_service,
                diet_service
                )
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