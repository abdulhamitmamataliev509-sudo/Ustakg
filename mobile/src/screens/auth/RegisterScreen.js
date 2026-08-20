import React, {useState} from 'react';
import { View, Text, TextInput, Button, Pressable, StyleSheet } from 'react-native';
import { useAuthStore } from '../../store/authStore';

export default function RegisterScreen() {
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('CUSTOMER');
  const register = useAuthStore((s) => s.register);

  const onRegister = async () => {
    if (!fullName || !phone || !password) {
      return alert('Name, phone and password are required');
    }
    try {
      await register({ phone_number: phone, password, full_name: fullName, role });
    } catch (e) {
      alert('Register failed: ' + (e.response?.data?.detail || e.message));
    }
  };

  const selectRole = (value) => setRole(value);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Register</Text>
      <TextInput placeholder="Full Name" style={styles.input} value={fullName} onChangeText={setFullName} />
      <TextInput
        placeholder="Phone (+996XXXXXXXXX)"
        keyboardType="phone-pad"
        autoCapitalize="none"
        style={styles.input}
        value={phone}
        onChangeText={setPhone}
      />
      <TextInput placeholder="Password" style={styles.input} value={password} onChangeText={setPassword} secureTextEntry />
      <View style={styles.roleRow}>
        <Text>Role: </Text>
        <Pressable style={[styles.roleBtn, role === 'CUSTOMER' && styles.roleBtnActive]} onPress={() => selectRole('CUSTOMER')}>
          <Text style={role === 'CUSTOMER' && styles.roleTextActive}>Customer</Text>
        </Pressable>
        <Pressable style={[styles.roleBtn, role === 'MASTER' && styles.roleBtnActive]} onPress={() => selectRole('MASTER')}>
          <Text style={role === 'MASTER' && styles.roleTextActive}>Master</Text>
        </Pressable>
      </View>
      <Button title="Create account" onPress={onRegister} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex:1, padding:16, justifyContent:'center' },
  title: { fontSize:20, marginBottom:16 },
  input: { borderWidth:1, borderColor:'#ccc', padding:8, marginBottom:12 },
  roleRow: { flexDirection:'row', alignItems:'center', marginBottom:12 },
  roleBtn: { paddingVertical:6, paddingHorizontal:14, borderWidth:1, borderColor:'#ccc', borderRadius:6, marginLeft:6, backgroundColor:'#fff' },
  roleBtnActive: { backgroundColor:'#0ea5e9', borderColor:'#0ea5e9' },
  roleTextActive: { color:'#fff' }
});
