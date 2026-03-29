const zhHomeSections = [
  {
    title: '为什么使用 VidGrab',
    paragraphs: [
      'VidGrab 将视频下载、字幕提取和 AI 视频总结整合到一个轻量工具里，帮助学习者和内容创作者更快获取关键信息。',
      '你可以用同一个入口完成链接解析、格式选择、字幕下载和智能问答，减少在多个工具之间切换的成本。',
    ],
  },
  {
    title: '适合哪些场景',
    paragraphs: [
      '适合课程复盘、素材收集、跨平台视频保存、长视频要点提炼，以及把公开视频整理成可搜索的学习资料。',
    ],
  },
  {
    title: '如何开始',
    paragraphs: [
      '把视频链接粘贴到首页，解析视频后即可选择下载格式，或直接使用 AI 学习助手生成摘要、字幕和思维导图。',
    ],
  },
]

const enHomeSections = [
  {
    title: 'Why use VidGrab',
    paragraphs: [
      'VidGrab combines video downloading, subtitle extraction, and AI summarization in one lightweight workflow for learners and creators.',
      'Paste a link once and keep moving from parsing to download, transcript export, and AI Q&A without switching tools.',
    ],
  },
  {
    title: 'Common use cases',
    paragraphs: [
      'Use VidGrab for lecture review, research clipping, creator asset collection, and turning long-form videos into searchable notes.',
    ],
  },
  {
    title: 'How it works',
    paragraphs: [
      'Paste a public video URL on the homepage, inspect the available formats, then download the file or launch the AI assistant for summaries and transcripts.',
    ],
  },
]

function makePlatformPage(locale, slug, title, platformName, featureLinks) {
  const isZh = locale === 'zh-CN'

  return {
    slug,
    path: `/${isZh ? 'zh' : 'en'}/platforms/${slug}`,
    title: isZh
      ? `${platformName} 视频下载器 - VidGrab | 在线解析、下载与 AI 总结`
      : `${platformName} Video Downloader - VidGrab | Download, Transcript and AI Summary`,
    description: isZh
      ? `使用 VidGrab 在线解析 ${platformName} 视频，支持视频下载、字幕提取、音频保存和 AI 内容总结，帮助你更高效整理学习与创作素材。`
      : `Use VidGrab to download ${platformName} videos online, export subtitles, save audio, and generate AI summaries for study and creator workflows.`,
    keywords: isZh
      ? [`${platformName} 视频下载器`, `${platformName} 下载`, `${platformName} 字幕下载`, '视频总结', 'VidGrab']
      : [`${platformName} downloader`, `${platformName} transcript`, `${platformName} video summary`, 'video downloader', 'VidGrab'],
    h1: isZh ? `${platformName} 视频下载与 AI 总结工具` : `${platformName} video downloader and AI summarizer`,
    intro: isZh
      ? `VidGrab 为 ${platformName} 视频提供下载、转录和内容总结能力，适合学习、存档和创作整理。`
      : `VidGrab helps you download, transcribe, and summarize ${platformName} videos for learning, archiving, and content workflows.`,
    sections: isZh
      ? [
          {
            title: `VidGrab 如何支持 ${platformName}`,
            paragraphs: [
              `你可以用 VidGrab 解析 ${platformName} 链接，查看可用格式，并在一个界面中继续完成字幕下载和 AI 摘要。`,
            ],
          },
          {
            title: '使用步骤',
            paragraphs: [
              '复制公开视频链接，打开首页粘贴并解析，确认视频信息后选择下载或进入 AI 学习助手。',
            ],
          },
          {
            title: '常见使用场景',
            paragraphs: [
              '适合整理课程、保存素材、提取字幕、生成章节总结和复盘公开视频内容。',
            ],
          },
        ]
      : [
          {
            title: `What you can do with ${platformName} on VidGrab`,
            paragraphs: [
              `Paste a public ${platformName} link into VidGrab to inspect available formats, export subtitles, and keep moving into AI summaries.`,
            ],
          },
          {
            title: 'How to use it',
            paragraphs: [
              'Copy a public video URL, open the homepage, paste the link, review the parsed video information, then download or launch the AI assistant.',
            ],
          },
          {
            title: 'Best-fit workflows',
            paragraphs: [
              'Use it for study notes, archive-friendly backups, transcript exports, and turning long videos into searchable knowledge.',
            ],
          },
        ],
    relatedLinks: featureLinks,
  }
}

