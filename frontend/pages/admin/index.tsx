import Head from 'next/head'
import { useState } from 'react'

export default function Admin() {
  const [stats] = useState({
    totalProducts: 0,
    totalOrders: 0,
    totalRevenue: 0,
    todaySales: 0
  })

  return (
    <>
      <Head>
        <title>پنل مدیریت - فروشگاه نقطه</title>
      </Head>

      <div className="min-h-screen bg-gray-100" dir="rtl">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
            <h1 className="text-3xl font-bold text-gray-900">پنل مدیریت</h1>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600">محصولات</div>
              <div className="text-2xl font-bold">{stats.totalProducts}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600">سفارشات</div>
              <div className="text-2xl font-bold">{stats.totalOrders}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600">درآمد کل</div>
              <div className="text-2xl font-bold">{stats.totalRevenue.toLocaleString('fa-IR')} تومان</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600">فروش امروز</div>
              <div className="text-2xl font-bold">{stats.todaySales.toLocaleString('fa-IR')} تومان</div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">عملیات سریع</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
                افزودن محصول
              </button>
              <button className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700">
                مشاهده سفارشات
              </button>
              <button className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700">
                گزارشات
              </button>
            </div>
          </div>
        </main>
      </div>
    </>
  )
}