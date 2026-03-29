import { SITE, toAbsoluteUrl } from './site-config.mjs'

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

function escapeJson(value) {
  return JSON.stringify(value).replaceAll('</script', '<\\/script')
}

export function buildMetaTags(page) {
  const canonicalUrl = toAbsoluteUrl(page.path)
  const imageUrl = toAbsoluteUrl(page.image || SITE.defaultOgImage)
  const keywords = page.keywords.join(', ')

  return [
    `<title>${escapeHtml(page.title)}</title>`,
    `<meta name="description" content="${escapeHtml(page.description)}" />`,
    `<meta name="keywords" content="${escapeHtml(keywords)}" />`,
    '<meta name="robots" content="index, follow" />',
    `<link rel="canonical" href="${escapeHtml(canonicalUrl)}" />`,
    `<meta property="og:title" content="${escapeHtml(page.title)}" />`,
    `<meta property="og:description" content="${escapeHtml(page.description)}" />`,
    `<meta property="og:type" content="${escapeHtml(page.ogType || 'website')}" />`,
    `<meta property="og:url" content="${escapeHtml(canonicalUrl)}" />`,
    `<meta property="og:image" content="${escapeHtml(imageUrl)}" />`,
    `<meta property="og:site_name" content="${escapeHtml(SITE.brandName)}" />`,
    `<meta property="og:locale" content="${escapeHtml(page.locale)}" />`,
    '<meta name="twitter:card" content="summary_large_image" />',
    `<meta name="twitter:title" content="${escapeHtml(page.title)}" />`,
    `<meta name="twitter:description" content="${escapeHtml(page.description)}" />`,
    `<meta name="twitter:image" content="${escapeHtml(imageUrl)}" />`,
  ].join('\n')
}

export function buildAlternateLinks(alternates) {
  return alternates
    .map((alternate) => `<link rel="alternate" hreflang="${escapeHtml(alternate.hrefLang)}" href="${escapeHtml(toAbsoluteUrl(alternate.path))}" />`)
    .join('\n')
}

export function buildJsonLdScripts(items) {
  return items
    .map((item) => `<script type="application/ld+json">${escapeJson(item)}</script>`)
    .join('\n')
}

export function buildBreadcrumbJsonLd(page, breadcrumbs) {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: breadcrumbs.map((breadcrumb, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: breadcrumb.label,
      item: toAbsoluteUrl(breadcrumb.path),
    })),
  }
}

export function buildFaqJsonLd(page) {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: page.faqs.map((faq) => ({
      '@type': 'Question',
      name: faq.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: faq.answer,
      },
    })),
  }
}

export function buildWebPageJsonLd(page) {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    name: page.title,
    description: page.description,
    url: toAbsoluteUrl(page.path),
    inLanguage: page.locale,
  }
}

export function buildHomeJsonLd() {
  const website = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: SITE.brandName,
    url: SITE.baseUrl,
    description: SITE.productTagline,
  }

  const organization = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: SITE.brandName,
    url: SITE.baseUrl,
    logo: toAbsoluteUrl(SITE.defaultOgImage),
  }

  const webApp = {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: SITE.brandName,
    applicationCategory: 'MultimediaApplication',
    operatingSystem: 'Web',
    url: SITE.baseUrl,
    description: 'Download public videos, export transcripts, and generate AI summaries in one workflow.',
  }

  return [website, organization, webApp]
}

function renderSection(section) {
  return `
    <section class="seo-section">
      <h2>${escapeHtml(section.title)}</h2>
      ${section.paragraphs.map((paragraph) => `<p>${escapeHtml(paragraph)}</p>`).join('\n')}
    </section>
  `
}

function renderRelatedLinks(links) {
  if (!links?.length) {
    return ''
  }

  return `
    <section class="seo-section">
      <h2>Related Pages</h2>
      <ul class="seo-link-list">
        ${links.map((link) => `<li><a href="${escapeHtml(link.path)}">${escapeHtml(link.label)}</a></li>`).join('\n')}
      </ul>
    </section>
  `
}

function renderFaqBlock(page) {
  if (!page.faqs?.length) {
    return ''
  }

  return `
    <section class="seo-section">
      <h2>${page.locale === 'zh-CN' ? '常见问题' : 'Frequently asked questions'}</h2>
      <div class="faq-list">
        ${page.faqs
          .map(
            (faq) => `
              <article class="faq-item">
                <h3>${escapeHtml(faq.question)}</h3>
                <p>${escapeHtml(faq.answer)}</p>
              </article>
            `,
          )
          .join('\n')}
      </div>
    </section>
  `
}

