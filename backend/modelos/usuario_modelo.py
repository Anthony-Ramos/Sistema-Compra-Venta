"""Modelo de Usuario: registro y autenticación con bcrypt."""

from dataclasses import dataclass
from typing import Optional, Tuple
import bcrypt
from backend.db import DB


@dataclass
class Usuario:
    """Entidad Usuario vinculada a la tabla 'usuarios'."""
    id_usuario: int
    nom_usuario: str
    contrasena_hash: str
    id_rol: int

    @staticmethod
    def _row_to_usuario(row: Tuple) -> "Usuario":
        """Convierte una tupla de BD en un objeto Usuario."""
        return Usuario(
            id_usuario=row[0],
            nom_usuario=row[1],
            contrasena_hash=row[2],
            id_rol=row[3],
        )

    @classmethod
    def buscar_por_nombre(cls, nom_usuario: str) -> Optional["Usuario"]:
        """Busca un usuario por su nombre."""
        row = DB.fetch_one(
            "SELECT id_usuario, nom_usuario, contrasena, id_rol "
            "FROM usuarios WHERE nom_usuario = %s",
            (nom_usuario,),
        )
        return cls._row_to_usuario(row) if row else None

    @staticmethod
    def _hash_password(plain: str) -> str:
        """Genera un hash seguro de la contraseña."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def _check_password(plain: str, hashed: str) -> bool:
        """Verifica que la contraseña coincida con el hash almacenado."""
        try:
            return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        except (ValueError, TypeError):
            return False

    @classmethod
    def registrar(cls, nom_usuario: str, contrasena: str, id_rol: int = 1) -> int:
        """Registra un nuevo usuario en la BD y devuelve su id."""
        existente = cls.buscar_por_nombre(nom_usuario)
        if existente:
            raise ValueError("El nombre de usuario ya existe.")

        hashed = cls._hash_password(contrasena)
        row = DB.execute_returning(
            "INSERT INTO usuarios (nom_usuario, contrasena, id_rol) "
            "VALUES (%s, %s, %s) RETURNING id_usuario",
            (nom_usuario, hashed, id_rol),
        )
        return int(row[0])

    @classmethod
    def autenticar(cls, nom_usuario: str, contrasena: str) -> Optional["Usuario"]:
        """Devuelve el usuario si la contraseña es correcta, si no None."""
        user = cls.buscar_por_nombre(nom_usuario)
        if not user:
            return None
        if not cls._check_password(contrasena, user.contrasena_hash):
            return None
        return user
    @classmethod
    def obtener_todos(cls):
        """
        Devuelve todos los usuarios con el nombre de su rol.
        """
        sql = """
            SELECT 
                u.id_usuario, 
                u.nom_usuario, 
                r.nom_rol
            FROM 
                usuarios u
            INNER JOIN 
                rol r ON u.id_rol = r.id_rol
            ORDER BY 
                u.id_usuario
        """
        return DB.ejecutar_consulta(sql, fetch_all=True)
    @classmethod
    def eliminar(cls, id_usuario):
        """
        Elimina un usuario por su ID.
        """
        sql = "DELETE FROM usuarios WHERE id_usuario = %s"
        DB.ejecutar_consulta(sql, (id_usuario,))

    @staticmethod
    def actualizar_nombre_rol(id_usuario, nom_usuario, id_rol):
        "Actualiza Nombre y rol segun usuario"
        sql = """
            UPDATE usuarios
            SET nom_usuario = %s,
                id_rol = %s
            WHERE id_usuario = %s;
        """
        DB.execute(sql, (nom_usuario, id_rol, id_usuario))

    @staticmethod
    def obtener_nombre_rol(id_rol: int) -> str:
        """Obtiene el nombre del rol dado su ID."""
        query = "SELECT nom_rol FROM rol WHERE id_rol = %s"
        row = DB.fetch_one(query, (id_rol,))
        return row[0] if row else "Desconocido"
