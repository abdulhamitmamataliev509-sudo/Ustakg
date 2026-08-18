import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuthStore } from '../store/authStore';
import AuthStack from './AuthStack';
import CustomerTabs from './CustomerTabs';
import MasterTabs from './MasterTabs';
import OrderDetailsScreen from '../screens/OrderDetailsScreen';

const Root = createNativeStackNavigator();

export default function RootNavigator() {
  const { token, role } = useAuthStore();

  if (!token) {
    return <AuthStack />;
  }

  return (
    <Root.Navigator>
      {role === 'MASTER' ? (
        <Root.Screen name="Master" component={MasterTabs} options={{ headerShown: false }} />
      ) : (
        <Root.Screen name="Customer" component={CustomerTabs} options={{ headerShown: false }} />
      )}
      <Root.Screen name="OrderDetails" component={OrderDetailsScreen} />
    </Root.Navigator>
  );
}
