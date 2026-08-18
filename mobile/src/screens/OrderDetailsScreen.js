import React from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';

export default function OrderDetailsScreen({ route }) {
  const order = route?.params?.order || {};

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Order Details</Text>
      <Text>{order.title || 'Title'}</Text>
      <Text>{order.description || 'Description'}</Text>
      <Button title="Close" onPress={() => {}} />
    </View>
  );
}

const styles = StyleSheet.create({ container:{flex:1,padding:16}, title:{fontSize:20,marginBottom:8} });
