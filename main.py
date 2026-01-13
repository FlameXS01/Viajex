import tkinter as tk
from application.services.account_service import AccountService
from application.services.card_service import CardService
from application.services.card_transaction_service import CardTransactionService
from application.services.department_service import DepartmentService
from application.services.report_service import ReportService  
from core.entities import card_transaction
from core.repositories import card_transaction_repository
from core.use_cases.account import create_account_use_case
from core.use_cases.account.create_account_use_case import CreateAccountUseCase
from core.use_cases.account.delete_account_use_case import DeleteAccountUseCase
from core.use_cases.account.get_account_by_id_use_case import GetAccountByIdUseCase
from core.use_cases.account.get_account_by_number_use_case import GetAccountByNumberUseCase
from core.use_cases.account.get_all_accounts_use_case import GetAllAccountsUseCase
from core.use_cases.account.search_accounts_by_description_use_case import SearchAccountsByDescriptionUseCase
from core.use_cases.account.update_account_use_case import UpdateAccountUseCase
from core.use_cases.account.validate_account_number_use_case import ValidateAccountNumberUseCase
from core.use_cases.cards.aviable_card import GetAviableCardsUseCase
from core.use_cases.cards.discount_card import DiscountCardUseCase
from core.use_cases.cards.export_card_transactions_use_case import ExportCardTransactionsUseCase
from core.use_cases.cards.generate_daily_snapshots_use_case import GenerateDailySnapshotsUseCase
from core.use_cases.cards.get_card_balance_at_date_use_case import GetCardBalanceAtDateUseCase
from core.use_cases.cards.get_card_monthly_summary_use_case import GetCardMonthlySummaryUseCase
from core.use_cases.cards.get_card_transactions_use_case import GetCardTransactionsUseCase
from core.use_cases.cards.record_card_transaction_use_case import RecordCardTransactionUseCase
from core.use_cases.request_user.list_users_request import ListRequestUsersUseCase
from infrastructure.database.repositories.account_repository import AccountRepositoryImpl
from infrastructure.database.repositories.card_transaction_repository import CardBalanceSnapshotRepositoryImpl, CardTransactionRepositoryImpl
from infrastructure.database.repositories.department_repository import DepartmentRepositoryImpl
from infrastructure.database.repositories.diet_liquidation_repository import DietLiquidationRepositoryImpl
from infrastructure.database.repositories.diet_repository import DietRepositoryImpl
from infrastructure.database.repositories.diet_service_repository import DietServiceRepositoryImpl
from infrastructure.database.repositories.request_user_repository import RequestUserRepositoryImpl
from infrastructure.database.repositories.user_repository import UserRepositoryImpl
from infrastructure.database.session import Base, engine
from infrastructure.security.password_hasher import BCryptPasswordHasher
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from infrastructure.database.session import Base, engine
from infrastructure.database.repositories.user_repository import UserRepositoryImpl
from infrastructure.security.password_hasher import BCryptPasswordHasher

# Use Cases System user
from core.use_cases.users.create_user import CreateUserUseCase
from core.use_cases.users.update_user import UpdateUserUseCase
from core.use_cases.users.update_user_role import UpdateUserRoleUseCase
from core.use_cases.users.update_user_password import UpdateUserPasswordUseCase
from core.use_cases.users.toggle_user_active import ToggleUserActiveUseCase
from core.use_cases.users.delete_user import DeleteUserUseCase
from core.use_cases.auth.login import LoginUseCase

# Use Cases Department 
from core.use_cases.department.create_department import CreateDepartmentUseCase
from core.use_cases.department.update_department import UpdateDepartmentUseCase
from core.use_cases.department.get_department import GetDepartmentUseCase
from core.use_cases.department.delete_department import DeleteDepartmentUseCase
from core.use_cases.department.list_department import ListDepartmentUseCase

