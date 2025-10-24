# En tu archivo main.py o donde inicialices la aplicación
from infrastructure.database.session import DatabaseSession
from infrastructure.database.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from core.use_cases.users.create_user_use_case import CreateUserUseCase
from core.use_cases.users.get_user_use_case import GetUserUseCase
from core.use_cases.users.update_user_use_case import UpdateUserUseCase
from core.use_cases.users.delete_user_use_case import DeleteUserUseCase
from core.use_cases.users.list_users_use_case import ListUsersUseCase
from application.services import create_user_service
from application.controllers import create_user_controller

# 1. Configurar base de datos y repositorios
db_session = DatabaseSession()
session = db_session.get_session()

user_repository = SQLAlchemyUserRepository(session)

# 2. Crear use cases
create_user_use_case = CreateUserUseCase(user_repository)
get_user_use_case = GetUserUseCase(user_repository)
update_user_use_case = UpdateUserUseCase(user_repository)
delete_user_use_case = DeleteUserUseCase(user_repository)
list_users_use_case = ListUsersUseCase(user_repository)

# 3. Crear servicio
user_service = create_user_service(
    create_user_use_case,
    get_user_use_case, 
    update_user_use_case,
    delete_user_use_case,
    list_users_use_case
)

# 4. Crear controller
user_controller = create_user_controller(user_service)

# 5. Usar en la GUI
# Ejemplo: Crear usuario desde la interfaz
result = user_controller.create_user(CreateUserRequest(
    username="nuevo_usuario",
    email="usuario@empresa.com",
    role=UserRole.USER
))

if result.success:
    print(f"✅ Usuario creado: {result.message}")
else:
    print(f"❌ Error: {result.error}")

# Ejemplo: Obtener estadísticas
stats = user_controller.get_user_statistics()
if stats['success']:
    print(f"📊 Total usuarios: {stats['data']['total_users']}")