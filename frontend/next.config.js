/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  i18n: {
    locales: ['fa'],
    defaultLocale: 'fa',
  },
  images: {
    domains: [
      'dkstatics-public.digikala.com',
      'mihanstore.net',
      'torob.com',
      'static.bamilo.com'
    ],
  },
}

module.exports = nextConfig
