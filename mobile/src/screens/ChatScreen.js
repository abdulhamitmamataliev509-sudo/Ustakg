import React, {useEffect, useRef, useState} from 'react';
import { View, Text, FlatList, TextInput, Button, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { useAuthStore } from '../store/authStore';
import { DEFAULT_API_BASE } from '../config';

function makeWsUrl(base, chatId, token){
  // convert http(s) to ws(s)
  let wsBase = base.replace(/^http/, 'ws');
  if (wsBase.endsWith('/api/v1')) wsBase = wsBase.replace(/\/api\/v1$/, '/api/v1');
  return `${wsBase}/chats/ws/${chatId}?token=${encodeURIComponent(token)}`;
}

export default function ChatScreen({ route }){
  const chatId = route?.params?.chatId;
  const token = useAuthStore(s=>s.token);
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState('');
  const wsRef = useRef(null);

  useEffect(()=>{
    if (!chatId || !token) return;
    const url = makeWsUrl(DEFAULT_API_BASE, chatId, token);
    const ws = new WebSocket(url);
    wsRef.current = ws;
    ws.onopen = ()=>{
      console.log('ws open', url);
    };
    ws.onmessage = (ev)=>{
      try{
        const data = JSON.parse(ev.data);
        if (data.type === 'message'){
          setMessages((m)=>[...m, data]);
        }
      }catch(e){ console.warn(e) }
    };
    ws.onclose = ()=>{
      console.log('ws closed');
      // naive reconnect after 1s
      setTimeout(()=>{
        if (wsRef.current === ws) {
          const newWs = new WebSocket(url);
          wsRef.current = newWs;
        }
      }, 1000);
    };
    return ()=>{ ws.close(); };
  }, [chatId, token]);

  const send = ()=>{
    if (!wsRef.current || wsRef.current.readyState !== 1) return alert('Not connected');
    wsRef.current.send(JSON.stringify({ message_text: text }));
    setText('');
  };

  return (
    <KeyboardAvoidingView behavior={Platform.OS==='ios'?'padding':'height'} style={{flex:1}}>
      <View style={styles.container}>
        <Text style={styles.title}>Chat</Text>
        <FlatList data={messages} keyExtractor={(i)=>i.id || Math.random().toString()} renderItem={({item})=> (
          <View style={styles.message}><Text style={{fontWeight:'600'}}>{item.sender_id}</Text><Text>{item.message_text}</Text></View>
        )} />
        <View style={styles.inputRow}>
          <TextInput style={styles.input} value={text} onChangeText={setText} placeholder="Message" />
          <Button title="Send" onPress={send} />
        </View>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({ container:{flex:1,padding:12}, title:{fontSize:18,marginBottom:8}, message:{padding:8,backgroundColor:'#fff',borderRadius:6,marginBottom:6}, inputRow:{flexDirection:'row',alignItems:'center',paddingTop:8}, input:{flex:1,borderWidth:1,borderColor:'#ddd',padding:8,marginRight:8,borderRadius:6} });
