"use client"
import React, {useEffect, useState} from 'react'
import api from '../../../services/api'

export default function MastersPage(){
  const [masters, setMasters] = useState([])

  useEffect(()=>{
    (async()=>{
      try{
        const res = await api.get('/masters/')
        setMasters(res.data || [])
      }catch(e){ console.warn('fetch masters', e.message) }
    })()
  },[])

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Masters</h1>
      <div className="space-y-3">
        {masters.map(m=> (
          <div key={m.id} className="p-4 bg-white rounded shadow flex justify-between">
            <div>
              <h3 className="font-semibold">{m.name}</h3>
              <div className="text-sm text-gray-600">Rating: {m.rating || '—'}</div>
            </div>
            <div className="text-sm text-gray-500">{m.category_names?.join(', ')}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
