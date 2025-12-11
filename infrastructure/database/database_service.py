# infrastructure/database/database_service.py
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """Servicio para operaciones de base de datos SQLite"""
    
    def __init__(self, db_path: str = "dietas_app.db"):
        self.db_path = Path(db_path)
        self.backup_dir = Path("SalvasDietas")
        self._ensure_backup_dir()
       
    def _ensure_backup_dir(self):
        """Crea el directorio de backups si no existe"""
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, description: Optional[str] = None) -> Path:
        """
        Crea un backup de la base de datos
        
        Args:
            description: Descripción opcional del backup
        
        Returns:
            Path: Ruta del archivo de backup creado
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Base de datos no encontrada: {self.db_path}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        desc_part = f"_{description}" if description else ""
        backup_name = f"backup{desc_part}_{timestamp}.db"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copy2(self.db_path, backup_path)
            self._sqlite_backup(backup_path)
            
            logger.info(f"Backup creado: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            raise
    
    def _sqlite_backup(self, backup_path: Path):
        """
        Método alternativo usando SQLite backup API
        Más seguro para bases de datos en uso
        """
        try:
            source = sqlite3.connect(self.db_path)
            destination = sqlite3.connect(backup_path)
            
            with destination:
                source.backup(destination)
                
            destination.close()
            source.close()
        except sqlite3.Error as e:
            logger.warning(f"Backup SQLite falló, usando copia simple: {e}")
            shutil.copy2(self.db_path, backup_path)
    
    def restore_backup(self, backup_path: Path) -> bool:
        """
        Restaura un backup
        
        Args:
            backup_path: Ruta del archivo de backup
        
        Returns:
            bool: True si se restauró exitosamente
        """
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup no encontrado: {backup_path}")
        
        self._create_pre_restore_backup()
        
        try:
            shutil.copy2(backup_path, self.db_path)
            
            logger.info(f"Backup restaurado desde: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error restaurando backup: {e}")
            return False
    
    def _create_pre_restore_backup(self):
        """Crea un backup de la BD actual antes de restaurar"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pre_backup_path = self.backup_dir / f"pre_restore_{timestamp}.db"
        
        if self.db_path.exists():
            shutil.copy2(self.db_path, pre_backup_path)
            logger.info(f"Backup pre-restauración creado: {pre_backup_path}")
    
    def get_backup_list(self) -> List[Tuple[Path, datetime, float]]:
        """
        Obtiene lista de backups disponibles
        
        Returns:
            Lista de tuplas (path, fecha, tamaño)
        """
        backups = []
        
        for file_path in self.backup_dir.glob("backup_*.db"):
            try:
                filename = file_path.stem
                date_str = filename.split('_')[-1]  
                file_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                
                backups.append((file_path, file_date, file_path.stat().st_size))
            except (ValueError, IndexError):
               
                file_date = datetime.fromtimestamp(file_path.stat().st_mtime)
                backups.append((file_path, file_date, file_path.stat().st_size))
        
        
        backups.sort(key=lambda x: x[1], reverse=True)
        return backups
    
    def delete_backup(self, backup_path: Path) -> bool:
        """Elimina un backup específico"""
        try:
            backup_path.unlink()
            logger.info(f"Backup eliminado: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error eliminando backup: {e}")
            return False
    
    def get_database_info(self) -> dict:
        """Obtiene información de la base de datos"""
        info = {
            "path": str(self.db_path),
            "exists": self.db_path.exists(),
            "backup_dir": str(self.backup_dir),
            "backup_count": len(list(self.backup_dir.glob("*.db")))
        }
        
        if self.db_path.exists():
            stat = self.db_path.stat()
            info.update({
                "size_mb": stat.st_size / (1024 * 1024),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "created": datetime.fromtimestamp(stat.st_ctime)
            })
        
        return info
    
    def optimize_database(self) -> bool:
        """Optimiza la base de datos SQLite"""
        if not self.db_path.exists():
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            conn.execute("VACUUM")
        
            conn.execute("PRAGMA optimize")
            conn.execute("PRAGMA analysis_limit=400")
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            
            conn.close()
            logger.info("Base de datos optimizada")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error optimizando base de datos: {e}")
            return False
        
    def create_clean_database_copy(self, new_db_name: str) -> Path:
        """
        Crea una nueva base de datos copiando todo EXCEPTO:
        - DietModel (tabla 'diets')
        - DietLiquidationModel (tabla 'diet_liquidations')
        """
        try:
            import sqlite3
            import shutil
            from datetime import datetime
            
            # 1. Verificar que la base de datos original existe
            if not self.db_path.exists():
                raise FileNotFoundError(f"Base de datos no encontrada: {self.db_path}")
            
            # 2. Crear directorio para ciclos
            cycles_dir = Path("ciclos")
            cycles_dir.mkdir(exist_ok=True)
            
            # 3. Nombre del archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_db_filename = f"ciclo_{new_db_name}_{timestamp}.db"
            new_db_path = cycles_dir / new_db_filename
            
            logger.info(f"Creando nuevo ciclo: {new_db_path}")
            
            # 4. Crear copia completa
            shutil.copy2(self.db_path, new_db_path)
            
            # 5. Conectar a la nueva base de datos
            new_conn = sqlite3.connect(new_db_path)
            new_cursor = new_conn.cursor()
            
            # 6. Eliminar tablas de dietas (simplemente DROP TABLE)
            tables_to_remove = ['diets', 'diet_liquidations']
            
            for table in tables_to_remove:
                try:
                    # Verificar si la tabla existe
                    new_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                    if new_cursor.fetchone():
                        # Obtener conteo de registros antes de eliminar (para el log)
                        new_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = new_cursor.fetchone()[0]
                        logger.info(f"Eliminando {table} con {count} registros")
                        
                        # Eliminar la tabla
                        new_cursor.execute(f"DROP TABLE {table}")
                        logger.info(f"✅ Tabla {table} eliminada")
                    else:
                        logger.info(f"La tabla {table} no existe en la nueva base de datos")
                        
                except sqlite3.Error as e:
                    logger.warning(f"No se pudo eliminar la tabla {table}: {e}")
            
            # 7. Vaciar para optimizar
            new_cursor.execute("VACUUM")
            
            # 8. Verificar que las tablas fueron eliminadas
            new_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            remaining_tables = [row[0] for row in new_cursor.fetchall()]
            logger.info(f"Tablas restantes: {remaining_tables}")
            
            # 9. Contar registros en tablas importantes
            tables_to_check = ['requests', 'cards', 'department', 'users', 'diet_services']
            counts_after = {}
            
            for table in tables_to_check:
                try:
                    new_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = new_cursor.fetchone()[0]
                    counts_after[table] = count
                except sqlite3.Error:
                    counts_after[table] = 0
            
            # 10. Verificar específicamente que diets y diet_liquidaciones no existen
            diet_tables_exist = False
            for table in ['diets', 'diet_liquidations']:
                new_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if new_cursor.fetchone():
                    diet_tables_exist = True
                    logger.error(f"❌ ERROR: La tabla {table} todavía existe después de la eliminación")
            
            if diet_tables_exist:
                raise Exception("No se pudieron eliminar todas las tablas de dietas")
            
            # 11. Generar reporte
            report_content = f"""REPORTE DE NUEVO CICLO
    =========================
    Fecha creación: {datetime.now()}
    Ciclo: {new_db_name}
    Archivo: {new_db_filename}

    DATOS CONSERVADOS:
    • Solicitantes (requests): {counts_after.get('requests', 0)}
    • Tarjetas (cards): {counts_after.get('cards', 0)}
    • Departamentos (department): {counts_after.get('department', 0)}
    • Usuarios (users): {counts_after.get('users', 0)}
    • Servicios de dieta (diet_services): {counts_after.get('diet_services', 0)}

    DATOS ELIMINADOS:
    • Todas las dietas (diets): ELIMINADAS
    • Todas las liquidaciones (diet_liquidations): ELIMINADAS

    ESTADO:
    ✅ Listo para comenzar nuevo ciclo
    📊 Próxima dieta: #1 (máximo ID actual: 0)
    📊 Próxima liquidación: #1 (máximo ID actual: 0)
    """
            
            # 12. Guardar reporte
            report_path = cycles_dir / f"reporte_{new_db_name}_{timestamp}.txt"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            # 13. Commit y cerrar
            new_conn.commit()
            new_conn.close()
            
            logger.info(f"✅ Nuevo ciclo creado exitosamente: {new_db_path}")
            
            return new_db_path
            
        except Exception as e:
            logger.error(f"❌ Error creando nuevo ciclo: {e}")
            # Limpiar archivo si falló
            if 'new_db_path' in locals() and new_db_path.exists():
                try:
                    new_db_path.unlink()
                except:
                    pass
            raise