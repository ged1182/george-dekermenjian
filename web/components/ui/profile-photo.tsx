"use client";

import { useState } from "react";
import Image from "next/image";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

interface ProfilePhotoProps {
  src: string;
  alt: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizeClasses = {
  sm: "size-12",
  md: "size-16",
  lg: "size-20",
};

const sizePx = {
  sm: 48,
  md: 64,
  lg: 80,
};

export function ProfilePhoto({ src, alt, size = "md", className }: ProfilePhotoProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Thumbnail - clickable */}
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className={cn(
          "ring-primary/20 hover:ring-primary/40 focus:ring-primary relative shrink-0 cursor-pointer overflow-hidden rounded-full ring-2 transition-all hover:scale-105 focus:outline-none",
          sizeClasses[size],
          className
        )}
        aria-label={`View ${alt} full size`}
      >
        <Image
          src={src}
          alt={alt}
          fill
          className="object-cover"
          sizes={`${sizePx[size]}px`}
          priority
        />
      </button>

      {/* Modal with larger photo */}
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="overflow-hidden border-none bg-transparent p-0 shadow-2xl sm:max-w-md">
          <DialogTitle className="sr-only">{alt}</DialogTitle>
          <div className="relative aspect-square w-full max-w-md overflow-hidden rounded-xl">
            <Image
              src={src}
              alt={alt}
              fill
              className="object-cover"
              sizes="(max-width: 768px) 100vw, 448px"
              priority
            />
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
