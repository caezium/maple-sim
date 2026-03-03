import { createMDX } from 'fumadocs-mdx/next';

const withMDX = createMDX();

const basePath = process.env.BASE_PATH ?? ""

/** @type {import('next').NextConfig} */
const config = {
  reactStrictMode: true,
  devIndicators: false,
  output: "export",
  pageExtensions: ["ts", "tsx", "mdx"],
  basePath,
  images: {
    unoptimized: true
  },
  env: {
    BASE_PATH: basePath
  }
};

export default withMDX(config);
