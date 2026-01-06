'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('')

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-primary">🛒 فروشگاه نقطه</h1>
            <nav className="flex gap-6">
              <Link href="/products" className="hover:text-primary">محصولات</Link>
              <Link href="/about" className="hover:text-primary">درباره ما</Link>
              <Link href="/contact" className="hover:text-primary">تماس</Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-l from-blue-500 to-blue-600 text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-4">خرید هوشمند از 10+ فروشگاه</h2>
          <p className="text-xl mb-8">بهترین قیمت را برای شما پیدا می‌کنیم</p>
          
          <div className="max-w-2xl mx-auto">
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="چه محصولی دنبال هستید؟"
                className="flex-1 px-6 py-4 rounded-lg text-gray-800 text-lg"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button className="bg-white text-blue-600 px-8 py-4 rounded-lg font-bold hover:bg-gray-100">
                🔍 جستجو
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <h3 className="text-3xl font-bold text-center mb-12">چرا فروشگاه نقطه؟</h3>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-lg shadow-md text-center">
              <div className="text-4xl mb-4">💰</div>
              <h4 className="text-xl font-bold mb-2">بهترین قیمت</h4>
              <p className="text-gray-600">مقایسه خودکار قیمت در 10+ فروشگاه</p>
            </div>
            
            <div className="bg-white p-8 rounded-lg shadow-md text-center">
              <div className="text-4xl mb-4">🚚</div>
              <h4 className="text-xl font-bold mb-2">ارسال سریع</h4>
              <p className="text-gray-600">ارسال رایگان به سراسر کشور</p>
            </div>
            
            <div className="bg-white p-8 rounded-lg shadow-md text-center">
              <div className="text-4xl mb-4">✅</div>
              <h4 className="text-xl font-bold mb-2">گارانتی اصالت</h4>
              <p className="text-gray-600">تضمین اصالت و کیفیت محصولات</p>
            </div>
          </div>
        </div>
      </section>

      {/* Platforms */}
      <section className="bg-gray-100 py-16">
        <div className="container mx-auto px-4">
          <h3 className="text-3xl font-bold text-center mb-8">فروشگاه‌های همکار</h3>
          <div className="flex flex-wrap justify-center gap-8 items-center">
            <div className="bg-white px-8 py-4 rounded-lg shadow">دیجی‌کالا</div>
            <div className="bg-white px-8 py-4 rounded-lg shadow">میهن استور</div>
            <div className="bg-white px-8 py-4 rounded-lg shadow">ترب</div>
            <div className="bg-white px-8 py-4 rounded-lg shadow">بامیلو</div>
            <div className="bg-white px-8 py-4 rounded-lg shadow">دیوار</div>
            <div className="bg-white px-8 py-4 rounded-lg shadow">شیپور</div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8">
        <div className="container mx-auto px-4 text-center">
          <p>© 2026 فروشگاه نقطه - تمامی حقوق محفوظ است</p>
        </div>
      </footer>
    </div>
  )
}
