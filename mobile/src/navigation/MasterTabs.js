import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import OrderFeedScreen from '../screens/master/OrderFeedScreen';
import MyOffersScreen from '../screens/master/MyOffersScreen';
import MasterProfileScreen from '../screens/master/MasterProfileScreen';

const Tab = createBottomTabNavigator();

export default function MasterTabs() {
  return (
    <Tab.Navigator>
      <Tab.Screen name="Feed" component={OrderFeedScreen} />
      <Tab.Screen name="Offers" component={MyOffersScreen} />
      <Tab.Screen name="Profile" component={MasterProfileScreen} />
    </Tab.Navigator>
  );
}
