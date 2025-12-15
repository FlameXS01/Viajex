# infrastructure/database/database_service.py
import os
import shutil
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseService:
    """Servicio para operaciones de base de datos SQLite optimizado"""
    
    def __init__(self, db_path: str = "dietas_app.db"):
        self.db_path = Path(db_path).resolve()
        self.backup_dir = Path("SalvasDietas").resolve()
        self.cycles_dir = Path("ciclos").resolve()
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Crea los directorios necesarios si no existen"""
        self.backup_dir.mkdir(exist_ok=True)
        self.cycles_dir.mkdir(exist_ok=True)
    
    @contextmanager
    def _db_connection(self, path: Optional[Path] = None):
        """Context manager para conexiones a la base de datos"""
        conn = None
        try:
            conn = sqlite3.connect(path or self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
        finally:
            if conn:
                conn.close()
    
    def _get_timestamp(self) -> str:
        """Devuelve timestamp formateado para nombres de archivo"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _format_filename(self, prefix: str, description: str = "", 
                        extension: str = ".db") -> str:
        """Formatea nombres de archivo consistentemente"""
        timestamp = self._get_timestamp()
        desc = f"_{description}" if description else ""
        return f"{prefix}{desc}_{timestamp}{extension}"
    
    def create_backup(self, description: Optional[str] = None) -> Path:
        """
        Crea un backup de la base de datos usando el método más seguro
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Base de datos no encontrada: {self.db_path}")
        
        filename = self._format_filename("backup", description or "manual")
        backup_path = self.backup_dir / filename
        
        try:
            # Usar el método de backup nativo de SQLite para mayor seguridad
            with self._db_connection() as source, self._db_connection(backup_path) as dest:
                source.backup(dest)
            
            logger.info(f"Backup creado exitosamente: {backup_path}")
            return backup_path
            
        except sqlite3.Error as e:
            logger.error(f"Error en backup SQLite: {e}")
            # Fallback a copia de archivo
            try:
                shutil.copy2(self.db_path, backup_path)
                logger.info(f"Backup creado (fallback): {backup_path}")
                return backup_path
            except Exception as copy_error:
                logger.error(f"Error en backup fallback: {copy_error}")
                raise
    
    def restore_backup(self, backup_path: Path) -> bool:
        """
        Restaura un backup con bloqueo de la aplicación
        """
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup no encontrado: {backup_path}")
        
        # Crear backup de seguridad antes de restaurar
        pre_restore_backup = self.create_backup("pre_restore")
        logger.info(f"Backup de seguridad creado: {pre_restore_backup}")
        
        try:
            # Bloquear la base de datos actual
            lock_file = self.db_path.with_suffix('.db.lock')
            lock_file.touch(exist_ok=True)
            
            # Restaurar desde el backup
            with self._db_connection(backup_path) as source, self._db_connection() as dest:
                source.backup(dest)
            
            # Crear archivo de requerimiento de reinicio
            restart_file = Path("REINICIAR_APP.txt")
            restart_file.write_text(
                f"La base de datos ha sido restaurada desde: {backup_path.name}\n"
                f"Fecha: {datetime.now()}\n"
                f"Backup de seguridad: {pre_restore_backup.name}\n"
                "Por favor, cierre y reinicie la aplicación."
            )
            
            logger.info(f"Backup restaurado desde: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error restaurando backup: {e}")
            # Intentar restaurar desde el backup de seguridad
            try:
                if pre_restore_backup.exists():
                    shutil.copy2(pre_restore_backup, self.db_path)
                    logger.info("Restaurado desde backup de seguridad")
            except Exception as restore_error:
                logger.error(f"Error crítico: {restore_error}")
            return False
        finally:
            if 'lock_file' in locals() and lock_file.exists():
                lock_file.unlink()
    
    # def create_clean_database_copy(self, ciclo_nombre: str) -> Path:
    #     """
    #     Crea una nueva base de datos limpia para nuevo ciclo
    #     y la trata como un backup automático
    #     """
    #     if not self.db_path.exists():
    #         raise FileNotFoundError(f"Base de datos no encontrada: {self.db_path}")
        
    #     # Crear backup automático antes de comenzar
    #     auto_backup = self.create_backup(f"pre_ciclo_{ciclo_nombre}")
    #     logger.info(f"Backup automático creado: {auto_backup}")
        
    #     # Nombre del nuevo ciclo (en carpeta de backups)
    #     filename = self._format_filename("ciclo", ciclo_nombre)
    #     new_db_path = self.backup_dir / filename
        
    #     try:
    #         # 1. Copiar la base de datos completa
    #         shutil.copy2(self.db_path, new_db_path)
            
    #         # 2. Eliminar tablas específicas
    #         tables_to_remove = ['diets', 'diet_liquidations']
            
    #         with self._db_connection(new_db_path) as conn:
    #             cursor = conn.cursor()
                
    #             for table in tables_to_remove:
    #                 cursor.execute(
    #                     "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
    #                     (table,)
    #                 )
    #                 if cursor.fetchone():
    #                     cursor.execute(f"DROP TABLE {table}")
    #                     logger.info(f"Tabla {table} eliminada")
                
    #             # 3. Resetear secuencias de autoincremento para las tablas eliminadas
    #             cursor.execute("VACUUM")
                
    #             # 4. Verificar eliminación
    #             cursor.execute("""
    #                 SELECT name FROM sqlite_master 
    #                 WHERE type='table' 
    #                 AND name IN ('diets', 'diet_liquidations')
    #             """)
    #             remaining = cursor.fetchall()
    #             if remaining:
    #                 raise Exception(f"Tablas no eliminadas: {remaining}")
                
    #             conn.commit()
            
    #         # 5. Crear reporte detallado
    #         report = self._generate_cycle_report(ciclo_nombre, new_db_path)
    #         report_path = self.cycles_dir / f"reporte_{ciclo_nombre}_{self._get_timestamp()}.txt"
    #         report_path.write_text(report, encoding='utf-8')
            
    #         # 6. Restaurar automáticamente este nuevo ciclo
    #         self.restore_backup(new_db_path)
            
    #         logger.info(f"Nuevo ciclo creado y restaurado: {new_db_path}")
    #         return new_db_path
            
    #     except Exception as e:
    #         logger.error(f"Error creando nuevo ciclo: {e}")
    #         # Limpieza en caso de error
    #         if new_db_path.exists():
    #             try:
    #                 new_db_path.unlink()
    #             except:
    #                 pass
    #         raise
    
    def _generate_cycle_report(self, ciclo_nombre: str, db_path: Path) -> str:
        """Genera reporte detallado del nuevo ciclo"""
        with self._db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Contar registros en tablas importantes
            tables = ['requests', 'cards', 'department', 'users', 'diet_services']
            counts = {}
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    counts[table] = cursor.fetchone()[0]
                except sqlite3.Error:
                    counts[table] = 0
            
            # Obtener próximos IDs disponibles
            cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM diets")
            next_diet_id = cursor.fetchone()[0]
            
            cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM diet_liquidations")
            next_liquidation_id = cursor.fetchone()[0]
            
            report = f"""REPORTE DE NUEVO CICLO
=========================
Fecha creación: {datetime.now()}
Ciclo: {ciclo_nombre}
Archivo: {db_path.name}

DATOS CONSERVADOS:
• Solicitantes (requests): {counts.get('requests', 0)}
• Tarjetas (cards): {counts.get('cards', 0)}
• Departamentos (department): {counts.get('department', 0)}
• Usuarios (users): {counts.get('users', 0)}
• Servicios de dieta (diet_services): {counts.get('diet_services', 0)}

DATOS ELIMINADOS:
• Todas las dietas (diets): ELIMINADAS
• Todas las liquidaciones (diet_liquidations): ELIMINADAS

PRÓXIMAS NUMERACIONES:
• Próxima dieta: #{next_diet_id}
• Próxima liquidación: #{next_liquidation_id}

ESTADO:
✅ Nuevo ciclo listo para uso
📊 Base de datos optimizada
🔒 Backup automático creado

NOTA: La aplicación debe ser reiniciada para comenzar con el nuevo ciclo.
"""
            return report
    
    def get_backup_list(self) -> List[Tuple[Path, datetime, float]]:
        """
        Obtiene lista de backups disponibles ordenados
        """
        backups = []
        
        for file_path in self.backup_dir.glob("*.db"):
            try:
                stat = file_path.stat()
                file_date = datetime.fromtimestamp(stat.st_mtime)
                
                # Extraer descripción del nombre si existe
                name_parts = file_path.stem.split('_')
                if len(name_parts) > 1 and name_parts[0] in ['backup', 'ciclo']:
                    backups.append((file_path, file_date, stat.st_size))
                    
            except Exception as e:
                logger.warning(f"Error procesando backup {file_path}: {e}")
        
        # Ordenar por fecha descendente
        backups.sort(key=lambda x: x[1], reverse=True)
        return backups
    
    def optimize_database(self) -> bool:
        """Optimiza la base de datos de forma segura"""
        if not self.db_path.exists():
            return False
        
        try:
            with self._db_connection() as conn:
                # Ejecutar optimizaciones en transacción
                conn.execute("BEGIN IMMEDIATE")
                conn.execute("VACUUM")
                conn.execute("PRAGMA optimize")
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                conn.commit()
            
            logger.info("Base de datos optimizada exitosamente")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error optimizando base de datos: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Obtiene información detallada de la base de datos"""
        info = {
            "path": str(self.db_path),
            "exists": self.db_path.exists(),
            "backup_dir": str(self.backup_dir),
            "backup_count": len(list(self.backup_dir.glob("*.db"))),
            "cycles_count": len(list(self.cycles_dir.glob("*.txt")))
        }
        
        if self.db_path.exists():
            stat = self.db_path.stat()
            info.update({
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "created": datetime.fromtimestamp(stat.st_ctime)
            })
            
            # Información de tablas
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                info["tables"] = tables
                info["table_count"] = len(tables)
        
        return info
    
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
            path = shutil.copy2(self.db_path, new_db_path)
            
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
            
            self.restore_backup(Path(path))

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