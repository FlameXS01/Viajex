"""
Módulo de diálogos para reportes del sistema VIAJEX.
Contiene todos los diálogos necesarios para configurar y generar reportes.
"""

from .base_report_dialog import BaseReportDialog
from .date_range_dialog import DateRangeDialog
from .cards_in_cash_dialog import CardsInCashDialog
from .accounts_report_dialog import AccountsReportDialog
from .cost_center_dialog import CostCenterDialog
from .cards_in_advance_dialog import CardsInAdvanceDialog
from .unsettled_advances_dialog import UnsettledAdvancesDialog
from .accounting_voucher_dialog import AccountingVoucherDialog
from .daily_results_dialog import DailyResultsDialog
from .employee_report_dialog import EmployeeReportDialog
from .department_report_dialog import DepartmentReportDialog
from .export_options_dialog import ExportOptionsDialog
from .report_preview_dialog import ReportPreviewDialog
from .email_report_dialog import EmailReportDialog
from .filter_manager_dialog import FilterManagerDialog

__all__ = [
    'BaseReportDialog',
    'DateRangeDialog',
    'CardsInCashDialog',
    'AccountsReportDialog',
    'CostCenterDialog',
    'CardsInAdvanceDialog',
    'UnsettledAdvancesDialog',
    'AccountingVoucherDialog',
    'DailyResultsDialog',
    'EmployeeReportDialog',
    'DepartmentReportDialog',
    'ExportOptionsDialog',
    'ReportPreviewDialog',
    'EmailReportDialog',
    'FilterManagerDialog'
]

__version__ = '1.0.0'
__author__ = 'Equipo VIAJEX'
__description__ = 'Diálogos para configuración y generación de reportes'