function makeFeaturePage(locale, slug, title, featureName, relatedPlatformLinks) {
  const isZh = locale === 'zh-CN'

  return {
    slug,
    path: `/${isZh ? 'zh' : 'en'}/features/${slug}`,
    title: isZh
      ? `${featureName} - VidGrab | 视频下载与 AI 学习助手`
      : `${featureName} - VidGrab | Video Downloader and AI Study Assistant`,
    description: isZh
      ? `通过 VidGrab 使用 ${featureName}，快速完成视频保存、字幕导出和内容提炼，适合学习者、研究者和内容创作者。`
      : `Use VidGrab for ${featureName}, from downloading public videos to exporting transcripts and turning long content into concise notes.`,
    keywords: isZh
      ? [featureName, '视频下载', '字幕下载', 'AI 总结', 'VidGrab']
      : [featureName, 'video downloader', 'subtitle export', 'AI summary', 'VidGrab'],
    h1: isZh ? `${featureName}，为视频学习与整理提效` : `${featureName} for faster video workflows`,
    intro: isZh
      ? `${featureName} 是 VidGrab 的核心能力之一，帮助你把公开视频转化成更容易保存、阅读和复盘的资料。`
      : `${featureName} is one of VidGrab's core workflows for turning public videos into downloadable, searchable, and review-friendly assets.`,
    sections: isZh
      ? [
          {
            title: '这个功能解决什么问题',
            paragraphs: [
              '当你需要从公开视频里提取重点、保留证据链或整理课程内容时，这个能力可以减少手工整理时间。',
            ],
          },
          {
            title: '如何使用',
            paragraphs: [
              '从首页解析视频后，根据你的目标选择下载、字幕导出或 AI 总结入口，整个流程保持在一个页面完成。',
            ],
          },
          {
            title: '适合哪些人',
            paragraphs: [
              '适合学生、研究者、运营、剪辑师和需要管理公开视频资料的团队。',
            ],
          },
        ]
      : [
          {
            title: 'What problem this solves',
            paragraphs: [
              'This workflow helps when you need to save public videos, extract evidence, or turn long recordings into concise notes and searchable transcripts.',
            ],
          },
          {
            title: 'How to use it',
            paragraphs: [
              'Parse a video on the homepage, then choose download, subtitle export, or AI summary based on the outcome you need.',
            ],
          },
          {
            title: 'Who it is for',
            paragraphs: [
              'Students, researchers, operators, editors, and teams that need to manage public video references efficiently.',
            ],
          },
        ],
    relatedLinks: relatedPlatformLinks,
  }
}

function makeFaqPage(locale, relatedLinks) {
  const isZh = locale === 'zh-CN'
  return {
    slug: 'faq',
    path: `/${isZh ? 'zh' : 'en'}/faq`,
    title: isZh
      ? '常见问题 - VidGrab | 视频下载与 AI 总结 FAQ'
      : 'FAQ - VidGrab | Video Downloader and AI Summary Questions',
    description: isZh
      ? '查看 VidGrab 的常见问题，包括支持的平台、字幕导出、AI 总结、公开视频使用方式和工具页入口。'
      : 'Read common VidGrab questions about supported platforms, transcript export, AI summaries, public video usage, and the main tool workflow.',
    keywords: isZh
      ? ['VidGrab 常见问题', '视频下载 FAQ', 'AI 视频总结', '字幕导出', 'VidGrab']
      : ['VidGrab FAQ', 'video downloader FAQ', 'AI video summary', 'subtitle export', 'VidGrab'],
    h1: isZh ? 'VidGrab 常见问题' : 'VidGrab frequently asked questions',
    intro: isZh
      ? '以下问题帮助你快速了解 VidGrab 能做什么，以及如何把工具用于学习和内容整理。'
      : 'These answers explain what VidGrab can do and how to use it for study, archiving, and creator workflows.',
    sections: [],
    relatedLinks,
    faqs: isZh
      ? [
          {
            question: 'VidGrab 支持哪些平台？',
            answer: '当前首批 SEO 页面覆盖 YouTube、Bilibili、TikTok 和 Instagram，工具页也支持更多公开视频平台的解析流程。',
          },
          {
            question: '除了下载视频，还能做什么？',
            answer: '你可以导出字幕、查看 AI 摘要、浏览章节要点、生成思维导图，并围绕视频内容进行问答。',
          },
          {
            question: '我该从哪里开始使用？',
            answer: '直接访问首页，把公开视频链接粘贴到输入框里解析，然后按你的目标选择下载或 AI 学习助手。',
          },
        ]
      : [
          {
            question: 'Which platforms does VidGrab support?',
            answer: 'The first SEO rollout highlights YouTube, Bilibili, TikTok, and Instagram, while the main tool flow can parse additional public video sources.',
          },
          {
            question: 'Can VidGrab do more than downloading videos?',
            answer: 'Yes. You can export subtitles, read AI summaries, browse chapter-level takeaways, view a mind map, and ask questions about the video.',
          },
          {
            question: 'Where should I start?',
            answer: 'Open the homepage, paste a public video URL into the input box, parse the video, and continue with download or AI tools based on your goal.',
          },
        ],
  }
}

const zhFeatureLinks = [
  { path: '/zh/features/video-downloader', label: '视频下载' },
  { path: '/zh/features/audio-extractor', label: '音频提取' },
  { path: '/zh/features/subtitle-downloader', label: '字幕下载' },
  { path: '/zh/features/ai-video-summarizer', label: 'AI 视频总结' },
  { path: '/zh/answers/', label: '答案中心' },
]

const enFeatureLinks = [
  { path: '/en/features/video-downloader', label: 'Video Downloader' },
  { path: '/en/features/audio-extractor', label: 'Audio Extractor' },
  { path: '/en/features/subtitle-downloader', label: 'Subtitle Downloader' },
  { path: '/en/features/ai-video-summarizer', label: 'AI Video Summarizer' },
  { path: '/en/answers/', label: 'Answers Hub' },
]

