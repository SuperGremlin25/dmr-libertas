/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['localhost'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL + '/:path*',
      },
    ];
  },
  webpack(config) {
    // Add support for importing SVGs as React components
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    });

    return config;
  },
  // Enable static exports for standalone Docker image
  output: 'standalone',
  // Enable experimental features if needed
  experimental: {
    // Enable server components
    serverComponents: true,
    // Enable concurrent features
    concurrentFeatures: true,
    // Enable new link behavior
    newNextLinkBehavior: true,
  },
  // Configure webpack for better bundle analysis in production
  webpack: (config, { isServer }) => {
    // Add source maps in development
    if (!isServer) {
      config.devtool = 'source-map';
    }

    // Add support for loading WebAssembly modules
    config.experiments = {
      ...config.experiments,
      asyncWebAssembly: true,
      layers: true,
    };

    return config;
  },
};

module.exports = nextConfig;
