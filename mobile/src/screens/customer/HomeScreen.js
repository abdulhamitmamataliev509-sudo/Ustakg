import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';

export default function HomeScreen() {
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Home</Text>
      <Text>Categories grid and top masters will appear here.</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding:16 },
  title: { fontSize:22, marginBottom:12 }
});
