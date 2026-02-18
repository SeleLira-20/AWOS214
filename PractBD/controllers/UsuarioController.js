import { Usuario } from '../models/usuario';
import { Platform } from 'react-native';

// La API corre en el puerto 5000 de tu PC
const API_BASE = Platform.OS === 'android' 
    ? 'http://10.0.2.2:5000/v1/usuarios/'  // Para emulador Android
    : 'http://localhost:5000/v1/usuarios/'; // Para iOS/web

export class UsuarioController {
    constructor() {
        this.listeners = [];
    }

    async initialize() {
        return true; 
    }
    
    async obtenerUsuarios() {
        try {
            console.log('Conectando a:', API_BASE); // Para depuración
            const response = await fetch(API_BASE);
            const data = await response.json();
            
            if (data && data.usuarios) {
                return data.usuarios.map(u => new Usuario(
                    u.id, 
                    u.nombre, 
                    new Date().toISOString() 
                ));
            }
            return [];
        } catch (error) {
            console.error('Error de conexión:', error);
            throw new Error('No se pudo conectar con FastAPI. ¿La API está corriendo en http://localhost:5000?');
        }
    }
    
    async crearUsuario(nombre) {
        try {
            const nuevoUsuario = {
                id: Math.floor(Math.random() * 1000),
                nombre: nombre.trim(),
                edad: 21
            };

            const response = await fetch(API_BASE, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(nuevoUsuario)
            });

            const result = await response.json();
            if (!response.ok) throw new Error(result.detail || 'Error al guardar');

            this.notifyListeners();
            return new Usuario(result.Usuario.id, result.Usuario.nombre);
        } catch (error) {
            throw error;
        }
    }

    async actualizarUsuario(id, nombre) {
        try {
            const usuarioActualizado = {
                id: id,
                nombre: nombre.trim(),
                edad: 21
            };

            const response = await fetch(`${API_BASE}${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(usuarioActualizado)
            });

            const result = await response.json();
            if (!response.ok) throw new Error(result.detail || 'Error al actualizar');

            this.notifyListeners();
            return new Usuario(result.Usuario.id, result.Usuario.nombre);
        } catch (error) {
            throw error;
        }
    }

    async eliminarUsuario(id) {
        try {
            const response = await fetch(`${API_BASE}${id}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            });

            const result = await response.json();
            if (!response.ok) throw new Error(result.detail || 'Error al eliminar');

            this.notifyListeners();
            return new Usuario(result.Usuario.id, result.Usuario.nombre);
        } catch (error) {
            throw error;
        }
    }

    addListener(callback) { this.listeners.push(callback); }
    removeListener(callback) { this.listeners = this.listeners.filter(l => l !== callback); }
    notifyListeners() { this.listeners.forEach(callback => callback()); }
}