export const SITE = {
  brandName: 'VidGrab',
  baseUrl: 'https://vidgrab.sunandyu.top',
  defaultOgImage: '/og/default-share-cover.svg',
}

export function toAbsoluteUrl(path) {
  return `${SITE.baseUrl}${path}`
}
