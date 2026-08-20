import React, {useEffect, useState} from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import api from '../../services/api';

export default function MyOffersScreen() {
  const [offers, setOffers] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get('/offers/my');
        setOffers(res.data || []);
      } catch (e) { console.warn(e.message); }
    })();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>My Offers</Text>
      <FlatList data={offers} keyExtractor={(i)=>String(i.id)} renderItem={({item}) => (
        <View style={styles.item}>
          <Text>Price: {item.proposed_price} KGS</Text>
          <Text style={{color:'#666'}}>Status: {item.status}</Text>
          {item.comment ? <Text style={{color:'#888'}}>{item.comment}</Text> : null}
        </View>
      )} ListEmptyComponent={<Text>No offers yet.</Text>} />
    </View>
  );
}

const styles = StyleSheet.create({ container:{flex:1,padding:16}, title:{fontSize:20,marginBottom:8}, item:{padding:12,borderBottomWidth:1,borderColor:'#eee'} });
