"use client"
import React, {useEffect, useState} from 'react'
import api from '../../services/api'
import Link from 'next/link'

export default function AdminLayout({ children }){
  const [authorized, setAuthorized] = useState(null)

  useEffect(()=>{
    (async()=>{
      try{
        const res = await api.get('/auth/me')
        if (res.data?.role === 'ADMIN') setAuthorized(true)
        else setAuthorized(false)
      }catch(e){ setAuthorized(false) }
    })()
  },[])

  if (authorized === null) return <div>Checking admin permissions...</div>
  if (!authorized) return <div>Unauthorized — admin access required.</div>

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Admin Panel</h2>
        <nav className="space-x-4">
          <Link href="/admin/dashboard">Dashboard</Link>
          <Link href="/admin/categories">Categories</Link>
          <Link href="/admin/users">Users</Link>
        </nav>
      </div>
      <div>{children}</div>
    </div>
  )
}
