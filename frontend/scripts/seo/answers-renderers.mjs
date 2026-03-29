import {
  buildAlternateLinks,
  buildBreadcrumbJsonLd,
  buildJsonLdScripts,
  buildMetaTags,
  buildWebPageJsonLd,
} from './renderers.mjs'

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

export function buildHowToJsonLd(page) {
  return {
    '@context': 'https://schema.org',
    '@type': 'HowTo',
    name: page.title,
    step: page.steps.map((step, index) => ({
      '@type': 'HowToStep',
      position: index + 1,
      name: step.name,
      text: step.text,
    })),
  }
}

function buildFaqJsonLd(page) {
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

function buildBaseJsonLd(locale, page, breadcrumbs) {
  return [
    buildWebPageJsonLd({ ...page, locale }),
    buildBreadcrumbJsonLd({ ...page, locale }, breadcrumbs),
  ]
}

function renderSections(page) {
  return page.sections
    .map(
      (section) => `
        <section class="answer-section">
          <h2>${escapeHtml(section.title)}</h2>
          ${section.paragraphs.map((paragraph) => `<p>${escapeHtml(paragraph)}</p>`).join('\n')}
        </section>
      `,
    )
    .join('\n')
}

function renderFaqItems(page, locale) {
  if (!page.faqs?.length) {
    return ''
  }

  return `
    <section class="answer-section">
      <h2>${locale === 'zh-CN' ? '相关问答' : 'Related questions'}</h2>
      <div class="answer-list">
        ${page.faqs
          .map(
            (faq) => `
              <article class="answer-item">
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

function renderHowToSteps(page, locale) {
  if (!page.steps?.length) {
    return ''
  }

  return `
    <section class="answer-section">
      <h2>${locale === 'zh-CN' ? '操作步骤' : 'Steps'}</h2>
      <ol class="step-list">
        ${page.steps
          .map(
            (step) => `
              <li class="step-item">
                <strong>${escapeHtml(step.name)}</strong>
                <p>${escapeHtml(step.text)}</p>
              </li>
            `,
          )
          .join('\n')}
      </ol>
    </section>
  `
}

function renderComparisonTable(page, locale) {
  if (!page.comparisonTable) {
    return ''
  }

  return `
    <section class="answer-section">
      <h2>${locale === 'zh-CN' ? '核心差异表' : 'Key comparison table'}</h2>
      <div class="comparison-wrapper">
        <table class="comparison-table">
          <thead>
            <tr>
              ${page.comparisonTable.headers.map((header) => `<th>${escapeHtml(header)}</th>`).join('')}
            </tr>
          </thead>
          <tbody>
            ${page.comparisonTable.rows
              .map(
                (row) => `
                  <tr>
                    ${row.map((cell) => `<td>${escapeHtml(cell)}</td>`).join('')}
                  </tr>
                `,
              )
              .join('\n')}
          </tbody>
        </table>
      </div>
    </section>
  `
}

function renderRelatedLinks(page, locale) {
  return `
    <section class="answer-section">
      <h2>${locale === 'zh-CN' ? '继续查看' : 'Continue exploring'}</h2>
      <ul class="related-links">
        ${page.relatedLinks.map((link) => `<li><a href="${escapeHtml(link.path)}">${escapeHtml(link.label)}</a></li>`).join('\n')}
      </ul>
    </section>
  `
}

function renderAnswerLayout({ locale, page, alternates, breadcrumbs, jsonLdItems, extraBlock = '' }) {
  return `<!doctype html>
<html lang="${locale === 'zh-CN' ? 'zh-CN' : 'en'}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    ${buildMetaTags({
      ...page,
      locale,
      ogType: 'article',
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
      body { margin: 0; font-family: "Outfit", "PingFang SC", "Microsoft YaHei", sans-serif; background: var(--bg); color: var(--text); }
      a { color: var(--accent); text-decoration: none; }
      a:hover { text-decoration: underline; }
      .page { max-width: 980px; margin: 0 auto; padding: 48px 20px 80px; }
      .hero, .answer-section, .cta-card { background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 28px; margin-bottom: 20px; }
      .eyebrow { display: inline-flex; align-items: center; border-radius: 999px; background: #eff6ff; color: #1d4ed8; font-size: 12px; font-weight: 600; padding: 6px 12px; margin-bottom: 16px; }
      .direct-answer { font-size: 1.05rem; line-height: 1.8; color: var(--text); margin: 0; }
      h1 { font-size: clamp(2rem, 5vw, 3.25rem); line-height: 1.1; margin: 0 0 12px; }
      h2 { font-size: 1.25rem; margin: 0 0 12px; }
      h3 { font-size: 1rem; margin: 0 0 8px; }
      p, li, td, th { color: var(--muted); font-size: 1rem; line-height: 1.75; }
      .breadcrumbs { font-size: 14px; color: var(--muted); margin-bottom: 16px; }
      .answer-list, .step-list, .related-links { margin: 0; padding-left: 20px; }
      .answer-item + .answer-item, .step-item + .step-item { margin-top: 12px; }
      .comparison-wrapper { overflow-x: auto; }
      .comparison-table { width: 100%; border-collapse: collapse; }
      .comparison-table th, .comparison-table td { border: 1px solid var(--border); padding: 12px; text-align: left; }
      .comparison-table th { background: #eff6ff; color: var(--text); }
      .cta-link { display: inline-flex; align-items: center; justify-content: center; width: fit-content; min-width: 220px; padding: 12px 18px; border-radius: 999px; background: var(--accent); color: #ffffff; font-weight: 600; }
    </style>
  </head>
  <body>
    <main class="page">
      <nav class="breadcrumbs">
        ${breadcrumbs.map((breadcrumb) => `<a href="${escapeHtml(breadcrumb.path)}">${escapeHtml(breadcrumb.label)}</a>`).join(' / ')}
      </nav>
      <section class="hero">
        <span class="eyebrow">VidGrab Answers</span>
        <h1>${escapeHtml(page.h1)}</h1>
        <p class="direct-answer">${escapeHtml(page.answer)}</p>
      </section>
      ${extraBlock}
      ${renderSections(page)}
      ${renderFaqItems(page, locale)}
      ${renderRelatedLinks(page, locale)}
      <section class="cta-card">
        <h2>${locale === 'zh-CN' ? '回到 VidGrab 工具页继续操作' : 'Return to the VidGrab tool'}</h2>
        <p>${locale === 'zh-CN' ? '如果这条答案正好适合你的场景，可以回到首页，把公开视频链接粘贴进去继续下载、导出字幕或生成 AI 总结。' : 'If this answer matches your use case, go back to the homepage and continue with download, subtitle export, or AI summaries there.'}</p>
        <a class="cta-link" href="/">${locale === 'zh-CN' ? '打开首页工具' : 'Open the homepage tool'}</a>
      </section>
    </main>
  </body>
</html>`
}

export function renderFaqAnswerPage({ locale, page, alternates, breadcrumbs }) {
  return renderAnswerLayout({
    locale,
    page,
    alternates,
    breadcrumbs,
    jsonLdItems: [...buildBaseJsonLd(locale, page, breadcrumbs), buildFaqJsonLd(page)],
  })
}

export function renderHowToAnswerPage({ locale, page, alternates, breadcrumbs }) {
  return renderAnswerLayout({
    locale,
    page,
    alternates,
    breadcrumbs,
    jsonLdItems: [...buildBaseJsonLd(locale, page, breadcrumbs), buildHowToJsonLd(page)],
    extraBlock: renderHowToSteps(page, locale),
  })
}

export function renderCompareAnswerPage({ locale, page, alternates, breadcrumbs }) {
  return renderAnswerLayout({
    locale,
    page,
    alternates,
    breadcrumbs,
    jsonLdItems: buildBaseJsonLd(locale, page, breadcrumbs),
    extraBlock: renderComparisonTable(page, locale),
  })
}
