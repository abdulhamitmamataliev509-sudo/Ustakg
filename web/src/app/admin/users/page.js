"use client"
import React, {useEffect, useState} from 'react'
import api from '../../../services/api'

export default function AdminUsers(){
  const [users, setUsers] = useState([])

  const load = async ()=>{
    try{ const res = await api.get('/users/'); setUsers(res.data||[]) }catch(e){console.warn(e.message)}
  }

  useEffect(()=>{ load() },[])

  const verify = async (id)=>{
    try{ await api.post(`/users/${id}/verify`); await load(); }catch(e){alert('Verify failed')}
  }

  const toggleBlock = async (id)=>{
    try{ await api.post(`/users/${id}/block`); await load(); }catch(e){alert('Block toggle failed')}
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Users</h1>
      <div className="space-y-2">
        {users.map(u => (
          <div key={u.id} className="p-3 bg-white rounded flex justify-between items-center">
            <div>
              <div className="font-semibold">{u.name || u.email}</div>
              <div className="text-sm text-gray-600">Role: {u.role}</div>
            </div>
            <div className="space-x-2">
              <button onClick={()=>verify(u.id)} className="px-2 py-1 bg-green-600 text-white rounded">Verify</button>
              <button onClick={()=>toggleBlock(u.id)} className="px-2 py-1 bg-red-600 text-white rounded">Block/Unblock</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
