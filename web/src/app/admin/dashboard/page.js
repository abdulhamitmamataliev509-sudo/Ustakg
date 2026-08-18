"use client"
import React, {useEffect, useState} from 'react'
import api from '../../../services/api'

export default function DashboardPage(){
  const [stats, setStats] = useState({})

  useEffect(()=>{
    (async()=>{
      try{
        const res = await api.get('/admin/stats')
        setStats(res.data || {})
      }catch(e){ console.warn('fetch stats', e.message) }
    })()
  },[])

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Dashboard</h1>
      <div className="grid grid-cols-4 gap-4">
        <div className="p-4 bg-white rounded shadow">Total Users: {stats.total_users ?? '—'}</div>
        <div className="p-4 bg-white rounded shadow">Total Masters: {stats.total_masters ?? '—'}</div>
        <div className="p-4 bg-white rounded shadow">Open Orders: {stats.open_orders ?? '—'}</div>
        <div className="p-4 bg-white rounded shadow">System: {stats.system_status ?? '—'}</div>
      </div>
    </div>
  )
}
