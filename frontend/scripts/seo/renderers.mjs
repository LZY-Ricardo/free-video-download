import { SITE, toAbsoluteUrl } from './site-config.mjs'

export function buildMetaTags({ locale, path, title, description, keywords, image }) {
  const canonicalUrl = toAbsoluteUrl(path)
  const ogImage = toAbsoluteUrl(image || SITE.defaultOgImage)
  const kw = Array.isArray(keywords) ? keywords.join(',') : keywords
  return [
    `<link rel="canonical" href="${canonicalUrl}" />`,
    `<meta name="description" content="${esc(description)}" />`,
    `<meta name="keywords" content="${esc(kw)}" />`,
    `<meta name="robots" content="index,follow" />`,
    `<meta property="og:title" content="${esc(title)}" />`,
    `<meta property="og:description" content="${esc(description)}" />`,
    `<meta property="og:type" content="website" />`,
    `<meta property="og:url" content="${canonicalUrl}" />`,
    `<meta property="og:image" content="${ogImage}" />`,
    `<meta property="og:site_name" content="${SITE.brandName}" />`,
    `<meta name="twitter:card" content="summary_large_image" />`,
    `<meta name="twitter:title" content="${esc(title)}" />`,
    `<meta name="twitter:description" content="${esc(description)}" />`,
    `<meta name="twitter:image" content="${ogImage}" />`,
  ].join('\n    ')
}

export function buildAlternateLinks(alternatesOrOptions) {
  if (Array.isArray(alternatesOrOptions)) {
    return alternatesOrOptions
      .map(a => `<link rel="alternate" hreflang="${a.hrefLang}" href="${toAbsoluteUrl(a.path)}" />`)
      .join('\n    ')
  }
  const { currentPath, alternatePath } = alternatesOrOptions
  const zhPath = currentPath.startsWith('/zh/') ? currentPath : alternatePath
  const enPath = currentPath.startsWith('/en/') ? currentPath : alternatePath
  return [
    `<link rel="alternate" hreflang="zh-CN" href="${toAbsoluteUrl(zhPath)}" />`,
    `<link rel="alternate" hreflang="en" href="${toAbsoluteUrl(enPath)}" />`,
    `<link rel="alternate" hreflang="x-default" href="${toAbsoluteUrl('/')}" />`,
  ].join('\n    ')
}

export function buildJsonLdScripts(jsonLds) {
  return jsonLds.map(j => `<script type="application/ld+json">${JSON.stringify(j)}</script>`).join('\n    ')
}

