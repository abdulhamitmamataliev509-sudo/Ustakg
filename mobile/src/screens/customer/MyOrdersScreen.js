import React, {useEffect, useState} from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import api from '../../services/api';

export default function MyOrdersScreen() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get('/orders/my');
        setOrders(res.data || []);
      } catch (e) {
        console.warn('fetch orders', e.message);
      }
    })();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>My Orders</Text>
      <FlatList data={orders} keyExtractor={(i) => String(i.id)} renderItem={({item}) => (
        <View style={styles.item}><Text>{item.title || 'Order'}</Text></View>
      )} ListEmptyComponent={<Text>No orders yet.</Text>} />
    </View>
  );
}

const styles = StyleSheet.create({ container:{flex:1,padding:16}, title:{fontSize:20,marginBottom:8}, item:{padding:12,borderBottomWidth:1,borderColor:'#eee'} });
