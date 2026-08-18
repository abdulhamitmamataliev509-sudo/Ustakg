"use client"
import React, {useEffect, useState} from 'react'
import api from '../../../services/api'

export default function AdminCategories(){
  const [categories, setCategories] = useState([])
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  const load = async ()=>{
    try{ const res = await api.get('/categories/'); setCategories(res.data||[]) }catch(e){console.warn(e.message)}
  }

  useEffect(()=>{ load() },[])

  const create = async ()=>{
    try{
      await api.post('/categories/', { name, description })
      setName(''); setDescription('')
      await load()
      alert('Category created')
    }catch(e){ alert('Create failed: '+e.message) }
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Manage Categories</h1>
      <div className="mb-4">
        <input value={name} onChange={(e)=>setName(e.target.value)} placeholder="Name" className="p-2 border" />
        <input value={description} onChange={(e)=>setDescription(e.target.value)} placeholder="Description" className="p-2 border ml-2" />
        <button onClick={create} className="ml-2 px-3 py-2 bg-blue-600 text-white rounded">Create</button>
      </div>
      <div className="grid grid-cols-3 gap-4">
        {categories.map(c=> <div key={c.id} className="p-3 bg-white rounded shadow">{c.name}</div>)}
      </div>
    </div>
  )
}