export function renderSeoPage({
  locale,
  page,
  alternates,
  breadcrumbs,
}) {
  const jsonLdItems = [
    buildWebPageJsonLd({ ...page, locale }),
    buildBreadcrumbJsonLd({ ...page, locale }, breadcrumbs),
  ]

  if (page.faqs?.length) {
    jsonLdItems.push(buildFaqJsonLd(page))
  }

  const ctaText = locale === 'zh-CN' ? '返回首页开始使用 VidGrab' : 'Go to the homepage and start using VidGrab'
  const relatedHeading = locale === 'zh-CN' ? '相关页面' : 'Related Pages'

  return `<!doctype html>
<html lang="${locale === 'zh-CN' ? 'zh-CN' : 'en'}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    ${buildMetaTags({
      ...page,
      locale,
      ogType: page.faqs?.length ? 'article' : 'website',
    })}
    ${buildAlternateLinks(alternates)}
    ${buildJsonLdScripts(jsonLdItems)}
    <style>
      :root {
        color-scheme: light;
        --bg: #f8fafc;
        --card: #ffffff;
        --text: #0f172a;
        --muted: #475569;
        --border: #e2e8f0;
        --accent: #1777ff;
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: "Outfit", "PingFang SC", "Microsoft YaHei", sans-serif;
        background: var(--bg);
        color: var(--text);
      }
      a { color: var(--accent); text-decoration: none; }
      a:hover { text-decoration: underline; }
      .page {
        max-width: 960px;
        margin: 0 auto;
        padding: 48px 20px 80px;
      }
      .hero, .seo-section, .cta-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 20px;
      }
      .eyebrow {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        background: #eff6ff;
        color: #1d4ed8;
        font-size: 12px;
        font-weight: 600;
        padding: 6px 12px;
        margin-bottom: 16px;
      }
      h1 {
        font-size: clamp(2rem, 5vw, 3.25rem);
        line-height: 1.1;
        margin: 0 0 12px;
      }
      h2 {
        font-size: 1.25rem;
        margin: 0 0 12px;
      }
      h3 {
        font-size: 1rem;
        margin: 0 0 8px;
      }
      p, li {
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.75;
      }
      .breadcrumbs {
        font-size: 14px;
        color: var(--muted);
        margin-bottom: 16px;
      }
      .seo-link-list {
        margin: 0;
        padding-left: 20px;
      }
      .cta-card {
        display: flex;
        flex-direction: column;
        gap: 14px;
      }
      .cta-link {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: fit-content;
        min-width: 220px;
        padding: 12px 18px;
        border-radius: 999px;
        background: var(--accent);
        color: #ffffff;
        font-weight: 600;
      }
      .faq-list {
        display: grid;
        gap: 16px;
      }
    </style>
  </head>
  <body>
    <main class="page">
      <nav class="breadcrumbs">
        ${breadcrumbs.map((breadcrumb) => `<a href="${escapeHtml(breadcrumb.path)}">${escapeHtml(breadcrumb.label)}</a>`).join(' / ')}
      </nav>
      <section class="hero">
        <span class="eyebrow">${escapeHtml(SITE.brandName)}</span>
        <h1>${escapeHtml(page.h1)}</h1>
        <p>${escapeHtml(page.intro)}</p>
      </section>
      ${page.sections.map((section) => renderSection(section)).join('\n')}
      ${page.faqs?.length ? renderFaqBlock(page) : ''}
      <section class="seo-section">
        <h2>${escapeHtml(relatedHeading)}</h2>
        <ul class="seo-link-list">
          ${page.relatedLinks.map((link) => `<li><a href="${escapeHtml(link.path)}">${escapeHtml(link.label)}</a></li>`).join('\n')}
        </ul>
      </section>
      <section class="cta-card">
        <h2>${locale === 'zh-CN' ? '开始使用 VidGrab' : 'Start with VidGrab'}</h2>
        <p>${locale === 'zh-CN' ? '回到工具首页，粘贴公开视频链接，继续完成下载、字幕导出或 AI 总结。' : 'Return to the main tool, paste a public video URL, and continue with download, transcript export, or AI summary.'}</p>
        <a class="cta-link" href="/">${escapeHtml(ctaText)}</a>
      </section>
    </main>
  </body>
</html>`
}
