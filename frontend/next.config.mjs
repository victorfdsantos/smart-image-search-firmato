

const nextConfig = {
  // Enables standalone build for minimal Docker image
  output: "standalone",

  // Proxy /api/* → backend. Works in dev and in any cloud deployment.
  async rewrites() {
    const apiBase = process.env.API_BASE ?? "http://localhost:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${apiBase}/:path*`,
      },
    ];
  },
  images: {
    remotePatterns: [
      { protocol: "http", hostname: "**" },
      { protocol: "https", hostname: "**" },
    ],
  },
};

export default nextConfig;
