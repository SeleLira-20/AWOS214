import React, { useEffect, useState } from 'react';
import {
  View, Text, FlatList, TouchableOpacity,
  Alert, StyleSheet, ActivityIndicator,
  TextInput, ScrollView
} from 'react-native';

const API_URL = 'http://10.16.35.44:5000';

// 👇 credenciales fijas en el código
const toBase64 = (str) => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
  let encoded = '';
  for (let i = 0; i < str.length; i += 3) {
    const a = str.charCodeAt(i);
    const b = i + 1 < str.length ? str.charCodeAt(i + 1) : 0;
    const c = i + 2 < str.length ? str.charCodeAt(i + 2) : 0;
    encoded += chars[a >> 2];
    encoded += chars[((a & 3) << 4) | (b >> 4)];
    encoded += i + 1 < str.length ? chars[((b & 15) << 2) | (c >> 6)] : '=';
    encoded += i + 2 < str.length ? chars[c & 63] : '=';
  }
  return encoded;
};

const AUTH = 'Basic ' + toBase64('SeleneLira:123456');

export default function App() {
  const [productos, setProductos] = useState([]);
  const [cargando, setCargando]   = useState(true);
  const [modalVisible, setModal]  = useState(false);
  const [editando, setEditando]   = useState(false);

  const [id, setId]         = useState('');
  const [nombre, setNombre] = useState('');
  const [precio, setPrecio] = useState('');
  const [stock, setStock]   = useState('');

  useEffect(() => {
    obtenerProductos();
  }, []);

  // ──────────────────────────────
  // GET
  // ──────────────────────────────
  const obtenerProductos = async () => {
    try {
      const res  = await fetch(`${API_URL}/v1/productos/`);
      const data = await res.json();
      setProductos(data.productos);
    } catch {
      Alert.alert('Error', 'No se pudo conectar con la API');
    } finally {
      setCargando(false);
    }
  };

  // ──────────────────────────────
  // POST
  // ──────────────────────────────
  const crearProducto = async () => {
    try {
      const res = await fetch(`${API_URL}/v1/productos/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id:     parseInt(id),
          nombre: nombre,
          precio: parseFloat(precio),
          stock:  parseInt(stock)
        })
      });
      if (res.ok) {
        cerrarModal();
        await obtenerProductos();
        Alert.alert('✅ Éxito', 'Producto creado');
      } else {
        const err = await res.json();
        Alert.alert('❌ Error', err.detail || 'No se pudo crear');
      }
    } catch {
      Alert.alert('Error', 'Falló la conexión');
    }
  };

  // ──────────────────────────────
  // PUT
  // ──────────────────────────────
  const actualizarProducto = async () => {
    try {
      const res = await fetch(`${API_URL}/v1/productos/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': AUTH  // 👈 credenciales fijas
        },
        body: JSON.stringify({
          id:     parseInt(id),
          nombre: nombre,
          precio: parseFloat(precio),
          stock:  parseInt(stock)
        })
      });
      if (res.ok) {
        cerrarModal();
        await obtenerProductos();
        Alert.alert('✅ Éxito', 'Producto actualizado');
      } else {
        const err = await res.json();
        Alert.alert('❌ Error', err.detail || 'No se pudo actualizar');
      }
    } catch {
      Alert.alert('Error', 'Falló la conexión');
    }
  };

  // ──────────────────────────────
  // DELETE
  // ──────────────────────────────
  const eliminarProducto = async (idProducto) => {
    try {
      const res = await fetch(`${API_URL}/v1/productos/${idProducto}`, {
        method: 'DELETE',
        headers: { 'Authorization': AUTH }  // 👈 credenciales fijas
      });
      if (res.ok) {
        await obtenerProductos();
        Alert.alert('✅ Éxito', 'Producto eliminado');
      } else {
        Alert.alert('❌ Error', 'No autorizado o producto no encontrado');
      }
    } catch {
      Alert.alert('Error', 'Falló la conexión');
    }
  };

  // ──────────────────────────────
  // Helpers modal
  // ──────────────────────────────
  const abrirCrear = () => {
    setId(''); setNombre(''); setPrecio(''); setStock('');
    setEditando(false);
    setModal(true);
  };

  const abrirEditar = (item) => {
    setId(item.id.toString());
    setNombre(item.nombre);
    setPrecio(item.precio.toString());
    setStock(item.stock.toString());
    setEditando(true);
    setModal(true);
  };

  const cerrarModal = () => setModal(false);

  // ──────────────────────────────
  // UI
  // ──────────────────────────────
  if (cargando) return <ActivityIndicator size="large" style={styles.loader} />;

  return (
    <View style={styles.contenedor}>
      <Text style={styles.titulo}>🛒 Productos</Text>

      {/* Botones superiores */}
      <View style={styles.filaBotones}>
        <TouchableOpacity style={styles.botonAgregar} onPress={abrirCrear}>
          <Text style={styles.botonTexto}>➕ Agregar</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.botonRefrescar} onPress={obtenerProductos}>
          <Text style={styles.botonTexto}>🔄 Refrescar</Text>
        </TouchableOpacity>
      </View>

      {/* Lista productos */}
      <FlatList
        data={productos}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View style={styles.tarjeta}>
            <View style={{ flex: 1 }}>
              <Text style={styles.nombre}>{item.nombre}</Text>
              <Text style={styles.detalle}>💰 ${item.precio}</Text>
              <Text style={styles.detalle}>📦 Stock: {item.stock}</Text>
            </View>
            <View style={styles.filaBotonesCard}>
              <TouchableOpacity
                style={styles.botonEditar}
                onPress={() => abrirEditar(item)}
              >
                <Text style={styles.botonTexto}>✏️</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.botonEliminar}
                onPress={() => eliminarProducto(item.id)}
              >
                <Text style={styles.botonTexto}>🗑️</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}
      />

      {/* Modal formulario */}
      {modalVisible && (
        <View style={styles.modalFondo}>
          <ScrollView contentContainerStyle={styles.modal}>
            <Text style={styles.modalTitulo}>
              {editando ? '✏️ Editar Producto' : '➕ Nuevo Producto'}
            </Text>

            <Text style={styles.label}>ID</Text>
            <TextInput
              style={[styles.input, editando && styles.inputDeshabilitado]}
              value={id}
              onChangeText={setId}
              keyboardType="numeric"
              editable={!editando}
              placeholder="Ej: 4"
            />

            <Text style={styles.label}>Nombre</Text>
            <TextInput
              style={styles.input}
              value={nombre}
              onChangeText={setNombre}
              placeholder="Ej: Monitor"
            />

            <Text style={styles.label}>Precio</Text>
            <TextInput
              style={styles.input}
              value={precio}
              onChangeText={setPrecio}
              keyboardType="decimal-pad"
              placeholder="Ej: 3500.00"
            />

            <Text style={styles.label}>Stock</Text>
            <TextInput
              style={styles.input}
              value={stock}
              onChangeText={setStock}
              keyboardType="numeric"
              placeholder="Ej: 15"
            />

            <TouchableOpacity
              style={styles.botonGuardar}
              onPress={editando ? actualizarProducto : crearProducto}
            >
              <Text style={styles.botonTexto}>
                {editando ? '💾 Actualizar' : '💾 Guardar'}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.botonCancelar} onPress={cerrarModal}>
              <Text style={styles.botonTexto}>✖️ Cancelar</Text>
            </TouchableOpacity>
          </ScrollView>
        </View>
      )}

    </View>
  );
}

