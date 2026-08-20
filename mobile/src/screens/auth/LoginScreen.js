import React, {useState} from 'react';
import { View, Text, TextInput, Button, StyleSheet } from 'react-native';
import { useAuthStore } from '../../store/authStore';

export default function LoginScreen({ navigation }) {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const login = useAuthStore((s) => s.login);

  const onLogin = async () => {
    if (!phone || !password) return alert('Phone and password are required');
    try {
      await login(phone, password);
    } catch (e) {
      alert('Login failed: ' + (e.response?.data?.detail || e.message));
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Usta kg — Login</Text>
      <TextInput
        placeholder="Phone (+996XXXXXXXXX)"
        keyboardType="phone-pad"
        autoCapitalize="none"
        style={styles.input}
        value={phone}
        onChangeText={setPhone}
      />
      <TextInput placeholder="Password" style={styles.input} value={password} onChangeText={setPassword} secureTextEntry />
      <Button title="Login" onPress={onLogin} />
      <Button title="Register" onPress={() => navigation.navigate('Register')} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex:1, padding:16, justifyContent:'center' },
  title: { fontSize:20, marginBottom:16 },
  input: { borderWidth:1, borderColor:'#ccc', padding:8, marginBottom:12 }
});
