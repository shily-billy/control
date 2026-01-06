import Head from 'next/head'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export default function Home() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProducts()
  }, [])

  const fetchProducts = async () => {
    try {
      const response = await axios.get(`${API_URL}/products/`)
      setProducts(response.data)
    } catch (error) {
      console.error('Error fetching products:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Head>
        <title>فروشگاه نقطه - DOT SHOP</title>
        <meta name="description" content="امپراتوری فروش شخصی" />
      </Head>

      <main className="min-h-screen bg-gray-50" dir="rtl">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                🛍️ فروشگاه نقطه
              </h1>
              <nav className="flex gap-4">
                <Link href="/" className="text-gray-700 hover:text-gray-900">
                  خانه
                </Link>
                <Link href="/products" className="text-gray-700 hover:text-gray-900">
                  محصولات
                </Link>
                <Link href="/admin" className="text-gray-700 hover:text-gray-900">
                  مدیریت
                </Link>
              </nav>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <section className="bg-gradient-to-r from-blue-500 to-purple-600 text-white py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-4xl font-bold mb-4">
              امپراتوری فروش شخصی
            </h2>
            <p className="text-xl mb-8">
              فروش هوشمند از ۱۰+ پلتفرم بزرگ ایرانی
            </p>
            <Link
              href="/products"
              className="bg-white text-blue-600 px-8 py-3 rounded-lg font-bold hover:bg-gray-100 inline-block"
            >
              مشاهده محصولات
            </Link>
          </div>
        </section>

        {/* Products Preview */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <h3 className="text-2xl font-bold mb-6">محصولات جدید</h3>
          
          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">در حال بارگذاری...</p>
            </div>
          ) : products.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <p className="text-gray-600">محصولی موجود نیست</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {products.slice(0, 8).map((product: any) => (
                <div key={product.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition">
                  <div className="h-48 bg-gray-200"></div>
                  <div className="p-4">
                    <h4 className="font-bold text-lg mb-2 truncate">{product.title}</h4>
                    <p className="text-blue-600 font-bold">
                      {product.final_price.toLocaleString('fa-IR')} تومان
                    </p>
                    <Link
                      href={`/products/${product.id}`}
                      className="mt-4 block w-full bg-blue-600 text-white text-center py-2 rounded hover:bg-blue-700"
                    >
                      مشاهده
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Features */}
        <section className="bg-white py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
              <div>
                <div className="text-4xl mb-4">🚀</div>
                <h4 className="font-bold text-lg mb-2">فروش هوشمند</h4>
                <p className="text-gray-600">انتخاب خودکار بهترین پلتفرم</p>
              </div>
              <div>
                <div className="text-4xl mb-4">💰</div>
                <h4 className="font-bold text-lg mb-2">بیشترین سود</h4>
                <p className="text-gray-600">کمیسیون تا ۵۰٪</p>
              </div>
              <div>
                <div className="text-4xl mb-4">⚡</div>
                <h4 className="font-bold text-lg mb-2">خودکار</h4>
                <p className="text-gray-600">بدون نیاز به مدیریت دستی</p>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="bg-gray-800 text-white py-8">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <p>© 2026 فروشگاه نقطه - تمامی حقوق محفوظ است</p>
          </div>
        </footer>
      </main>
    </>
  )
}