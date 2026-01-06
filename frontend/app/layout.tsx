import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'فروشگاه نقطه - DOT SHOP',
  description: 'امپراتوری فروش شخصی چند پلتفرمی',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fa" dir="rtl">
      <body className="font-sans bg-gray-50">{children}</body>
    </html>
  )
}
