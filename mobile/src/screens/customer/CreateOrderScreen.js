import React, {useState} from 'react';
import { View, Text, TextInput, Button, StyleSheet } from 'react-native';
import api from '../../services/api';

export default function CreateOrderScreen({ navigation }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const submit = async () => {
    try {
      const res = await api.post('/orders', { title, description });
      alert('Order created');
      navigation.navigate('Orders');
    } catch (e) {
      alert('Create order failed: ' + (e.response?.data?.detail || e.message));
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Create Order</Text>
      <TextInput placeholder="Title" style={styles.input} value={title} onChangeText={setTitle} />
      <TextInput placeholder="Description" style={[styles.input,{height:100}]} value={description} onChangeText={setDescription} multiline />
      <Button title="Submit" onPress={submit} />
    </View>
  );
}

const styles = StyleSheet.create({ container:{flex:1,padding:16}, title:{fontSize:20,marginBottom:12}, input:{borderWidth:1,borderColor:'#ccc',padding:8,marginBottom:12} });