# Use Cases rSolicitant 
from core.use_cases.request_user.create_request_user import CreateRequestUserUseCase
from core.use_cases.request_user.update_user_request import UpdateRequestUserUseCase
from core.use_cases.request_user.get_request_user import GetRequestUserUseCase
from core.use_cases.request_user.delete_request_user import DeleteRequestUserUseCase
from core.use_cases.request_user.list_users_request import ListRequestUsersUseCase

# Use Cases Card 
from core.use_cases.cards.create_card import CreateCardUseCase
from core.use_cases.cards.delete_card import DeleteCardUseCase
from core.use_cases.cards.get_all_cards import GetAllCardsUseCase
from core.use_cases.cards.get_card_by_number import GetCardByNumberUseCase
from core.use_cases.cards.get_card_use_case import GetCardByIdUseCase
from core.use_cases.cards.toggle_card_active import ToggleCardActiveUseCase
from core.use_cases.cards.update_card import UpdateCardUseCase
from core.use_cases.cards.recharged_card import RechargeCardUseCase

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
from infrastructure.database.repositories.card_repository import CardRepositoryImpl




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
        account_repository = AccountRepositoryImpl(db_session)
        card_repository= CardRepositoryImpl(db_session)
        card_transaction_repository = CardTransactionRepositoryImpl(db_session)
        card_balance_snapshot_repository = CardBalanceSnapshotRepositoryImpl(db_session)

        diet_liquidation_repository = DietLiquidationRepositoryImpl(db_session)
        diet_repository = DietRepositoryImpl(db_session)
        diet_service_repository = DietServiceRepositoryImpl(db_session)
        
        # Inicializar casos de uso de usuarios
        create_user_use_case = CreateUserUseCase(user_repository, password_hasher)
        update_user_use_case = UpdateUserUseCase(user_repository)
        update_user_role_use_case = UpdateUserRoleUseCase(user_repository)
        update_user_password_use_case = UpdateUserPasswordUseCase(user_repository, password_hasher)
        toggle_user_active_use_case = ToggleUserActiveUseCase(user_repository)
        delete_user_use_case = DeleteUserUseCase(user_repository)

        # Inicializar casos de uso de solicitantes
        create_request_user = CreateRequestUserUseCase(request_user_repository)
        update_user_request = UpdateRequestUserUseCase(request_user_repository)
        get_request_user = GetRequestUserUseCase(request_user_repository)
        delete_request_user = DeleteRequestUserUseCase(request_user_repository)
        get_request_user_list = ListRequestUsersUseCase(request_user_repository)

        # Inicializar casos de uso de department
        create_department = CreateDepartmentUseCase(department_repository)
        update_department = UpdateDepartmentUseCase(department_repository)
        get_department = GetDepartmentUseCase(department_repository)
        delete_department = DeleteDepartmentUseCase(department_repository)
        get_department_list = ListDepartmentUseCase(department_repository)

        # Inicializar casos de uso de Card
        create_card_use_case = CreateCardUseCase(card_repository)
        delete_card_use_case = DeleteCardUseCase(card_repository)
        update_card_use_case = UpdateCardUseCase(card_repository)
        get_card_by_id_use_case = GetCardByIdUseCase(card_repository)
        get_all_cards_use_case = GetAllCardsUseCase(card_repository)
        toggle_card_active_use_case = ToggleCardActiveUseCase(card_repository)
        get_card_by_number_use_case = GetCardByNumberUseCase(card_repository)
        recharge_card_use_case = RechargeCardUseCase(card_repository, card_transaction_repository)
        discount_card_use_case = DiscountCardUseCase(card_repository, card_transaction_repository)
        get_aviable_cards_use_case = GetAviableCardsUseCase(card_repository)

        get_card_transactions_use_case = GetCardTransactionsUseCase(card_transaction_repository, card_repository)
        get_card_balance_at_date_use_case = GetCardBalanceAtDateUseCase(card_transaction_repository, card_repository)
        get_card_monthly_summary_use_case = GetCardMonthlySummaryUseCase(card_balance_snapshot_repository, card_transaction_repository, card_repository)
        export_card_transactions_use_case = ExportCardTransactionsUseCase(card_transaction_repository, card_repository)
        generate_daily_snapshots_use_case = GenerateDailySnapshotsUseCase(card_transaction_repository, card_balance_snapshot_repository, card_repository)
        record_card_transaction_use_case = RecordCardTransactionUseCase(card_transaction_repository, card_repository)

        # Inicializar casos de uso de Account
        create_account_use_case = CreateAccountUseCase(account_repository)
        delete_account_use_case = DeleteAccountUseCase(account_repository)
        update_account_use_case = UpdateAccountUseCase(account_repository)
        get_account_by_id_use_case = GetAccountByIdUseCase(account_repository)
        get_all_accounts_use_case = GetAllAccountsUseCase(account_repository)
        get_account_by_number_use_case = GetAccountByNumberUseCase(account_repository)
        search_accounts_by_description_use_case = SearchAccountsByDescriptionUseCase(account_repository)
        validate_account_number_use_case = ValidateAccountNumberUseCase(account_repository)


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

        # Inicializar servicio de dietas
        diet_service = DietAppService(
            diet_liquidation_repository=diet_liquidation_repository,
            diet_service_repository = diet_service_repository,
            diet_repository = diet_repository,
            request_user_repository = request_user_repository,
        )

        # Inicializar servicio de cards
        card_service = CardService(
            create_card_use_case = create_card_use_case,
            delete_card_use_case = delete_card_use_case,
            update_card_use_case = update_card_use_case,
            get_card_by_id_use_case = get_card_by_id_use_case,
            get_all_cards_use_case = get_all_cards_use_case,
            get_aviable_cards_use_case = get_aviable_cards_use_case,
            toggle_card_active_use_case = toggle_card_active_use_case,
            recharge_card_use_case = recharge_card_use_case,
            discount_card_use_case = discount_card_use_case,
            get_card_by_number_use_case = get_card_by_number_use_case
        )

        card_transaction = CardTransactionService(
            get_card_transactions_use_case = get_card_transactions_use_case,
            get_card_balance_at_date_use_case = get_card_balance_at_date_use_case,
            get_card_monthly_summary_use_case = get_card_monthly_summary_use_case,
            export_card_transactions_use_case = export_card_transactions_use_case,
            generate_daily_snapshots_use_case = generate_daily_snapshots_use_case, 
            record_card_transaction_use_case = record_card_transaction_use_case
        )

         # Inicializar servicio de usuarios
        account_service = AccountService(
            create_account_use_case = create_account_use_case,
            delete_account_use_case = delete_account_use_case,
            update_account_use_case = update_account_use_case,
            get_account_by_id_use_case = get_account_by_id_use_case,
            get_all_accounts_use_case = get_all_accounts_use_case,
            get_account_by_number_use_case = get_account_by_number_use_case,
            search_accounts_by_description_use_case = search_accounts_by_description_use_case,
            validate_account_number_use_case = validate_account_number_use_case
        )

        report_service = ReportService(
            card_repo = card_repository,
            diet_repo = diet_repository,
            request_user_repo = request_user_repository,
            department_repo = department_repository,
            liquidation_repo = diet_liquidation_repository
        )

        # # Crear usuario admin por defecto
        initialize_admin_user(user_service)
        

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
                card_service,
                diet_service,
                account_service, 
                card_transaction,
                report_service=report_service
                )
            dashboard.run()

        # Ciclo principal de la aplicación
        while True:
            # Mostrar ventana de login
            login_window = LoginWindow(auth_service, on_login_success)
            login_window.run()
            
            # Después de cerrar el dashboard, preguntar si quiere salir completamente
            if not auth_service.is_authenticated():
                response = tk.messagebox.askyesno(                      # type: ignore
                    "Salir", 
                    "¿Desea salir completamente de la aplicación?"
                )
                if response:
                    break

    except Exception as e:
        print(f"Error crítico en la aplicación: {e}")
        tk.messagebox.showerror("Error", f"Error crítico: {e}")         # type: ignore
    finally:
        db_session.close()

if __name__ == "__main__":
    main()