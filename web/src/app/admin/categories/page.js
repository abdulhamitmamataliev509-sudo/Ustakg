"use client"
import React, {useEffect, useState} from 'react'
import api from '../../../services/api'

function slugify(value) {
  return value.toLowerCase().trim().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
}

export default function AdminCategories(){
  const [categories, setCategories] = useState([])
  const [title, setTitle] = useState('')

  const load = async ()=>{
    try{ const res = await api.get('/categories/'); setCategories(res.data||[]) }catch(e){console.warn(e.message)}
  }

  useEffect(()=>{ load() },[])

  const create = async ()=>{
    try{
      if (!title.trim()) return alert('Title is required')
      await api.post('/categories/', { title, slug: slugify(title) })
      setTitle('')
      await load()
      alert('Category created')
    }catch(e){ alert('Create failed: '+(e.response?.data?.detail || e.message)) }
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Manage Categories</h1>
      <div className="mb-4">
        <input value={title} onChange={(e)=>setTitle(e.target.value)} placeholder="Title" className="p-2 border" />
        <button onClick={create} className="ml-2 px-3 py-2 bg-blue-600 text-white rounded">Create</button>
      </div>
      <div className="grid grid-cols-3 gap-4">
        {categories.map(c=> <div key={c.id} className="p-3 bg-white rounded shadow">{c.title}</div>)}
      </div>
    </div>
  )
}
