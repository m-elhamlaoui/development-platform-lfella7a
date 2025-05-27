'use client';

import Image, { ImageProps } from 'next/image';
import { useState } from 'react';

type ImageWithFallbackProps = ImageProps & {
  fallbackStyle?: React.CSSProperties;
};

export default function ImageWithFallback({
  fallbackStyle,
  ...props
}: ImageWithFallbackProps) {
  const [error, setError] = useState(false);

  return (
    <Image
      {...props}
      onError={() => setError(true)}
      style={{
        ...props.style,
        ...(error ? fallbackStyle || { display: 'none' } : {}),
      }}
    />
  );
} 