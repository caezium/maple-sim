import defaultMdxComponents from 'fumadocs-ui/mdx';
import * as TabsComponents from 'fumadocs-ui/components/tabs';
import type { MDXComponents } from 'mdx/types';
import type { ImgHTMLAttributes } from 'react';

const basePath = process.env.BASE_PATH ?? '';

type ImageSource = string | { src?: string };

function resolveImageSource(src: ImageSource | undefined): string | undefined {
  if (!src) return undefined;
  let value =
    typeof src === 'string'
      ? src
      : src.src ?? (src as { default?: string }).default;
  if (!value) return undefined;
  value = value.replace(/%2F/gi, '/');
  if (value.startsWith('../media/')) value = value.replace('../media/', '/media/');
  if (value.startsWith('./')) value = value.slice(1);
  if (value.startsWith('media/')) value = `/${value}`;
  if (value.startsWith('/')) {
    return `${basePath}${value}`.replace(/ /g, '%20');
  }
  return value.replace(/ /g, '%20');
}

function MdxImage({
  src,
  alt = '',
  ...rest
}: ImgHTMLAttributes<HTMLImageElement> & { src?: ImageSource }) {
  const resolved = resolveImageSource(src);
  return <img src={resolved} alt={alt} {...rest} />;
}

// use this function to get MDX components, you will need it for rendering MDX
export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultMdxComponents,
    ...TabsComponents,
    img: MdxImage,
    ...components,
  };
}
