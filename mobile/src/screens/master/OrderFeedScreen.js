import React, {useEffect, useState} from 'react';
import { View, Text, FlatList, StyleSheet, Button } from 'react-native';
import api from '../../services/api';

export default function OrderFeedScreen() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        // Backend lists open orders via ?status_filter=OPEN on /orders/
        const res = await api.get('/orders/', { params: { status_filter: 'OPEN' } });
        setOrders(res.data || []);
      } catch (e) { console.warn(e.message); }
    })();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Open Orders</Text>
      <FlatList data={orders} keyExtractor={(i)=>String(i.id)} renderItem={({item}) => (
        <View style={styles.item}><Text>{item.title}</Text><Button title="View" onPress={()=>{}}/></View>
      )} ListEmptyComponent={<Text>No open orders.</Text>} />
    </View>
  );
}

const styles = StyleSheet.create({ container:{flex:1,padding:16}, title:{fontSize:20,marginBottom:8}, item:{padding:12,borderBottomWidth:1,borderColor:'#eee'} });
