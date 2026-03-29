import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { seoContent } from './seo/content.mjs'
import { renderSeoPage } from './seo/renderers.mjs'
import { SITE, toAbsoluteUrl } from './seo/site-config.mjs'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const publicDir = path.resolve(__dirname, '../public')

function getBreadcrumbs(locale, page) {
  const isZh = locale === 'zh-CN'
  const homeLabel = isZh ? '首页' : 'Home'
  const localeLabel = isZh ? '中文入口' : 'English Hub'

  const breadcrumbs = [{ label: homeLabel, path: '/' }]

  if (page.path !== (isZh ? '/zh/' : '/en/')) {
    breadcrumbs.push({ label: localeLabel, path: isZh ? '/zh/' : '/en/' })
  }

  breadcrumbs.push({ label: page.h1, path: page.path })
  return breadcrumbs
}

function getAlternates(locale, page) {
  const counterpartPath = locale === 'zh-CN'
    ? page.path.replace(/^\/zh\//, '/en/')
    : page.path.replace(/^\/en\//, '/zh/')

  return [
    { hrefLang: 'zh-CN', path: locale === 'zh-CN' ? page.path : counterpartPath },
    { hrefLang: 'en', path: locale === 'en' ? page.path : counterpartPath },
    { hrefLang: 'x-default', path: '/' },
  ]
}

function normalizeOutputPath(pagePath) {
  if (pagePath === '/zh/' || pagePath === '/en/') {
    return `${pagePath.slice(1)}index.html`
  }

  return `${pagePath.replace(/^\/+/, '').replace(/\/+$/, '')}/index.html`
}

function collectPages() {
  return [
    { locale: 'zh-CN', page: seoContent.zh.hub },
    { locale: 'en', page: seoContent.en.hub },
    ...seoContent.zh.platforms.map((page) => ({ locale: 'zh-CN', page })),
    ...seoContent.en.platforms.map((page) => ({ locale: 'en', page })),
    ...seoContent.zh.features.map((page) => ({ locale: 'zh-CN', page })),
    ...seoContent.en.features.map((page) => ({ locale: 'en', page })),
    { locale: 'zh-CN', page: seoContent.zh.faq },
    { locale: 'en', page: seoContent.en.faq },
  ]
}

function buildSitemap(urls) {
  const items = urls
    .map((url) => `  <url>\n    <loc>${url}</loc>\n  </url>`)
    .join('\n')

  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${items}\n</urlset>\n`
}

function buildRobots() {
  return `User-agent: *\nAllow: /\n\nSitemap: ${toAbsoluteUrl('/sitemap.xml')}\n`
}

export function generateSiteFiles() {
  const pages = {}
  const urls = [toAbsoluteUrl('/')]

  for (const entry of collectPages()) {
    const breadcrumbs = getBreadcrumbs(entry.locale, entry.page)
    const alternates = getAlternates(entry.locale, entry.page)
    const outputPath = normalizeOutputPath(entry.page.path)

    pages[outputPath] = renderSeoPage({
      locale: entry.locale,
      page: entry.page,
      alternates,
      breadcrumbs,
    })

    urls.push(toAbsoluteUrl(entry.page.path))
  }

  return {
    pages,
    sitemap: buildSitemap(urls),
    robots: buildRobots(),
  }
}

export function writeGeneratedFiles(files = generateSiteFiles()) {
  fs.mkdirSync(publicDir, { recursive: true })

  for (const [relativePath, html] of Object.entries(files.pages)) {
    const absolutePath = path.join(publicDir, relativePath)
    fs.mkdirSync(path.dirname(absolutePath), { recursive: true })
    fs.writeFileSync(absolutePath, html, 'utf8')
  }

  fs.writeFileSync(path.join(publicDir, 'sitemap.xml'), files.sitemap, 'utf8')
  fs.writeFileSync(path.join(publicDir, 'robots.txt'), files.robots, 'utf8')
}

const isDirectRun = process.argv[1] && path.resolve(process.argv[1]) === __filename

if (isDirectRun) {
  writeGeneratedFiles()
}
