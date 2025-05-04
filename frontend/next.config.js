/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  // 如果需要配置API代理，可以在这里添加
  // async rewrites() {
  //   return [
  //     {
  //       source: '/api/:path*',
  //       destination: 'http://backend:8000/api/:path*',
  //     },
  //   ]
  // },
}

module.exports = nextConfig
