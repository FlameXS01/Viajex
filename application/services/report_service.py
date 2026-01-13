# application/services/report_service.py
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from application.services.diet_service import DietAppService
from core.entities.cards import Card
from core.entities.diet import Diet
from core.entities.diet_liquidation import DietLiquidation
from core.entities.request_user import RequestUser
from core.entities.department import Department
from infrastructure.database.repositories.card_repository import CardRepository
from infrastructure.database.repositories.diet_repository import DietRepository
from infrastructure.database.repositories.request_user_repository import RequestUserRepository
from infrastructure.database.repositories.department_repository import DepartmentRepository
from infrastructure.database.repositories.diet_liquidation_repository import DietLiquidationRepository


class ReportService:
    """Servicio para generar reportes del sistema"""
    
    def __init__(self, card_repo, diet_repo, request_user_repo, department_repo, liquidation_repo, diet_service):
        self.card_repo = card_repo
        self.diet_repo = diet_repo
        self.request_user_repo = request_user_repo
        self.department_repo = department_repo
        self.liquidation_repo = liquidation_repo
        self.diet_service = diet_service
    
    def get_all_cards_report(self) -> list[dict[str, Any]]:
        """Obtiene todos los datos de tarjetas para el reporte"""
        cards = self.card_repo.get_all()
        
        report_data = []
        for card in cards:
            # Determinar estado basado en is_active y with_money
            estado = "Activa"
            if not card.is_active:
                estado = "Inactiva"

            
            report_data.append({
                "numero_tarjeta": card.card_number,
                "pin": card.card_pin,  # Nota: Esto podría estar hasheado
                "balance": f"${card.balance:.2f}" if card.balance is not None else "$0.00",
                "estado": estado,
                "raw_balance": card.balance or 0.0,
                "is_active": card.is_active
            })
        
        return report_data
    
    def get_all_diets_report(self) -> list[dict[str, Any]]:
        """Obtiene todos los datos de dietas para el reporte consolidado"""
        diets = self.diet_repo.get_all()
        
        report_data = []
        for diet in diets:
            # Obtener información del solicitante
            request_user = self.request_user_repo.get_by_id(diet.request_user_id)
            
            # Obtener departamento
            department_name = "N/A"
            if request_user and request_user.department_id:
                department = self.department_repo.get_by_id(request_user.department_id)
                department_name = department.name if department else "N/A"
            
            diet_service = self.diet_service.get_by_local(diet.is_local)

            # Obtener liquidación si existe
            liquidation = self.liquidation_repo.get_by_diet_id(diet.id)
            
            # Calcular montos
            monto_solicitado = self._calculate_diet_amount(diet, diet_service)
            gasto_liquidado = self._calculate_liquidation_amount(liquidation, diet_service)
            
            # Formatear fechas
            fecha_solicitud = diet.created_at.strftime("%d/%m/%Y") if diet.created_at else "N/A"
            fecha_liquidacion = liquidation.liquidation_date.strftime("%d/%m/%Y") if liquidation and liquidation.liquidation_date else "N/A"
            

            report_data.append({
                "no_anticipo": diet.advance_number,
                "no_liquidacion": liquidation.liquidation_number if liquidation else "N/A",
                "descripcion": diet.description or "",
                "solicitante": request_user.fullname if request_user else "N/A",
                "departamento": department_name,
                "fecha_inicio": diet.start_date.strftime("%d/%m/%Y") if diet.start_date else "N/A",
                "fecha_fin": diet.end_date.strftime("%d/%m/%Y") if diet.end_date else "N/A",
                "fecha_solicitud": fecha_solicitud,
                "fecha_liquidacion": fecha_liquidacion,
                "monto_solicitado_efec": f"${monto_solicitado[0]:.2f}",
                "monto_solicitado_card": f"${monto_solicitado[1]:.2f}",
                "gasto_efec": f"${gasto_liquidado[0]:.2f}" if liquidation else "$0.00",
                "gasto_card": f"${gasto_liquidado[1]:.2f}" if liquidation else "$0.00",
                "raw_monto_solicitado": monto_solicitado[0] + monto_solicitado[1],
                "raw_gasto": gasto_liquidado[0] + gasto_liquidado[1],
                "estado": diet.status.upper() if hasattr(diet, 'status') else "N/A"
            })
        
        return report_data
    
    # En ambos calcular la primera pos de la lista es el efectivo y en la segunda en tarjeta
    def _calculate_diet_amount(self, diet: Diet, diet_service) -> list[float]:
        """Calcula el monto total solicitado de una dieta"""
        # Obtener servicio de dieta para los precios
        if not diet_service:
            return [0.0,0.0] 
        
        # Calcular montos basados en precios y cantidades
        breakfast_total = diet.breakfast_count * diet_service.breakfast_price
        lunch_total = diet.lunch_count * diet_service.lunch_price
        dinner_total = diet.dinner_count * diet_service.dinner_price
        
        efective = breakfast_total + lunch_total + dinner_total
        
        # Precio de alojamiento según método de pago
        if diet.accommodation_payment_method.upper() == "CARD":
            accommodation_total = diet.accommodation_count * diet_service.accommodation_card_price
            return [efective, accommodation_total]
        else:
            accommodation_total = diet.accommodation_count * diet_service.accommodation_cash_price
            return [efective + accommodation_total, 0.0]

    def _calculate_liquidation_amount(self, liquidation: DietLiquidation, diet_service) -> list[float]:
        """Calcula el monto total liquidado"""
        
        if not liquidation:
            return [0.0 , 0.0]

        if not diet_service:
            return [0.0 , 0.0]

        # Calcular montos basados en precios y cantidades liquidadas
        breakfast_total = liquidation.breakfast_count_liquidated * diet_service.breakfast_price
        lunch_total = liquidation.lunch_count_liquidated * diet_service.lunch_price
        dinner_total = liquidation.dinner_count_liquidated * diet_service.dinner_price
        
        efective = breakfast_total + lunch_total + dinner_total

        # Precio de alojamiento según método de pago
        if liquidation.accommodation_payment_method.upper() == "CARD":
            if hasattr(liquidation, 'total_pay') and liquidation.total_pay:
                accommodation_total = liquidation.total_pay
            else:
                accommodation_total = liquidation.accommodation_count_liquidated * diet_service.accommodation_card_price
            return [efective, accommodation_total]
        else:
            accommodation_total = liquidation.accommodation_count_liquidated * diet_service.accommodation_cash_price
            return [efective + accommodation_total, 0.0]
         
    def filter_cards_report(self, filters: Dict[str, str]) -> List[Dict[str, Any]]:
        """Filtra el reporte de tarjetas"""
        all_cards = self.get_all_cards_report()
        
        if not filters:
            return all_cards
        
        filtered_data = []
        for card in all_cards:
            match = True
            for key, value in filters.items():
                if value and key in card:
                    card_value = str(card[key]).lower()
                    if value.lower() not in card_value:
                        match = False
                        break
            
            if match:
                filtered_data.append(card)
        
        return filtered_data
    
    def filter_diets_report(self, filters: Dict[str, str]) -> List[Dict[str, Any]]:
        """Filtra el reporte de dietas"""
        all_diets = self.get_all_diets_report()
        
        if not filters:
            return all_diets
        
        filtered_data = []
        for diet in all_diets:
            match = True
            for key, value in filters.items():
                if value and key in diet:
                    diet_value = str(diet[key]).lower()
                    if value.lower() not in diet_value:
                        match = False
                        break
            
            if match:
                filtered_data.append(diet)
        
        return filtered_data