export function buildBreadcrumbJsonLd(pageOrBreadcrumbs, breadcrumbsArg) {
  const breadcrumbs = Array.isArray(pageOrBreadcrumbs) ? pageOrBreadcrumbs : (breadcrumbsArg || [])
  const items = breadcrumbs.map((b, i) => ({
    '@type': 'ListItem',
    position: i + 1,
    name: b.label,
    item: toAbsoluteUrl(b.path),
  }))
  return JSON.stringify({ '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: items }, null, 2)
}

export function buildWebPageJsonLd({ title, description, path }) {
  return JSON.stringify({
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    name: title,
    description,
    url: toAbsoluteUrl(path),
  }, null, 2)
}

function buildFaqJsonLd(faqs) {
  return JSON.stringify({
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map(f => ({
      '@type': 'Question',
      name: f.q,
      acceptedAnswer: { '@type': 'Answer', text: f.a },
    })),
  }, null, 2)
}

function esc(str) {
  return String(str).replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function baseHtml({ locale, title, metaTags, alternateLinks, jsonLds, body }) {
  const lang = locale === 'zh-CN' ? 'zh-CN' : 'en'
  const jsonLdBlocks = jsonLds.map(j => `<script type="application/ld+json">${j}</script>`).join('\n    ')
  return `<!doctype html>
<html lang="${lang}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${esc(title)}</title>
  ${metaTags}
  ${alternateLinks}
  ${jsonLdBlocks}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:Outfit,'PingFang SC','Microsoft YaHei',sans-serif;background:#f8fafc;color:#0f172a;line-height:1.7}
    .wrap{max-width:860px;margin:0 auto;padding:32px 20px}
    nav.bc{font-size:13px;color:#64748b;margin-bottom:24px}
    nav.bc a{color:#1d4ed8;text-decoration:none}nav.bc span{margin:0 6px}
    h1{font-size:clamp(22px,4vw,34px);font-weight:700;margin-bottom:16px;color:#0f172a}
    h2{font-size:18px;font-weight:600;margin:28px 0 10px;color:#1e293b}
    h3{font-size:15px;font-weight:600;margin:18px 0 6px}
    p{margin-bottom:12px;color:#334155}
    ul,ol{padding-left:20px;margin-bottom:12px}
    li{margin-bottom:6px;color:#334155}
    .cta{display:inline-block;margin-top:24px;padding:12px 28px;background:#1d4ed8;color:#fff;border-radius:8px;text-decoration:none;font-weight:600;font-size:15px}
    .cta:hover{background:#1e40af}
    .card{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:20px;margin-bottom:12px}
    .links{margin-top:32px;display:flex;flex-wrap:wrap;gap:12px}
    .links a{color:#1d4ed8;text-decoration:none;font-size:14px;padding:6px 14px;border:1px solid #bfdbfe;border-radius:6px}
    table{width:100%;border-collapse:collapse;margin-bottom:16px}
    th,td{padding:10px 14px;border:1px solid #e2e8f0;font-size:14px;text-align:left}
    th{background:#f1f5f9;font-weight:600}
    header.site-header{background:#fff;border-bottom:1px solid #e2e8f0;padding:12px 20px;display:flex;align-items:center;gap:12px}
    header.site-header a{color:#0f172a;text-decoration:none;font-weight:700;font-size:18px}
    footer.site-footer{margin-top:48px;border-top:1px solid #e2e8f0;padding:24px 20px;text-align:center;font-size:13px;color:#94a3b8}
  </style>
</head>
<body>
  <header class="site-header">
    <a href="/">&#9654; VidGrab</a>
  </header>
  <div class="wrap">
    ${body}
  </div>
  <footer class="site-footer">© 2026 VidGrab · <a href="/" style="color:#1d4ed8">返回首页</a></footer>
</body>
</html>`
}

function renderBreadcrumb(breadcrumbs) {
  const parts = breadcrumbs.map((b, i) =>
    i < breadcrumbs.length - 1
      ? `<a href="${b.path}">${b.label}</a><span>/</span>`
      : `<span>${b.label}</span>`
  ).join(' ')
  return `<nav class="bc" aria-label="breadcrumb">${parts}</nav>`
}

export function renderSeoPage({ locale, page, alternates, breadcrumbs }) {
  const isZh = locale === 'zh-CN'
  const metaTags = buildMetaTags({ locale, path: page.path, title: page.title, description: page.description, keywords: page.keywords })
  const alternateLinks = buildAlternateLinks({
    currentPath: page.path,
    alternatePath: alternates.find(a => a.hrefLang !== locale && a.hrefLang !== 'x-default')?.path || page.path,
  })
  const jsonLds = [
    buildWebPageJsonLd({ title: page.title, description: page.description, path: page.path }),
    buildBreadcrumbJsonLd(breadcrumbs),
  ]
  if (page.faqs) jsonLds.push(buildFaqJsonLd(page.faqs))

  const relatedLinks = (page.related || []).map(r => `<a href="${r.path}">${r.label}</a>`).join('')
  const faqHtml = page.faqs ? `<h2>${isZh ? '常见问题' : 'FAQ'}</h2>` + page.faqs.map(f =>
    `<div class="card"><h3>${f.q}</h3><p>${f.a}</p></div>`
  ).join('') : ''

  const body = `
    ${renderBreadcrumb(breadcrumbs)}
    <h1>${page.h1}</h1>
    ${(page.sections || []).map(s => `<h2>${s.heading}</h2>${s.paragraphs.map(p => `<p>${p}</p>`).join('')}${(s.items || []).length ? '<ul>' + s.items.map(i => `<li>${i}</li>`).join('') + '</ul>' : ''}`).join('')}
    ${faqHtml}
    ${relatedLinks ? `<div class="links">${relatedLinks}</div>` : ''}
    <a class="cta" href="/">${isZh ? '立即使用 VidGrab' : 'Try VidGrab Now'}</a>
  `
  return baseHtml({ locale, title: page.title, metaTags, alternateLinks, jsonLds, body })
}