const zhPlatformLinks = [
  { path: '/zh/platforms/youtube', label: 'YouTube 下载' },
  { path: '/zh/platforms/bilibili', label: 'Bilibili 下载' },
  { path: '/zh/platforms/tiktok', label: 'TikTok 下载' },
  { path: '/zh/platforms/instagram', label: 'Instagram 下载' },
]

const enPlatformLinks = [
  { path: '/en/platforms/youtube', label: 'YouTube Downloader' },
  { path: '/en/platforms/bilibili', label: 'Bilibili Downloader' },
  { path: '/en/platforms/tiktok', label: 'TikTok Downloader' },
  { path: '/en/platforms/instagram', label: 'Instagram Downloader' },
]

const zhPlatformPages = [
  makePlatformPage('zh-CN', 'youtube', 'YouTube 视频下载器', 'YouTube', zhFeatureLinks),
  makePlatformPage('zh-CN', 'bilibili', 'Bilibili 视频下载器', 'Bilibili', zhFeatureLinks),
  makePlatformPage('zh-CN', 'tiktok', 'TikTok 视频下载器', 'TikTok', zhFeatureLinks),
  makePlatformPage('zh-CN', 'instagram', 'Instagram 视频下载器', 'Instagram', zhFeatureLinks),
]

const enPlatformPages = [
  makePlatformPage('en', 'youtube', 'YouTube Video Downloader', 'YouTube', enFeatureLinks),
  makePlatformPage('en', 'bilibili', 'Bilibili Video Downloader', 'Bilibili', enFeatureLinks),
  makePlatformPage('en', 'tiktok', 'TikTok Video Downloader', 'TikTok', enFeatureLinks),
  makePlatformPage('en', 'instagram', 'Instagram Video Downloader', 'Instagram', enFeatureLinks),
]

const zhFeaturePages = [
  makeFeaturePage('zh-CN', 'video-downloader', '视频下载', '视频下载', zhPlatformLinks),
  makeFeaturePage('zh-CN', 'audio-extractor', '音频提取', '音频提取', zhPlatformLinks),
  makeFeaturePage('zh-CN', 'subtitle-downloader', '字幕下载', '字幕下载', zhPlatformLinks),
  makeFeaturePage('zh-CN', 'ai-video-summarizer', 'AI 视频总结', 'AI 视频总结', zhPlatformLinks),
]

const enFeaturePages = [
  makeFeaturePage('en', 'video-downloader', 'Video Downloader', 'Video Downloader', enPlatformLinks),
  makeFeaturePage('en', 'audio-extractor', 'Audio Extractor', 'Audio Extractor', enPlatformLinks),
  makeFeaturePage('en', 'subtitle-downloader', 'Subtitle Downloader', 'Subtitle Downloader', enPlatformLinks),
  makeFeaturePage('en', 'ai-video-summarizer', 'AI Video Summarizer', 'AI Video Summarizer', enPlatformLinks),
]

const zhFaqPage = makeFaqPage('zh-CN', [...zhPlatformLinks, ...zhFeatureLinks])
const enFaqPage = makeFaqPage('en', [...enPlatformLinks, ...enFeatureLinks])

export const seoContent = {
  zh: {
    hub: {
      slug: 'index',
      path: '/zh/',
      title: '视频下载与 AI 总结工具 - VidGrab | 中文版入口',
      description: 'VidGrab 中文入口聚合了视频下载、字幕导出、AI 总结、平台支持页和常见问题，帮助你更快找到合适的公开视频工作流。',
      keywords: ['视频下载工具', 'AI 视频总结', '字幕下载', '公开视频下载', 'VidGrab'],
      h1: 'VidGrab 中文视频下载与 AI 总结入口',
      intro: '这里汇总了 VidGrab 的中文平台页、功能页与常见问题，帮助你从搜索结果快速进入正确的工具场景。',
      sections: zhHomeSections,
      relatedLinks: [...zhPlatformLinks, ...zhFeatureLinks, { path: '/zh/faq', label: '常见问题' }],
    },
    platforms: zhPlatformPages,
    features: zhFeaturePages,
    faq: zhFaqPage,
  },
  en: {
    hub: {
      slug: 'index',
      path: '/en/',
      title: 'Video Downloader and AI Summarizer - VidGrab | English Hub',
      description: 'Explore VidGrab in English with platform pages, feature pages, FAQ, subtitle export, and AI summary workflows for public videos.',
      keywords: ['video downloader', 'AI video summarizer', 'subtitle downloader', 'public video tools', 'VidGrab'],
      h1: 'VidGrab English hub for video download and AI summary',
      intro: 'This hub connects you to VidGrab platform pages, feature pages, and FAQ content so you can move from search to the right workflow quickly.',
      sections: enHomeSections,
      relatedLinks: [...enPlatformLinks, ...enFeatureLinks, { path: '/en/faq', label: 'FAQ' }],
    },
    platforms: enPlatformPages,
    features: enFeaturePages,
    faq: enFaqPage,
  },
}
