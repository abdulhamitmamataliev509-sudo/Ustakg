"use client"
import React, {useEffect, useState} from 'react'
import api from '../../../services/api'

export default function CategoriesPage(){
  const [categories, setCategories] = useState([])

  useEffect(()=>{
    (async()=>{
      try{
        const res = await api.get('/categories/')
        setCategories(res.data || [])
      }catch(e){ console.warn('fetch categories', e.message) }
    })()
  },[])

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Categories</h1>
      <div className="grid grid-cols-3 gap-4">
        {categories.map(cat=> (
          <div key={cat.id} className="p-4 bg-white rounded shadow">
            <h3 className="font-semibold">{cat.title}</h3>
            {cat.children && cat.children.length > 0 ? (
              <p className="text-sm text-gray-600">
                {cat.children.map((child) => child.title).join(', ')}
              </p>
            ) : (
              <p className="text-sm text-gray-600">{cat.slug}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
