import csv
import json
import os
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from core.repositories.card_transaction_repository import CardTransactionRepository
from core.repositories.card_repository import CardRepository
import logging

logger = logging.getLogger(__name__)


class ExportCardTransactionsUseCase:
    """
    Caso de uso para exportar transacciones a diferentes formatos.
    
    Soporta CSV, Excel y JSON.
    """
    
    def __init__(
        self, 
        card_transaction_repository: CardTransactionRepository,
        card_repository: CardRepository
    ):
        self.card_transaction_repository = card_transaction_repository
        self.card_repository = card_repository
    
    def execute(
        self,
        card_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        export_format: str = "csv",
        output_dir: Optional[str] = None,
        include_summary: bool = True
    ) -> str:
        """
        Exporta transacciones a un archivo.
        
        Args:
            card_id: ID de la tarjeta
            start_date: Fecha inicial del filtro
            end_date: Fecha final del filtro
            export_format: Formato de exportación (csv, json, excel)
            output_dir: Directorio de salida (default: directorio actual)
            include_summary: Incluir resumen estadístico
            
        Returns:
            str: Ruta del archivo generado
            
        Raises:
            ValueError: Si las validaciones fallan
        """
        # Validaciones
        if not card_id or card_id <= 0:
            raise ValueError("El ID de la tarjeta debe ser un número positivo")
        
        if export_format not in ['csv', 'json', 'excel']:
            raise ValueError("Formato de exportación no soportado. Use: csv, json, excel")
        
        # Verificar que la tarjeta existe
        card = self.card_repository.get_by_id(card_id)
        if not card:
            raise ValueError(f"Tarjeta con ID {card_id} no encontrada")
        
        # Obtener transacciones
        transactions = self.card_transaction_repository.get_by_card_id(
            card_id=card_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if not transactions:
            raise ValueError("No hay transacciones para exportar en el período especificado")
        
        # Crear directorio si no existe
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transacciones_tarjeta_{card.card_number}_{timestamp}.{export_format}"
        
        if output_dir:
            filepath = os.path.join(output_dir, filename)
        else:
            filepath = filename
        
        # Exportar según formato
        if export_format == 'csv':
            self._export_to_csv(filepath, card, transactions, start_date, end_date, include_summary)
        elif export_format == 'json':
            self._export_to_json(filepath, card, transactions, start_date, end_date, include_summary)
        elif export_format == 'excel':
            self._export_to_excel(filepath, card, transactions, start_date, end_date, include_summary)
        
        logger.info(f"Transacciones exportadas exitosamente: {filepath}")
        
        return filepath
    
    def _export_to_csv(
        self, 
        filepath: str, 
        card,
        transactions: List,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        include_summary: bool
    ):
        """Exporta transacciones a CSV."""
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            # Encabezado informativo
            writer.writerow(['REPORTE DE TRANSACCIONES DE TARJETA'])
            writer.writerow([''])
            writer.writerow(['Tarjeta:', card.card_number])
            writer.writerow(['Período:', 
                           start_date.strftime("%d/%m/%Y %H:%M") if start_date else 'Inicio', 
                           'a',
                           end_date.strftime("%d/%m/%Y %H:%M") if end_date else 'Actual'])
            writer.writerow(['Fecha de exportación:', datetime.now().strftime("%d/%m/%Y %H:%M:%S")])
            writer.writerow([''])
            
            # Encabezados de datos
            writer.writerow([
                'Fecha Operación', 'Tipo', 'Monto', 'Saldo Anterior', 
                'Nuevo Saldo', 'Descripción', 'Referencia'
            ])
            
            # Datos
            total_credits = Decimal('0')
            total_debits = Decimal('0')
            
            for t in transactions:
                # Determinar tipo de referencia
                reference = ''
                if t.diet_id:
                    reference = f"Dieta #{t.diet_id}"
                elif t.liquidation_id:
                    reference = f"Liquidación #{t.liquidation_id}"
                
                writer.writerow([
                    t.operation_date.strftime("%d/%m/%Y %H:%M"),
                    t.transaction_type,
                    f"{t.amount:,.2f}",
                    f"{t.previous_balance:,.2f}",
                    f"{t.new_balance:,.2f}",
                    t.notes or '',
                    reference
                ])
                
                # Acumular totales
                if t.amount > 0:
                    total_credits += t.amount
                else:
                    total_debits += abs(t.amount)
            
            writer.writerow([''])
            
            if include_summary:
                # Resumen
                writer.writerow(['RESUMEN DEL PERÍODO'])
                writer.writerow(['Total transacciones:', len(transactions)])
                writer.writerow(['Total créditos:', f"{total_credits:,.2f}"])
                writer.writerow(['Total débitos:', f"{total_debits:,.2f}"])
                writer.writerow(['Movimiento neto:', f"{(total_credits - total_debits):,.2f}"])
                
                # Balance inicial y final
                if transactions:
                    initial_balance = transactions[-1].previous_balance if transactions else Decimal('0')
                    final_balance = transactions[0].new_balance if transactions else Decimal('0')
                    
                    writer.writerow([''])
                    writer.writerow(['Balance inicial:', f"{initial_balance:,.2f}"])
                    writer.writerow(['Balance final:', f"{final_balance:,.2f}"])
    
    def _export_to_json(
        self, 
        filepath: str, 
        card,
        transactions: List,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        include_summary: bool
    ):
        """Exporta transacciones a JSON."""
        export_data = {
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'card': {
                    'id': card.card_id,
                    'number': card.card_number,
                    'current_balance': float(card.balance) if card.balance else 0.0
                },
                'period': {
                    'start': start_date.isoformat() if start_date else None,
                    'end': end_date.isoformat() if end_date else None
                }
            },
            'transactions': []
        }
        
        total_credits = Decimal('0')
        total_debits = Decimal('0')
        
        for t in transactions:
            transaction_data = {
                'id': t.id,
                'operation_date': t.operation_date.isoformat(),
                'transaction_type': t.transaction_type,
                'amount': float(t.amount),
                'previous_balance': float(t.previous_balance),
                'new_balance': float(t.new_balance),
                'description': t.notes,
                'reference_type': 'diet' if t.diet_id else 'liquidation' if t.liquidation_id else None,
                'reference_id': t.diet_id or t.liquidation_id
            }
            export_data['transactions'].append(transaction_data)
            
            if t.amount > 0:
                total_credits += t.amount
            else:
                total_debits += abs(t.amount)
        
        if include_summary:
            export_data['summary'] = {
                'transaction_count': len(transactions),
                'total_credits': float(total_credits),
                'total_debits': float(total_debits),
                'net_movement': float(total_credits - total_debits)
            }
            
            if transactions:
                export_data['summary']['opening_balance'] = float(transactions[-1].previous_balance)
                export_data['summary']['closing_balance'] = float(transactions[0].new_balance)
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, ensure_ascii=False, indent=2, default=str)
    
    def _export_to_excel(
        self, 
        filepath: str, 
        card,
        transactions: List,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        include_summary: bool
    ):
        """Exporta transacciones a Excel (requiere pandas)."""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "Para exportar a Excel, instale pandas: pip install pandas openpyxl"
            )
        
        # Preparar datos
        data = []
        for t in transactions:
            data.append({
                'Fecha Operación': t.operation_date,
                'Tipo': t.transaction_type,
                'Monto': float(t.amount),
                'Saldo Anterior': float(t.previous_balance),
                'Nuevo Saldo': float(t.new_balance),
                'Descripción': t.notes or '',
                'Referencia': f"Dieta #{t.diet_id}" if t.diet_id else 
                             f"Liquidación #{t.liquidation_id}" if t.liquidation_id else ''
            })
        
        # Crear DataFrame
        df = pd.DataFrame(data)
        
        # Crear writer de Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Hoja de transacciones
            df.to_excel(writer, sheet_name='Transacciones', index=False)
            
            if include_summary:
                # Hoja de resumen
                summary_data = {
                    'Métrica': ['Total Transacciones', 'Total Créditos', 'Total Débitos', 
                               'Movimiento Neto', 'Balance Inicial', 'Balance Final'],
                    'Valor': [
                        len(transactions),
                        float(sum(t.amount for t in transactions if t.amount > 0)),
                        float(abs(sum(t.amount for t in transactions if t.amount < 0))),
                        float(sum(t.amount for t in transactions)),
                        float(transactions[-1].previous_balance) if transactions else 0.0,
                        float(transactions[0].new_balance) if transactions else 0.0
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Resumen', index=False)
            
            # Ajustar anchos de columna
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width