import React, {useEffect} from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { View, ActivityIndicator } from 'react-native';
import { useAuthStore } from './src/store/authStore';
import RootNavigator from './src/navigation';
import { setAuthToken } from './src/services/api';

export default function App() {
  const { restoring, restoreToken, token } = useAuthStore();

  useEffect(() => {
    restoreToken();
  }, []);

  useEffect(() => {
    if (token) setAuthToken(token);
  }, [token]);

  if (restoring) {
    return (
      <View style={{flex:1,justifyContent:'center',alignItems:'center'}}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <RootNavigator />
      <StatusBar style="auto" />
    </NavigationContainer>
  );
}
