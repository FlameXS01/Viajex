import hashlib
import secrets
import string
from typing import Tuple
from cryptography.fernet import Fernet
import base64

class PasswordHasher:
    """
    Servicio para el hashing y verificación de contraseñas
    Utiliza PBKDF2 con SHA256 para mayor seguridad
    """
    
    def __init__(self, iterations: int = 100000):
        self.iterations = iterations
        self.hash_algorithm = 'sha256'
        self.salt_length = 16
    
    def hash_password(self, password: str) -> str:
        """
        Hashea una contraseña usando PBKDF2 con salt aleatorio
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            str: Hash seguro en formato algorithm$iterations$salt$hash
        """
        if not password:
            raise ValueError("La contraseña no puede estar vacía")
        
        # Generar salt aleatorio
        salt = secrets.token_bytes(self.salt_length)
        
        # Hashear la contraseña con PBKDF2
        hash_bytes = hashlib.pbkdf2_hmac(
            self.hash_algorithm,
            password.encode('utf-8'),
            salt,
            self.iterations
        )
        
        # Codificar a formato almacenable
        salt_b64 = base64.b64encode(salt).decode('ascii')
        hash_b64 = base64.b64encode(hash_bytes).decode('ascii')
        
        return f"{self.hash_algorithm}${self.iterations}${salt_b64}${hash_b64}"
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verifica si una contraseña coincide con el hash almacenado
        
        Args:
            password: Contraseña en texto plano a verificar
            hashed_password: Hash almacenado en la base de datos
            
        Returns:
            bool: True si la contraseña es válida, False en caso contrario
        """
        if not password or not hashed_password:
            return False
        
        try:
            # Parsear el hash almacenado
            parts = hashed_password.split('$')
            if len(parts) != 4:
                return False
            
            algorithm, iterations_str, salt_b64, hash_b64 = parts
            
            # Convertir a los tipos correctos
            iterations = int(iterations_str)
            salt = base64.b64decode(salt_b64.encode('ascii'))
            stored_hash = base64.b64decode(hash_b64.encode('ascii'))
            
            # Hashear la contraseña proporcionada con el mismo salt
            computed_hash = hashlib.pbkdf2_hmac(
                algorithm,
                password.encode('utf-8'),
                salt,
                iterations
            )
            
            # Comparar los hashes de manera segura (timing-attack safe)
            return secrets.compare_digest(computed_hash, stored_hash)
            
        except (ValueError, TypeError, base64.binascii.Error):
            return False
    
    def generate_secure_password(self, length: int = 12) -> str:
        """
        Genera una contraseña segura automáticamente
        
        Args:
            length: Longitud de la contraseña (mínimo 8)
            
        Returns:
            str: Contraseña segura generada
        """
        if length < 8:
            raise ValueError("La longitud mínima de contraseña es 8")
        
        # Caracteres permitidos
        letters = string.ascii_letters
        digits = string.digits
        punctuation = "!@#$%&*"
        
        # Asegurar al menos un carácter de cada tipo
        password = [
            secrets.choice(letters),
            secrets.choice(digits),
            secrets.choice(punctuation)
        ]
        
        # Completar con caracteres aleatorios
        all_chars = letters + digits + punctuation
        password += [secrets.choice(all_chars) for _ in range(length - 3)]
        
        # Mezclar los caracteres
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    def is_password_strong(self, password: str) -> Tuple[bool, str]:
        """
        Valida la fortaleza de una contraseña
        
        Args:
            password: Contraseña a validar
            
        Returns:
            Tuple[bool, str]: (es_fuerte, mensaje_error)
        """
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        
        if len(password) > 128:
            return False, "La contraseña no puede tener más de 128 caracteres"
        
        # Verificar complejidad
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%&*" for c in password)
        
        if not (has_upper and has_lower):
            return False, "La contraseña debe incluir mayúsculas y minúsculas"
        
        if not has_digit:
            return False, "La contraseña debe incluir al menos un número"
        
        if not has_special:
            return False, "La contraseña debe incluir al menos un carácter especial (!@#$%&*)"
        
        # Verificar contraseñas comunes (lista básica)
        common_passwords = {
            'password', '12345678', 'qwerty', 'admin', 'welcome'
        }
        if password.lower() in common_passwords:
            return False, "La contraseña es demasiado común"
        
        return True, "Contraseña segura"
    
    def needs_rehash(self, hashed_password: str) -> bool:
        """
        Verifica si un hash necesita ser actualizado
        (por ejemplo, si cambió el número de iteraciones)
        
        Args:
            hashed_password: Hash almacenado a verificar
            
        Returns:
            bool: True si necesita re-hasheo
        """
        try:
            parts = hashed_password.split('$')
            if len(parts) != 4:
                return True
            
            algorithm, iterations_str, _, _ = parts
            
            # Verificar si el algoritmo o iteraciones cambiaron
            if algorithm != self.hash_algorithm:
                return True
            
            if int(iterations_str) != self.iterations:
                return True
            
            return False
            
        except (ValueError, IndexError):
            return True


# Ejemplo de uso (para testing)
if __name__ == "__main__":
    hasher = PasswordHasher()
    
    # Ejemplo de hashing y verificación
    password = "mi_contraseña_segura123!"
    hashed = hasher.hash_password(password)
    print(f"Hash generado: {hashed}")
    
    # Verificación
    is_valid = hasher.verify_password(password, hashed)
    print(f"Contraseña válida: {is_valid}")
    
    # Generar contraseña segura
    secure_pass = hasher.generate_secure_password()
    print(f"Contraseña segura generada: {secure_pass}")
    
    # Validar fortaleza
    is_strong, message = hasher.is_password_strong(secure_pass)
    print(f"Es fuerte: {is_strong}, Mensaje: {message}")