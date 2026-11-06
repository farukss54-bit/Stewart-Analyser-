import type { NextConfig } from "next";

// Python API adresi. Tarayıcı yalnızca bu uygulamaya (aynı kaynak) istek atar,
// /api/* istekleri sunucu tarafında API'ye yönlendirilir; CORS gerekmez.
const apiUrl = process.env.STEWART_API_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  /* config options here */
  cacheComponents: true,
  partialPrefetching: true,
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${apiUrl}/api/:path*` }];
  },
};

export default nextConfig;
