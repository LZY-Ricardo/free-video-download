export const SITE = {
  brandName: 'VidGrab',
  productTagline: 'AI Video Downloader & Summarizer',
  baseUrl: 'https://vidgrab.sunandyu.top',
  defaultOgImage: '/og/default-share-cover.svg',
  defaultLocale: 'en',
}

export const SUPPORTED_LOCALES = ['zh-CN', 'en']

export function toAbsoluteUrl(pathname) {
  if (!pathname) {
    return SITE.baseUrl
  }

  if (pathname.startsWith('http://') || pathname.startsWith('https://')) {
    return pathname
  }

  const normalizedPath = pathname.startsWith('/') ? pathname : `/${pathname}`
  return `${SITE.baseUrl}${normalizedPath}`
}