const styles = StyleSheet.create({
  contenedor:         { flex: 1, padding: 20, backgroundColor: '#f5f5f5' },
  titulo:             { fontSize: 24, fontWeight: 'bold', marginBottom: 15, marginTop: 40 },
  loader:             { flex: 1, justifyContent: 'center' },

  filaBotones:        { flexDirection: 'row', gap: 10, marginBottom: 15 },
  botonAgregar:       { backgroundColor: '#27ae60', padding: 10, borderRadius: 8,
                        flex: 1, alignItems: 'center' },
  botonRefrescar:     { backgroundColor: '#2980b9', padding: 10, borderRadius: 8,
                        flex: 1, alignItems: 'center' },

  tarjeta:            { backgroundColor: '#fff', padding: 15, borderRadius: 10,
                        marginBottom: 10, flexDirection: 'row', alignItems: 'center' },
  nombre:             { fontSize: 16, fontWeight: 'bold' },
  detalle:            { fontSize: 13, color: '#666' },
  filaBotonesCard:    { flexDirection: 'row', gap: 8 },
  botonEditar:        { backgroundColor: '#f39c12', padding: 8, borderRadius: 8 },
  botonEliminar:      { backgroundColor: '#e74c3c', padding: 8, borderRadius: 8 },
  botonTexto:         { color: '#fff', fontWeight: 'bold' },

  modalFondo:         { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
                        backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'center' },
  modal:              { backgroundColor: '#fff', margin: 20, borderRadius: 12, padding: 25 },
  modalTitulo:        { fontSize: 20, fontWeight: 'bold', marginBottom: 15 },
  label:              { fontSize: 14, color: '#333', marginBottom: 4 },
  input:              { borderWidth: 1, borderColor: '#ccc', borderRadius: 8,
                        padding: 10, marginBottom: 12, fontSize: 15 },
  inputDeshabilitado: { backgroundColor: '#eee', color: '#999' },
  botonGuardar:       { backgroundColor: '#27ae60', padding: 12, borderRadius: 8,
                        alignItems: 'center', marginBottom: 8 },
  botonCancelar:      { backgroundColor: '#95a5a6', padding: 12, borderRadius: 8,
                        alignItems: 'center' },
});