/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  experimental: {
    // Next's dev rewrite proxy defaults to a 30s timeout and answers with a bare
    // "500 Internal Server Error" when it trips. Model discovery, connectivity
    // sweeps and debate turns all legitimately run longer than that.
    proxyTimeout: 600000,
  },
  rewrites: async () => {
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
