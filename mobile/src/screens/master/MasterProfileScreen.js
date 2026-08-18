import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function MasterProfileScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Master Profile</Text>
      <Text>Edit bio, experience, and rating here.</Text>
    </View>
  );
}

const styles = StyleSheet.create({ container:{flex:1,padding:16}, title:{fontSize:20,marginBottom:8} });
