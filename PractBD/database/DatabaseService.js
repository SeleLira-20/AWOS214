import { Platform } from 'react-native';
import * as SQLite from 'expo-sqlite';

class DatabaseService {
    constructor() {
        this.db = null;
        this.storageKey = 'usuarios';
    }
    
    async initialize() {
        if (Platform.OS == 'web') {
            console.log('Usando LocalStorage para web');
        } else {
            console.log('Usando SQLite para móvil');
            this.db = await SQLite.openDatabaseAsync('miapp.db');
            await this.db.execAsync(
                `CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
                );`
            );
        }
    }
    
    // Función auxiliar para convertir a formato ISO
    ensureISODate(dateString) {
        console.log('Convirtiendo fecha a ISO:', dateString);
        if (!dateString) {
            console.log('Fecha vacía, usando fecha actual');
            return new Date().toISOString();
        }
        
        if (dateString.includes('T')) {
            console.log('Ya es formato ISO');
            return dateString;
        }
        
        if (dateString.includes(' ')) {
            const isoDate = dateString.replace(' ', 'T') + 'Z';
            console.log('Convertido a ISO:', isoDate);
            return isoDate;
        }
        
        console.log('Formato no reconocido, usando fecha actual');
        return new Date().toISOString();
    }
    
    async getAll() {
        try {
            console.log('Obteniendo todos los usuarios...');
            if (Platform.OS === 'web') {
                const data = localStorage.getItem(this.storageKey);
                const usuarios = data ? JSON.parse(data) : [];
                console.log('Usuarios desde localStorage:', usuarios);
                return usuarios;
            } else {
                const usuarios = await this.db.getAllAsync('SELECT * FROM usuarios ORDER BY id DESC');
                console.log('Usuarios desde SQLite (crudos):', usuarios);
                
                const usuariosConFechaISO = usuarios.map(usuario => ({
                    ...usuario,
                    fecha_creacion: this.ensureISODate(usuario.fecha_creacion)
                }));
                
                console.log('Usuarios con fechas ISO:', usuariosConFechaISO);
                return usuariosConFechaISO;
            }
        } catch (error) {
            console.error('Error en getAll:', error);
            throw error;
        }
    }
    
    async add(nombre) {
        try {
            console.log('Agregando usuario:', nombre);
            const fechaISO = new Date().toISOString();
            console.log('Fecha ISO generada:', fechaISO);
            
            if (Platform.OS == 'web') {
                const usuarios = await this.getAll();
                const nuevoUsuario = {
                    id: Date.now(),
                    nombre,
                    fecha_creacion: fechaISO
                };
                usuarios.unshift(nuevoUsuario);
                localStorage.setItem(this.storageKey, JSON.stringify(usuarios));
                console.log('Usuario agregado a localStorage:', nuevoUsuario);
                return nuevoUsuario;
            } else {
                const result = await this.db.runAsync(
                    'INSERT INTO usuarios(nombre) VALUES (?)',
                    [nombre]
                );
                const nuevoUsuario = {
                    id: result.lastInsertRowId,
                    nombre,
                    fecha_creacion: fechaISO
                };
                console.log('Usuario agregado a SQLite:', nuevoUsuario);
                return nuevoUsuario;
            }
        } catch (error) {
            console.error('Error en add:', error);
            throw error;
        }
    }

    // UPDATE - Actualizar usuario
    async update(id, nombre) {
        try {
            console.log('Actualizando usuario ID:', id, 'Nuevo nombre:', nombre);
            const fechaISO = new Date().toISOString();
            
            if (Platform.OS == 'web') {
                const usuarios = await this.getAll();
                const usuarioIndex = usuarios.findIndex(u => u.id == id);
                
                if (usuarioIndex === -1) {
                    throw new Error('Usuario no encontrado');
                }
                
                usuarios[usuarioIndex] = {
                    ...usuarios[usuarioIndex],
                    nombre,
                    fecha_creacion: fechaISO // Actualizar fecha de modificación
                };
                
                localStorage.setItem(this.storageKey, JSON.stringify(usuarios));
                console.log('Usuario actualizado en localStorage:', usuarios[usuarioIndex]);
                return usuarios[usuarioIndex];
            } else {
                const result = await this.db.runAsync(
                    'UPDATE usuarios SET nombre = ?, fecha_creacion = ? WHERE id = ?',
                    [nombre, fechaISO, id]
                );
                
                if (result.changes === 0) {
                    throw new Error('Usuario no encontrado');
                }
                
                const usuarioActualizado = {
                    id: parseInt(id),
                    nombre,
                    fecha_creacion: fechaISO
                };
                
                console.log('Usuario actualizado en SQLite:', usuarioActualizado);
                return usuarioActualizado;
            }
        } catch (error) {
            console.error('Error en update:', error);
            throw error;
        }
    }

    // DELETE - Eliminar usuario
    async delete(id) {
        try {
            console.log('Eliminando usuario ID:', id);
            
            if (Platform.OS == 'web') {
                const usuarios = await this.getAll();
                const usuarioIndex = usuarios.findIndex(u => u.id == id);
                
                if (usuarioIndex === -1) {
                    throw new Error('Usuario no encontrado');
                }
                
                const usuarioEliminado = usuarios[usuarioIndex];
                usuarios.splice(usuarioIndex, 1);
                
                localStorage.setItem(this.storageKey, JSON.stringify(usuarios));
                console.log('Usuario eliminado de localStorage:', usuarioEliminado);
                return usuarioEliminado;
            } else {
                // Primero obtener el usuario para retornarlo
                const usuario = await this.db.getFirstAsync(
                    'SELECT * FROM usuarios WHERE id = ?',
                    [id]
                );
                
                if (!usuario) {
                    throw new Error('Usuario no encontrado');
                }
                
                const result = await this.db.runAsync(
                    'DELETE FROM usuarios WHERE id = ?',
                    [id]
                );
                
                if (result.changes === 0) {
                    throw new Error('Usuario no encontrado');
                }
                
                console.log('Usuario eliminado de SQLite:', usuario);
                return usuario;
            }
        } catch (error) {
            console.error('Error en delete:', error);
            throw error;
        }
    }
}

// Exportar instancia de la clase
export default new DatabaseService();