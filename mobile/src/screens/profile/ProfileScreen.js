import React from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';
import { useAuthStore } from '../../store/authStore';

export default function ProfileScreen() {
  const { user, logout } = useAuthStore();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Profile</Text>
      <Text>{user?.full_name || user?.phone_number || 'User'}</Text>
      <Text>{user?.phone_number}</Text>
      <Text>Role: {user?.role}</Text>
      <Button title="Logout" onPress={logout} />
    </View>
  );
}

const styles = StyleSheet.create({ container:{flex:1,padding:16}, title:{fontSize:20,marginBottom:8} });
