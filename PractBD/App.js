import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View } from 'react-native';
import InsertUsuarioScreen from './screens/InsertUsuarioScreen'; 

export default function App() {
  return (
    <View style={styles.container}>
      <InsertUsuarioScreen />
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
});