import React, {useState} from 'react';
import { View, Text, TextInput, Button, StyleSheet, Picker } from 'react-native';
import { useAuthStore } from '../../store/authStore';

export default function RegisterScreen({ navigation }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState('CUSTOMER');
  const register = useAuthStore((s) => s.register);

  const onRegister = async () => {
    try {
      await register({ email, password, name, role });
    } catch (e) {
      alert('Register failed: ' + (e.response?.data?.detail || e.message));
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Register</Text>
      <TextInput placeholder="Name" style={styles.input} value={name} onChangeText={setName} />
      <TextInput placeholder="Email" style={styles.input} value={email} onChangeText={setEmail} />
      <TextInput placeholder="Password" style={styles.input} value={password} onChangeText={setPassword} secureTextEntry />
      <View style={{marginBottom:12}}>
        <Text>Role</Text>
        <Picker selectedValue={role} onValueChange={(v) => setRole(v)}>
          <Picker.Item label="Customer" value="CUSTOMER" />
          <Picker.Item label="Master" value="MASTER" />
        </Picker>
      </View>
      <Button title="Create account" onPress={onRegister} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex:1, padding:16, justifyContent:'center' },
  title: { fontSize:20, marginBottom:16 },
  input: { borderWidth:1, borderColor:'#ccc', padding:8, marginBottom:12 }
});
