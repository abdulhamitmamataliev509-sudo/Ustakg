"use client"
import React, {useEffect, useState} from 'react'
import api from '../../services/api'

export default function LandingPage(){
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
      <section className="py-12">
        <h1 className="text-4xl font-bold">Usta kg — Find trusted local masters</h1>
        <p className="mt-4 text-gray-600">Search services, view masters, book jobs.</p>
      </section>

      <section className="mt-8">
        <h2 className="text-2xl font-semibold mb-4">Popular Categories</h2>
        <div className="grid grid-cols-3 gap-4">
          {categories.slice(0,9).map((c)=> (
            <div key={c.id} className="p-4 bg-white rounded shadow">{c.title}</div>
          ))}
        </div>
      </section>
    </div>
  )
}
