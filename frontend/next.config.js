/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost', 'dotshop.ir'],
  },
  i18n: {
    locales: ['fa'],
    defaultLocale: 'fa',
  },
}

module.exports = nextConfig