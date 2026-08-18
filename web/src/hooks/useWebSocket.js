import { useEffect, useRef, useState } from 'react'

export default function useWebSocket(url) {
  const wsRef = useRef(null)
  const [lastMessage, setLastMessage] = useState(null)
  const [readyState, setReadyState] = useState(0)

  useEffect(()=>{
    if (!url) return
    const ws = new WebSocket(url)
    wsRef.current = ws
    ws.onopen = ()=> setReadyState(ws.readyState)
    ws.onmessage = (ev)=> setLastMessage(JSON.parse(ev.data))
    ws.onclose = ()=> setReadyState(ws.readyState)
    ws.onerror = ()=> setReadyState(ws.readyState)
    return ()=> ws.close()
  }, [url])

  const send = (payload)=> {
    if (wsRef.current && wsRef.current.readyState === 1) wsRef.current.send(JSON.stringify(payload))
  }

  return { send, lastMessage, readyState }
}
