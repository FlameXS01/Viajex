class LogoutUseCase:
    # En una aplicación con sesiones, aquí se invalidaría la sesión.
    # Pero en Clean Architecture, el logout suele ser manejado por la capa de presentación.
    def execute(self, user_id: int) -> str:
        return "Logout exitoso"