/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['maplibre-gl', 'react-map-gl'],
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  experimental: {
    serverComponentsExternalPackages: [],
    optimizePackageImports: ['maplibre-gl', 'react-map-gl', 'react-hot-toast'],
  }
};

module.exports = nextConfig; 