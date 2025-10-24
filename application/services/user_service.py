from typing import Dict, Any, List, Optional
from core.use_cases.auth.create_user_use_case import CreateUserUseCase
from core.use_cases.users.get_user_use_case import GetUserUseCase
from core.use_cases.users.update_user_use_case import UpdateUserUseCase
from core.use_cases.users.delete_user_use_case import DeleteUserUseCase
from core.use_cases.users.list_users_use_case import ListUsersUseCase
from core.entities.value_objects import UserRole
from core.entities.user import User

class UserService:
    """
    Servicio de aplicación para operaciones de usuario
    Orquesta use cases y proporciona una interfaz más simple para los controllers
    """
    
    def __init__(self,
                 create_user_use_case: CreateUserUseCase,
                 get_user_use_case: GetUserUseCase,
                 update_user_use_case: UpdateUserUseCase,
                 delete_user_use_case: DeleteUserUseCase,
                 list_users_use_case: ListUsersUseCase):
        
        self.create_user_use_case = create_user_use_case
        self.get_user_use_case = get_user_use_case
        self.update_user_use_case = update_user_use_case
        self.delete_user_use_case = delete_user_use_case
        self.list_users_use_case = list_users_use_case

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un nuevo usuario
        """
        try:
            # Validar y extraer datos
            username = user_data.get('username', '').strip()
            email = user_data.get('email', '').strip()
            password = user_data.get('password', '').strip()
            role_str = user_data.get('role', 'USER').upper()
            
            if not username or not email:
                return {
                    "success": False,
                    "message": "Username y email son requeridos",
                    "error": "Datos incompletos"
                }
            
            # Convertir string a UserRole
            try:
                role = UserRole[role_str]
            except KeyError:
                return {
                    "success": False,
                    "message": f"Rol inválido: {role_str}",
                    "error": f"Roles válidos: {[r.name for r in UserRole]}"
                }
            
            # Ejecutar use case
            user, message = self.create_user_use_case.execute(
                username=username,
                email=email,
                password=password,
                role=role
            )
            
            if user:
                return {
                    "success": True,
                    "data": self._user_to_dict(user),
                    "message": message
                }
            else:
                return {
                    "success": False,
                    "message": message,
                    "error": message
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": "Error interno al crear usuario",
                "error": str(e)
            }

    def get_user(self, user_id: int) -> Dict[str, Any]:
        """
        Obtiene un usuario por ID
        """
        try:
            user = self.get_user_use_case.execute(user_id)
            
            if user:
                return {
                    "success": True,
                    "data": self._user_to_dict(user),
                    "message": "Usuario encontrado"
                }
            else:
                return {
                    "success": False,
                    "message": f"Usuario con ID {user_id} no encontrado",
                    "error": "Usuario no existe"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": "Error interno al obtener usuario",
                "error": str(e)
            }

    def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """
        Busca un usuario por email
        """
        try:
            # Usamos list_users y filtramos por email
            users = self.list_users_use_case.execute()
            
            for user in users:
                if user.email.value.lower() == email.lower():
                    return {
                        "success": True,
                        "data": self._user_to_dict(user),
                        "message": "Usuario encontrado"
                    }
            
            return {
                "success": False,
                "message": f"Usuario con email {email} no encontrado",
                "error": "Usuario no existe"
            }
                
        except Exception as e:
            return {
                "success": False,
                "message": "Error interno al buscar usuario por email",
                "error": str(e)
            }

    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza un usuario existente
        """
        try:
            # Validar y extraer datos
            username = user_data.get('username', '').strip()
            email = user_data.get('email', '').strip()
            role_str = user_data.get('role', 'USER').upper()
            is_active = user_data.get('is_active', True)
            
            if not username or not email:
                return {
                    "success": False,
                    "message": "Username y email son requeridos",
                    "error": "Datos incompletos"
                }
            
            # Convertir string a UserRole
            try:
                role = UserRole[role_str]
            except KeyError:
                return {
                    "success": False,
                    "message": f"Rol inválido: {role_str}",
                    "error": f"Roles válidos: {[r.name for r in UserRole]}"
                }
            
            # Ejecutar use case
            user, message = self.update_user_use_case.execute(
                user_id=user_id,
                username=username,
                email=email,
                role=role            # type: ignore
            )
            
            if user:
                return {
                    "success": True,
                    "data": self._user_to_dict(user),
                    "message": message
                }
            else:
                return {
                    "success": False,
                    "message": message,
                    "error": message
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": "Error interno al actualizar usuario",
                "error": str(e)
            }

    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """
        Elimina un usuario
        """
        try:
            success, message = self.delete_user_use_case.execute(user_id)
            
            return {
                "success": success,
                "message": message,
                "error": None if success else message
            }
                
        except Exception as e:
            return {
                "success": False,
                "message": "Error interno al eliminar usuario",
                "error": str(e)
            }

    def list_users(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Lista todos los usuarios con filtros opcionales
        """
        try:
            users = self.list_users_use_case.execute()
            
            # Aplicar filtros si se proporcionan
            if filters:
                users = self._apply_filters(users, filters)
            
            user_dicts = [self._user_to_dict(user) for user in users]
            
            return {
                "success": True,
                "data": user_dicts,
                "message": f"Encontrados {len(user_dicts)} usuarios",
                "total": len(user_dicts)
            }
                
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": "Error interno al listar usuarios",
                "error": str(e)
            }

    def list_users_by_role(self, role: str) -> Dict[str, Any]:
        """
        Lista usuarios por rol
        """
        try:
            role_enum = UserRole[role.upper()]
            return self.list_users({'role': role_enum})
        except KeyError:
            return {
                "success": False,
                "data": [],
                "message": f"Rol inválido: {role}",
                "error": f"Roles válidos: {[r.name for r in UserRole]}"
            }

    def deactivate_user(self, user_id: int) -> Dict[str, Any]:
        """
        Desactiva un usuario (soft delete)
        """
        try:
            # Obtener usuario actual
            user_result = self.get_user(user_id)
            if not user_result['success']:
                return user_result
            
            user_data = user_result['data']
            
            # Actualizar solo el campo is_active
            return self.update_user(user_id, {
                'username': user_data['username'],
                'email': user_data['email'],
                'role': user_data['role'],
                'is_active': False
            })
                
        except Exception as e:
            return {
                "success": False,
                "message": "Error interno al desactivar usuario",
                "error": str(e)
            }

    def activate_user(self, user_id: int) -> Dict[str, Any]:
        """
        Activa un usuario previamente desactivado
        """
        try:
            # Obtener usuario actual
            user_result = self.get_user(user_id)
            if not user_result['success']:
                return user_result
            
            user_data = user_result['data']
            
            # Actualizar solo el campo is_active
            return self.update_user(user_id, {
                'username': user_data['username'],
                'email': user_data['email'],
                'role': user_data['role'],
                'is_active': True
            })
                
        except Exception as e:
            return {
                "success": False,
                "message": "Error interno al activar usuario",
                "error": str(e)
            }

    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """
        Convierte una entidad User a diccionario
        """
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email.value,
            "role": user.role.value,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "permissions": {
                "can_manage_users": user.can_manage_users(),
                "can_liquidate_diets": user.can_liquidate_diets(),
                "can_config_app": user.can_config_app()
            }
        }

    def _apply_filters(self, users: List[User], filters: Dict[str, Any]) -> List[User]:
        """
        Aplica filtros a la lista de usuarios
        """
        filtered_users = users
        
        # Filtrar por rol
        if 'role' in filters:
            filtered_users = [u for u in filtered_users if u.role == filters['role']]
        
        # Filtrar por estado activo
        if 'is_active' in filters:
            filtered_users = [u for u in filtered_users if u.is_active == filters['is_active']]
        
        # Filtrar por texto en username o email
        if 'search' in filters:
            search_term = filters['search'].lower()
            filtered_users = [
                u for u in filtered_users 
                if search_term in u.username.lower() or search_term in u.email.value.lower()
            ]
        
        return filtered_users

    def get_user_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de usuarios
        """
        try:
            users = self.list_users_use_case.execute()
            
            total_users = len(users)
            active_users = len([u for u in users if u.is_active])
            users_by_role = {}
            
            for role in UserRole:
                users_by_role[role.value] = len([u for u in users if u.role == role])
            
            return {
                "success": True,
                "data": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "inactive_users": total_users - active_users,
                    "users_by_role": users_by_role
                },
                "message": "Estadísticas obtenidas exitosamente"
            }
                
        except Exception as e:
            return {
                "success": False,
                "message": "Error interno al obtener estadísticas",
                "error": str(e)
            }