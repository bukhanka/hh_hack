import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactStrictMode: true,
  
  // Allow images from external sources
  images: {
    domains: ['localhost'],
  },
};

export default nextConfig;
