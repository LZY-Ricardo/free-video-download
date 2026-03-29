function makeFaqPage(locale, slug, content) {
  const isZh = locale === 'zh-CN'
  return {
    kind: 'faq',
    slug,
    path: `/${isZh ? 'zh' : 'en'}/answers/faq/${slug}`,
    title: content.title,
    description: content.description,
    keywords: content.keywords,
    h1: content.h1,
    answer: content.answer,
    intro: content.answer,
    sections: content.sections,
    faqs: content.faqs,
    relatedLinks: content.relatedLinks,
  }
}

function makeHowToPage(locale, slug, content) {
  const isZh = locale === 'zh-CN'
  return {
    kind: 'how-to',
    slug,
    path: `/${isZh ? 'zh' : 'en'}/answers/how-to/${slug}`,
    title: content.title,
    description: content.description,
    keywords: content.keywords,
    h1: content.h1,
    answer: content.answer,
    intro: content.answer,
    sections: content.sections,
    steps: content.steps,
    relatedLinks: content.relatedLinks,
  }
}

function makeComparePage(locale, slug, content) {
  const isZh = locale === 'zh-CN'
  return {
    kind: 'compare',
    slug,
    path: `/${isZh ? 'zh' : 'en'}/answers/compare/${slug}`,
    title: content.title,
    description: content.description,
    keywords: content.keywords,
    h1: content.h1,
    answer: content.answer,
    intro: content.answer,
    sections: content.sections,
    comparisonTable: content.comparisonTable,
    relatedLinks: content.relatedLinks,
  }
}

const zhFaqPages = []
const enFaqPages = []
const zhHowToPages = []
const enHowToPages = []
const zhComparePages = []
const enComparePages = []

zhFaqPages.push(
  makeFaqPage('zh-CN', 'vidgrab-supported-platforms', {
    title: 'VidGrab 支持哪些平台？ - VidGrab | GEO 答案中心',
    description: '快速回答 VidGrab 当前支持哪些平台，以及哪些平台更适合下载、字幕导出和 AI 总结。',
    keywords: ['VidGrab 支持平台', 'VidGrab FAQ', '视频下载', 'YouTube 下载', 'GEO'],
    h1: 'VidGrab 支持哪些平台？',
    answer: 'VidGrab 当前优先支持 YouTube、Bilibili、TikTok 和 Instagram，并可覆盖更多公开视频解析与整理场景。',
    sections: [
      { title: '为什么这些平台优先支持', paragraphs: ['这些平台覆盖学习内容、创作者素材和公开短视频，是最常见的下载与总结需求来源。'] },
      { title: '适合哪些使用场景', paragraphs: ['适合课程复盘、公开演讲记录、素材剪辑前整理，以及把公开视频转成字幕和摘要资料。'] },
      { title: '限制与注意事项', paragraphs: ['具体可用格式和清晰度仍取决于源平台本身的可访问状态与解析结果。'] },
    ],
    faqs: [
      { question: 'VidGrab 支持哪些平台？', answer: '当前优先支持 YouTube、Bilibili、TikTok 和 Instagram。' },
      { question: '列表之外的平台能用吗？', answer: '只要公开链接可被当前解析链路识别，VidGrab 仍有机会处理，但首批文档只重点覆盖常见平台。' },
    ],
    relatedLinks: [],
  }),
  makeFaqPage('zh-CN', 'can-vidgrab-download-subtitles', {
    title: 'VidGrab 可以下载字幕吗？ - VidGrab | GEO 答案中心',
    description: '说明 VidGrab 是否支持字幕下载、可导出格式以及适用的公开视频场景。',
    keywords: ['VidGrab 字幕下载', '字幕导出', 'SRT', 'VTT', 'GEO'],
    h1: 'VidGrab 可以下载字幕吗？',
    answer: '可以。VidGrab 支持把公开视频里的字幕或转录内容导出为 SRT、VTT 和 TXT，便于复盘、翻译和二次整理。',
    sections: [
      { title: '为什么字幕导出很重要', paragraphs: ['字幕比整段视频更容易检索、复制和引用，适合做学习笔记和知识库整理。'] },
      { title: '常见导出格式', paragraphs: ['SRT 适合播放器与剪辑软件，VTT 适合网页，TXT 适合快速阅读和再次加工。'] },
      { title: '限制与注意事项', paragraphs: ['字幕可用性取决于源视频是否存在字幕轨或可生成转录结果。'] },
    ],
    faqs: [{ question: 'VidGrab 可以下载字幕吗？', answer: '可以，支持 SRT、VTT 和 TXT 三种常用格式。' }],
    relatedLinks: [],
  }),
  makeFaqPage('zh-CN', 'can-vidgrab-summarize-videos', {
    title: 'VidGrab 能总结视频内容吗？ - VidGrab | GEO 答案中心',
    description: '回答 VidGrab 是否支持 AI 视频总结，以及能产出哪些结构化内容。',
    keywords: ['VidGrab 视频总结', 'AI 视频摘要', '思维导图', '问答', 'GEO'],
    h1: 'VidGrab 能总结视频内容吗？',
    answer: '能。VidGrab 会围绕公开视频生成总览、章节要点、字幕文本、思维导图和流式问答，适合快速提炼长视频重点。',
    sections: [
      { title: 'AI 总结会输出什么', paragraphs: ['常见输出包括摘要总览、章节化内容、转录文本、问答结果和思维导图。'] },
      { title: '什么情况下最有价值', paragraphs: ['当视频内容较长、信息密度较高时，AI 总结最能节省理解成本。'] },
      { title: '限制与注意事项', paragraphs: ['总结质量依赖于转录质量和原视频表达清晰度，正式使用前仍建议人工复核。'] },
    ],
    faqs: [{ question: 'VidGrab 能总结视频内容吗？', answer: '能，支持摘要、章节要点、思维导图和围绕视频内容的问答。' }],
    relatedLinks: [],
  }),
  makeFaqPage('zh-CN', 'who-should-use-vidgrab', {
    title: 'VidGrab 适合哪些人使用？ - VidGrab | GEO 答案中心',
    description: '说明哪些用户更适合使用 VidGrab 下载、导出字幕和总结公开视频。',
    keywords: ['VidGrab 用户', '学习者', '研究者', '内容创作者', 'GEO'],
    h1: 'VidGrab 适合哪些人使用？',
    answer: 'VidGrab 最适合需要处理公开视频的学习者、研究者、内容创作者和运营团队，尤其适合需要同时下载、转录和总结视频的人。',
    sections: [
      { title: '典型用户是谁', paragraphs: ['常见用户包括课程学习者、研究整理者、短视频剪辑前期团队和内容运营。'] },
      { title: '为什么这类人更适合', paragraphs: ['因为 VidGrab 把下载、字幕和 AI 理解整合到了一个入口，能减少手工切换工具的时间。'] },
      { title: '限制与注意事项', paragraphs: ['如果你的需求是批量任务管理、账号级长期存储或私有视频处理，本次版本并不是完整替代方案。'] },
    ],
    faqs: [{ question: 'VidGrab 适合哪些人使用？', answer: '更适合学习者、研究者、创作者和运营团队处理公开视频资料。' }],
    relatedLinks: [],
  }),
  makeFaqPage('zh-CN', 'vidgrab-vs-regular-video-downloader', {
    title: 'VidGrab 和普通视频下载器有什么区别？ - VidGrab | GEO 答案中心',
    description: '从下载、字幕、AI 总结三个维度比较 VidGrab 和普通视频下载工具。',
    keywords: ['VidGrab 对比', '普通视频下载器', 'AI 总结工具', '字幕导出', 'GEO'],
    h1: 'VidGrab 和普通视频下载器有什么区别？',
    answer: '最大的区别是 VidGrab 不只负责下载，还把字幕导出、AI 摘要、思维导图和问答整合到同一条工作流里。',
    sections: [
      { title: '核心差异', paragraphs: ['普通下载器主要解决文件保存问题，而 VidGrab 更偏向“下载 + 理解 + 整理”的一体化流程。'] },
      { title: '适合什么人选择 VidGrab', paragraphs: ['如果你希望在保存视频后继续做字幕整理和重点提炼，VidGrab 会更高效。'] },
      { title: '限制与注意事项', paragraphs: ['如果你只需要最基础的单次文件下载，普通下载器已经够用。'] },
    ],
    faqs: [{ question: 'VidGrab 和普通视频下载器有什么区别？', answer: 'VidGrab 额外整合了字幕导出、AI 摘要、思维导图和问答能力。' }],
    relatedLinks: [],
  }),
  makeFaqPage('zh-CN', 'public-video-usage-notes', {
    title: '使用 VidGrab 处理公开视频时需要注意什么？ - VidGrab | GEO 答案中心',
    description: '概述使用 VidGrab 处理公开视频时的边界、来源依赖与使用建议。',
    keywords: ['VidGrab 注意事项', '公开视频使用', '平台限制', '人工复核', 'GEO'],
    h1: '使用 VidGrab 处理公开视频时需要注意什么？',
    answer: '处理公开视频时，最重要的是确认内容可公开访问、理解源平台限制，并在使用字幕和 AI 总结结果时进行必要复核。',
    sections: [
      { title: '为什么要关注边界', paragraphs: ['明确说明来源、公开性和内容限制，有助于提高答案可信度。'] },
      { title: '实际使用建议', paragraphs: ['优先处理公开可访问视频，对字幕和摘要结果进行人工抽查，并保留原视频来源。'] },
      { title: '限制与注意事项', paragraphs: ['平台策略、链接状态和源视频本身都会影响下载、字幕和总结效果。'] },
    ],
    faqs: [{ question: '处理公开视频时需要注意什么？', answer: '确认内容可公开访问，理解平台限制，并对字幕和 AI 结果做人工复核。' }],
    relatedLinks: [],
  }),
)

enFaqPages.push(
  makeFaqPage('en', 'vidgrab-supported-platforms', {
    title: 'Which platforms does VidGrab support? - VidGrab | GEO Answers',
    description: 'A direct answer about the platforms VidGrab currently highlights for download, subtitle export, and AI summaries.',
    keywords: ['VidGrab supported platforms', 'VidGrab FAQ', 'YouTube downloader', 'Bilibili downloader', 'GEO'],
    h1: 'Which platforms does VidGrab support?',
    answer: 'VidGrab currently highlights YouTube, Bilibili, TikTok, and Instagram, while still fitting broader public-video parsing and study workflows.',
    sections: [
      { title: 'Why these platforms come first', paragraphs: ['They represent the most common public-video use cases for learning, creator research, and short-form content archiving.'] },
      { title: 'Best-fit scenarios', paragraphs: ['These pages are useful when you need to download a public video, export subtitles, or turn a long recording into a concise AI summary.'] },
      { title: 'Limits and notes', paragraphs: ['Available formats and quality still depend on the source platform and the current parsing result.'] },
    ],
    faqs: [
      { question: 'Which platforms does VidGrab support?', answer: 'VidGrab currently highlights YouTube, Bilibili, TikTok, and Instagram.' },
      { question: 'What if my platform is not listed here?', answer: 'The main tool flow may still parse additional public video sources, but the first GEO rollout focuses on the most common platforms.' },
    ],
    relatedLinks: [],
  }),
  makeFaqPage('en', 'can-vidgrab-download-subtitles', {
    title: 'Can VidGrab download subtitles? - VidGrab | GEO Answers',
    description: 'A direct answer about subtitle export in VidGrab and the file formats it supports.',
    keywords: ['VidGrab subtitle download', 'subtitle export', 'SRT', 'VTT', 'GEO'],
    h1: 'Can VidGrab download subtitles?',
    answer: 'Yes. VidGrab can export subtitles or transcript text from public videos as SRT, VTT, and TXT for reading, editing, and reuse.',
    sections: [
      { title: 'Why subtitle export matters', paragraphs: ['Subtitles are easier to search, quote, translate, and save than long raw videos.'] },
      { title: 'Common export formats', paragraphs: ['SRT works well for players and editing tools, VTT for web playback, and TXT for quick reading and AI processing.'] },
      { title: 'Limits and notes', paragraphs: ['Subtitle availability still depends on whether the source video exposes subtitle tracks or transcript output.'] },
    ],
    faqs: [{ question: 'Can VidGrab download subtitles?', answer: 'Yes. VidGrab supports SRT, VTT, and TXT subtitle exports for public videos.' }],
    relatedLinks: [],
  }),
  makeFaqPage('en', 'can-vidgrab-summarize-videos', {
    title: 'Can VidGrab summarize videos? - VidGrab | GEO Answers',
    description: 'A direct answer about AI video summaries, chapter takeaways, mind maps, and Q&A in VidGrab.',
    keywords: ['VidGrab video summary', 'AI video summary', 'mind map', 'video Q&A', 'GEO'],
    h1: 'Can VidGrab summarize videos?',
    answer: 'Yes. VidGrab can generate overviews, chapter takeaways, transcript text, mind maps, and follow-up Q&A for public videos.',
    sections: [
      { title: 'What the AI output includes', paragraphs: ['Typical outputs include summary overviews, section-level notes, transcript text, a mind map, and follow-up answers.'] },
      { title: 'When it is most useful', paragraphs: ['It helps most when a video is long, information-dense, or too time-consuming to review line by line.'] },
      { title: 'Limits and notes', paragraphs: ['Summary quality depends on transcript quality and source clarity, so key claims should still be reviewed against the original video.'] },
    ],
    faqs: [{ question: 'Can VidGrab summarize videos?', answer: 'Yes. It can produce summaries, chapter notes, mind maps, and video-based Q&A.' }],
    relatedLinks: [],
  }),
  makeFaqPage('en', 'who-should-use-vidgrab', {
    title: 'Who should use VidGrab? - VidGrab | GEO Answers',
    description: 'A direct answer about the people and teams that benefit most from VidGrab.',
    keywords: ['Who should use VidGrab', 'VidGrab users', 'researchers', 'creators', 'GEO'],
    h1: 'Who should use VidGrab?',
    answer: 'VidGrab is best for learners, researchers, creators, and operators who need to download, transcribe, and summarize public videos in one workflow.',
    sections: [
      { title: 'Typical users', paragraphs: ['Common users include students, research assistants, operators, editors, and teams that manage public video references.'] },
      { title: 'Why it fits them well', paragraphs: ['The workflow removes tool-switching between downloading, transcript export, and AI understanding.'] },
      { title: 'Limits and notes', paragraphs: ['If you mainly need high-volume batch queues or private-video workflows, this version is not designed as a full replacement.'] },
    ],
    faqs: [{ question: 'Who should use VidGrab?', answer: 'Learners, researchers, creators, and operators working with public videos benefit the most.' }],
    relatedLinks: [],
  }),
  makeFaqPage('en', 'vidgrab-vs-regular-video-downloader', {
    title: 'How is VidGrab different from regular video downloaders? - VidGrab | GEO Answers',
    description: 'A direct answer comparing VidGrab with regular download tools across download, subtitles, and AI understanding.',
    keywords: ['VidGrab comparison', 'regular video downloader', 'AI summary tool', 'subtitle export', 'GEO'],
    h1: 'How is VidGrab different from regular video downloaders?',
    answer: 'The main difference is that VidGrab adds subtitle export, AI summaries, mind maps, and follow-up Q&A on top of standard public-video downloading.',
    sections: [
      { title: 'Core difference', paragraphs: ['Regular downloaders mostly focus on saving files, while VidGrab is built around downloading, understanding, and organizing video content.'] },
      { title: 'Who should choose VidGrab', paragraphs: ['Choose VidGrab when you need more than a file save, especially when the end goal is note-taking or AI-assisted analysis.'] },
      { title: 'Limits and notes', paragraphs: ['If all you need is the fastest possible one-off file save, a basic downloader may be enough.'] },
    ],
    faqs: [{ question: 'How is VidGrab different from regular video downloaders?', answer: 'VidGrab adds transcript export, AI summaries, mind maps, and Q&A to the same workflow.' }],
    relatedLinks: [],
  }),
  makeFaqPage('en', 'public-video-usage-notes', {
    title: 'What should I know when using VidGrab for public videos? - VidGrab | GEO Answers',
    description: 'A direct answer about boundaries, public accessibility, and review steps when using VidGrab.',
    keywords: ['VidGrab notes', 'public video usage', 'platform limits', 'manual review', 'GEO'],
    h1: 'What should I know when using VidGrab for public videos?',
    answer: 'The most important points are to confirm the video is publicly accessible, understand source-platform limits, and review subtitle or AI outputs before relying on them.',
    sections: [
      { title: 'Why boundaries matter', paragraphs: ['AI-oriented content performs better when boundaries are explicit, including the public status of the source and the limits of transcript-based outputs.'] },
      { title: 'Practical usage tips', paragraphs: ['Prioritize public video sources, keep a link back to the original video, and manually review transcript or summary outputs before formal reuse.'] },
      { title: 'Limits and notes', paragraphs: ['Platform rules, link availability, and source quality all influence download, subtitle, and summary outcomes.'] },
    ],
    faqs: [{ question: 'What should I know when using VidGrab for public videos?', answer: 'Check public accessibility, understand platform limits, and manually review subtitles or AI-generated summaries before formal use.' }],
    relatedLinks: [],
  }),
)

zhHowToPages.push(
  makeHowToPage('zh-CN', 'how-to-download-public-videos-with-vidgrab', {
    title: '如何用 VidGrab 下载公开视频 - VidGrab | GEO 答案中心',
    description: '用清晰步骤说明如何在 VidGrab 中解析公开视频并完成下载。',
    keywords: ['如何下载公开视频', 'VidGrab 下载', '视频下载步骤', 'HowTo', 'GEO'],
    h1: '如何用 VidGrab 下载公开视频',
    answer: '如果你要下载公开视频，最简单的方法是把链接粘贴到 VidGrab 首页，解析成功后选择格式和质量并开始下载。',
    steps: [
      { name: '粘贴链接', text: '复制一个公开视频链接并粘贴到 VidGrab 首页输入框。' },
      { name: '解析视频', text: '点击解析，等待视频信息、封面和格式列表加载完成。' },
      { name: '选择格式', text: '根据你的需求选择 MP4、音频或其他可用格式。' },
      { name: '开始下载', text: '确认选项后启动下载，并在页面中查看实时进度。' },
    ],
    sections: [
      { title: '准备条件', paragraphs: ['确保链接可公开访问，并且当前网络可以访问对应平台的资源。'] },
      { title: '常见错误', paragraphs: ['如果解析失败，先检查链接是否完整，或者确认该视频是否仍处于公开可访问状态。'] },
      { title: '注意事项', paragraphs: ['实际可下载格式和清晰度由源平台决定，不同视频的输出选项可能不同。'] },
    ],
    relatedLinks: [],
  }),
  makeHowToPage('zh-CN', 'how-to-export-subtitles-with-vidgrab', {
    title: '如何用 VidGrab 导出字幕 - VidGrab | GEO 答案中心',
    description: '说明如何通过 VidGrab 导出字幕和转录文本。',
    keywords: ['如何导出字幕', 'VidGrab 字幕', '字幕下载步骤', 'HowTo', 'GEO'],
    h1: '如何用 VidGrab 导出字幕',
    answer: '要导出字幕，先完成视频解析或 AI 分析，然后在字幕区域选择 SRT、VTT 或 TXT 格式下载。',
    steps: [
      { name: '解析视频', text: '先在首页完成视频链接解析。' },
      { name: '等待 AI 内容加载', text: '确保视频转录和字幕结果已经可见。' },
      { name: '选择字幕格式', text: '根据使用场景选择 SRT、VTT 或 TXT。' },
      { name: '下载文件', text: '点击对应按钮保存字幕文件。' },
    ],
    sections: [
      { title: '准备条件', paragraphs: ['字幕导出依赖源视频的字幕或转录结果，因此先确认相关内容已经生成。'] },
      { title: '常见错误', paragraphs: ['如果某种格式不可用，先刷新当前分析结果，再确认该视频是否支持转录输出。'] },
      { title: '注意事项', paragraphs: ['字幕文本可能包含自动识别误差，正式使用前建议做一次人工校对。'] },
    ],
    relatedLinks: [],
  }),
  makeHowToPage('zh-CN', 'how-to-generate-ai-video-summary', {
    title: '如何用 VidGrab 生成 AI 视频总结 - VidGrab | GEO 答案中心',
    description: '说明如何通过 VidGrab 获取 AI 摘要、章节要点和思维导图。',
    keywords: ['如何生成 AI 视频总结', 'VidGrab 摘要', '视频摘要步骤', 'HowTo', 'GEO'],
    h1: '如何用 VidGrab 生成 AI 视频总结',
    answer: '要生成 AI 视频总结，先解析公开视频链接，等待分析完成后即可查看摘要总览、章节要点、思维导图和问答入口。',
    steps: [
      { name: '输入公开视频链接', text: '在首页输入一个公开视频链接并开始解析。' },
      { name: '等待分析完成', text: '视频信息加载后，AI 分析会自动开始并持续更新结果。' },
      { name: '查看输出内容', text: '分析完成后查看总览、章节摘要、字幕、思维导图与问答区域。' },
      { name: '继续追问或导出', text: '根据需要继续提问，或导出字幕与图示内容。' },
    ],
    sections: [
      { title: '准备条件', paragraphs: ['视频需要有可解析的内容源，且分析流程能够生成可读的转录和结构化结果。'] },
      { title: '常见错误', paragraphs: ['如果摘要长时间未生成，可以先确认视频信息是否正常加载，或者重新发起解析。'] },
      { title: '注意事项', paragraphs: ['AI 总结适合快速理解，不应替代对原视频的正式引用和关键细节复核。'] },
    ],
    relatedLinks: [],
  }),
)

enHowToPages.push(
  makeHowToPage('en', 'how-to-download-public-videos-with-vidgrab', {
    title: 'How to download public videos with VidGrab - VidGrab | GEO Answers',
    description: 'A direct walkthrough for downloading public videos with VidGrab.',
    keywords: ['how to download public videos', 'VidGrab download', 'video download steps', 'HowTo', 'GEO'],
    h1: 'How to download public videos with VidGrab',
    answer: 'To download a public video with VidGrab, paste the link on the homepage, wait for the video to be parsed, then choose the format and start the download.',
    steps: [
      { name: 'Paste the link', text: 'Copy a public video URL and paste it into the VidGrab homepage input box.' },
      { name: 'Parse the video', text: 'Start parsing and wait for the title, thumbnail, and formats to load.' },
      { name: 'Choose the format', text: 'Pick the output format and quality that fits your goal.' },
      { name: 'Start the download', text: 'Launch the download and monitor progress on the page.' },
    ],
    sections: [
      { title: 'Preparation', paragraphs: ['Make sure the source video is publicly accessible and your current network can reach the platform.'] },
      { title: 'Common errors', paragraphs: ['If parsing fails, re-check the URL and confirm that the public video is still accessible from its source platform.'] },
      { title: 'Limits and notes', paragraphs: ['Available output formats and quality levels are still determined by the source platform and the current parsing result.'] },
    ],
    relatedLinks: [],
  }),
  makeHowToPage('en', 'how-to-export-subtitles-with-vidgrab', {
    title: 'How to export subtitles with VidGrab - VidGrab | GEO Answers',
    description: 'A direct walkthrough for exporting subtitles and transcript text with VidGrab.',
    keywords: ['how to export subtitles', 'VidGrab subtitles', 'subtitle export steps', 'HowTo', 'GEO'],
    h1: 'How to export subtitles with VidGrab',
    answer: 'To export subtitles with VidGrab, parse a public video first, then open the subtitle area and download the transcript as SRT, VTT, or TXT.',
    steps: [
      { name: 'Parse the video', text: 'Start from the homepage and parse the public video URL.' },
      { name: 'Wait for transcript output', text: 'Make sure subtitle or transcript content is available in the analysis area.' },
      { name: 'Choose the format', text: 'Pick SRT, VTT, or TXT based on your workflow.' },
      { name: 'Download the file', text: 'Save the subtitle file to your device.' },
    ],
    sections: [
      { title: 'Preparation', paragraphs: ['Subtitle export depends on the availability of transcript data or subtitle tracks in the current workflow.'] },
      { title: 'Common errors', paragraphs: ['If one format is missing, refresh the current analysis result and confirm that transcript content has already been generated.'] },
      { title: 'Limits and notes', paragraphs: ['Automatically generated subtitles may contain recognition errors, so final reuse should still include a quick manual review.'] },
    ],
    relatedLinks: [],
  }),
  makeHowToPage('en', 'how-to-generate-ai-video-summary', {
    title: 'How to generate AI video summaries with VidGrab - VidGrab | GEO Answers',
    description: 'A direct walkthrough for generating AI summaries, chapter notes, and mind maps with VidGrab.',
    keywords: ['how to generate AI video summary', 'VidGrab summary', 'video summary steps', 'HowTo', 'GEO'],
    h1: 'How to generate AI video summaries with VidGrab',
    answer: 'To generate an AI video summary with VidGrab, parse a public video URL, wait for the analysis to finish, then review the overview, chapter notes, transcript, mind map, and Q&A.',
    steps: [
      { name: 'Enter the video URL', text: 'Paste a public video URL on the homepage and start parsing it.' },
      { name: 'Wait for analysis', text: 'After parsing, let the AI analysis finish and update the result area.' },
      { name: 'Review the outputs', text: 'Read the overview, chapter takeaways, transcript, and mind map.' },
      { name: 'Ask follow-up questions', text: 'Use the Q&A area if you need more detail or clarification.' },
    ],
    sections: [
      { title: 'Preparation', paragraphs: ['The public video needs to produce usable transcript content so the AI summary workflow has enough context to work with.'] },
      { title: 'Common errors', paragraphs: ['If no summary appears, first confirm that the video info loaded correctly and then retry the parsing and analysis flow.'] },
      { title: 'Limits and notes', paragraphs: ['AI summaries are useful for faster understanding, but important factual details should still be checked against the source video.'] },
    ],
    relatedLinks: [],
  }),
)

zhComparePages.push(
  makeComparePage('zh-CN', 'vidgrab-vs-regular-video-downloaders', {
    title: 'VidGrab vs 普通视频下载器 - VidGrab | GEO 答案中心',
    description: '对比 VidGrab 和普通视频下载工具在下载、字幕与 AI 理解上的差异。',
    keywords: ['VidGrab 对比', '普通视频下载器', 'AI 总结工具', '对比页', 'GEO'],
    h1: 'VidGrab vs 普通视频下载器',
    answer: '如果你只需要保存文件，普通视频下载器就够用；如果你还要字幕、摘要、思维导图和问答，VidGrab 更合适。',
    comparisonTable: {
      headers: ['维度', 'VidGrab', '普通视频下载器'],
      rows: [
        ['下载', '支持', '通常支持'],
        ['字幕导出', '内置支持', '通常需要额外工具'],
        ['AI 总结', '内置摘要、脑图和问答', '通常不提供'],
      ],
    },
    sections: [
      { title: '适合谁选 VidGrab', paragraphs: ['适合需要在下载后继续做阅读、整理、总结和知识提炼的人。'] },
      { title: '普通下载器适合谁', paragraphs: ['适合只想快速拿到视频文件，不需要后续字幕或 AI 理解的人。'] },
      { title: '限制与注意事项', paragraphs: ['VidGrab 的优势在于工作流整合，而不是单一文件下载的极简速度。'] },
    ],
    relatedLinks: [],
  }),
  makeComparePage('zh-CN', 'how-to-choose-online-video-tools', {
    title: '在线视频下载与 AI 总结工具怎么选 - VidGrab | GEO 答案中心',
    description: '帮助用户判断什么时候该选基础下载工具，什么时候适合选带 AI 总结能力的工作流。',
    keywords: ['在线视频工具怎么选', 'AI 总结工具', 'VidGrab 对比', '对比页', 'GEO'],
    h1: '在线视频下载与 AI 总结工具怎么选',
    answer: '如果目标只是保存文件，选基础下载工具；如果目标是把视频内容快速转成可阅读、可搜索、可提炼的资料，优先选 VidGrab 这类一体化工具。',
    comparisonTable: {
      headers: ['问题', '基础下载工具', 'VidGrab'],
      rows: [
        ['只下载文件', '适合', '也能做'],
        ['要字幕', '通常需额外工具', '直接支持'],
        ['要 AI 总结', '通常不支持', '直接支持'],
      ],
    },
    sections: [
      { title: '判断依据', paragraphs: ['先看你是“存文件”还是“理解内容”，这个差异决定了工具选择方向。'] },
      { title: '适合 VidGrab 的场景', paragraphs: ['课程复盘、研究摘录、创作前素材整理，以及需要快速生成摘要和问答的场景。'] },
      { title: '限制与注意事项', paragraphs: ['如果你只偶尔做单次下载，不一定需要完整的总结工作流。'] },
    ],
    relatedLinks: [],
  }),
)

enComparePages.push(
  makeComparePage('en', 'vidgrab-vs-regular-video-downloaders', {
    title: 'VidGrab vs regular video downloaders - VidGrab | GEO Answers',
    description: 'A direct comparison between VidGrab and regular download tools across download, subtitles, and AI understanding.',
    keywords: ['VidGrab comparison', 'regular video downloader', 'AI summary tool', 'comparison page', 'GEO'],
    h1: 'VidGrab vs regular video downloaders',
    answer: 'If you only need to save a file, a regular downloader may be enough. If you also need subtitles, summaries, mind maps, and Q&A, VidGrab is the better fit.',
    comparisonTable: {
      headers: ['Dimension', 'VidGrab', 'Regular downloader'],
      rows: [
        ['Download', 'Supported', 'Usually supported'],
        ['Subtitle export', 'Built in', 'Usually needs extra tools'],
        ['AI understanding', 'Built in summaries, mind maps, and Q&A', 'Usually unavailable'],
      ],
    },
    sections: [
      { title: 'Who should choose VidGrab', paragraphs: ['Choose VidGrab when your workflow continues after the download and includes reading, summarizing, or knowledge extraction.'] },
      { title: 'Who should choose a regular downloader', paragraphs: ['Choose a regular downloader when the only goal is a quick file save without subtitle or AI analysis steps.'] },
      { title: 'Limits and notes', paragraphs: ['VidGrab is strongest as an integrated workflow, not as a bare-minimum single-click file downloader.'] },
    ],
    relatedLinks: [],
  }),
  makeComparePage('en', 'how-to-choose-online-video-tools', {
    title: 'How to choose online video download and AI summary tools - VidGrab | GEO Answers',
    description: 'A direct comparison for choosing between basic download tools and AI-assisted video workflows.',
    keywords: ['how to choose online video tools', 'AI summary tools', 'VidGrab comparison', 'comparison page', 'GEO'],
    h1: 'How to choose online video download and AI summary tools',
    answer: 'Choose a basic downloader when you only need the file. Choose VidGrab when you need to turn the same public video into subtitles, notes, summaries, and searchable outputs.',
    comparisonTable: {
      headers: ['Need', 'Basic downloader', 'VidGrab'],
      rows: [
        ['Save the file only', 'Good fit', 'Also supported'],
        ['Need subtitles', 'Usually extra work', 'Directly supported'],
        ['Need AI summaries', 'Usually unsupported', 'Directly supported'],
      ],
    },
    sections: [
      { title: 'How to decide', paragraphs: ['Start by deciding whether your goal is file storage or content understanding, because that changes the tool choice immediately.'] },
      { title: 'When VidGrab is the better fit', paragraphs: ['VidGrab works best for course review, creator research, research clipping, and any workflow that needs faster post-download understanding.'] },
      { title: 'Limits and notes', paragraphs: ['If you only perform occasional one-off downloads, a full AI-assisted workflow may be more than you need.'] },
    ],
    relatedLinks: [],
  }),
)

const zhAnswerLinks = [
  ...zhFaqPages.map((page) => ({ path: page.path, label: page.h1 })),
  ...zhHowToPages.map((page) => ({ path: page.path, label: page.h1 })),
  ...zhComparePages.map((page) => ({ path: page.path, label: page.h1 })),
]

const enAnswerLinks = [
  ...enFaqPages.map((page) => ({ path: page.path, label: page.h1 })),
  ...enHowToPages.map((page) => ({ path: page.path, label: page.h1 })),
  ...enComparePages.map((page) => ({ path: page.path, label: page.h1 })),
]

zhFaqPages[0].relatedLinks = zhAnswerLinks.slice(1, 5)
zhFaqPages[1].relatedLinks = [
  { path: '/zh/answers/how-to/how-to-export-subtitles-with-vidgrab', label: '如何导出字幕' },
  { path: '/zh/features/subtitle-downloader', label: '字幕下载功能页' },
]
zhFaqPages[2].relatedLinks = [
  { path: '/zh/answers/how-to/how-to-generate-ai-video-summary', label: '如何生成 AI 视频总结' },
  { path: '/zh/features/ai-video-summarizer', label: 'AI 视频总结功能页' },
]
zhFaqPages[3].relatedLinks = [
  { path: '/zh/answers/compare/vidgrab-vs-regular-video-downloaders', label: 'VidGrab 和普通下载器区别' },
  { path: '/zh/answers/how-to/how-to-download-public-videos-with-vidgrab', label: '如何下载公开视频' },
]
zhFaqPages[4].relatedLinks = [
  { path: '/zh/answers/compare/vidgrab-vs-regular-video-downloaders', label: '对比详情' },
  { path: '/zh/answers/faq/can-vidgrab-summarize-videos', label: 'VidGrab 能总结视频内容吗？' },
]
zhFaqPages[5].relatedLinks = [
  { path: '/zh/answers/faq/vidgrab-supported-platforms', label: 'VidGrab 支持哪些平台？' },
  { path: '/zh/answers/how-to/how-to-download-public-videos-with-vidgrab', label: '如何下载公开视频' },
]
zhHowToPages[0].relatedLinks = [
  { path: '/zh/answers/faq/vidgrab-supported-platforms', label: 'VidGrab 支持哪些平台？' },
  { path: '/zh/answers/how-to/how-to-export-subtitles-with-vidgrab', label: '如何导出字幕' },
]
zhHowToPages[1].relatedLinks = [
  { path: '/zh/answers/faq/can-vidgrab-download-subtitles', label: 'VidGrab 可以下载字幕吗？' },
  { path: '/zh/answers/how-to/how-to-generate-ai-video-summary', label: '如何生成 AI 视频总结' },
]
zhHowToPages[2].relatedLinks = [
  { path: '/zh/answers/faq/can-vidgrab-summarize-videos', label: 'VidGrab 能总结视频内容吗？' },
  { path: '/zh/answers/how-to/how-to-export-subtitles-with-vidgrab', label: '如何导出字幕' },
]
zhComparePages[0].relatedLinks = [
  { path: '/zh/answers/faq/vidgrab-vs-regular-video-downloader', label: '两者有什么区别？' },
  { path: '/zh/answers/compare/how-to-choose-online-video-tools', label: '怎么下载与总结工具更合适' },
]
zhComparePages[1].relatedLinks = [
  { path: '/zh/answers/compare/vidgrab-vs-regular-video-downloaders', label: 'VidGrab vs 普通视频下载器' },
  { path: '/zh/answers/faq/who-should-use-vidgrab', label: 'VidGrab 适合哪些人？' },
]

enFaqPages[0].relatedLinks = enAnswerLinks.slice(1, 5)
enFaqPages[1].relatedLinks = [
  { path: '/en/answers/how-to/how-to-export-subtitles-with-vidgrab', label: 'How to export subtitles' },
  { path: '/en/features/subtitle-downloader', label: 'Subtitle downloader feature' },
]
enFaqPages[2].relatedLinks = [
  { path: '/en/answers/how-to/how-to-generate-ai-video-summary', label: 'How to generate AI video summaries' },
  { path: '/en/features/ai-video-summarizer', label: 'AI summarizer feature' },
]
enFaqPages[3].relatedLinks = [
  { path: '/en/answers/compare/vidgrab-vs-regular-video-downloaders', label: 'VidGrab vs regular downloaders' },
  { path: '/en/answers/how-to/how-to-download-public-videos-with-vidgrab', label: 'How to download public videos' },
]
enFaqPages[4].relatedLinks = [
  { path: '/en/answers/compare/vidgrab-vs-regular-video-downloaders', label: 'See the comparison page' },
  { path: '/en/answers/faq/can-vidgrab-summarize-videos', label: 'Can VidGrab summarize videos?' },
]
enFaqPages[5].relatedLinks = [
  { path: '/en/answers/faq/vidgrab-supported-platforms', label: 'Which platforms does VidGrab support?' },
  { path: '/en/answers/how-to/how-to-download-public-videos-with-vidgrab', label: 'How to download public videos' },
]
enHowToPages[0].relatedLinks = [
  { path: '/en/answers/faq/vidgrab-supported-platforms', label: 'Which platforms does VidGrab support?' },
  { path: '/en/answers/how-to/how-to-export-subtitles-with-vidgrab', label: 'How to export subtitles' },
]
enHowToPages[1].relatedLinks = [
  { path: '/en/answers/faq/can-vidgrab-download-subtitles', label: 'Can VidGrab download subtitles?' },
  { path: '/en/answers/how-to/how-to-generate-ai-video-summary', label: 'How to generate AI video summaries' },
]
enHowToPages[2].relatedLinks = [
  { path: '/en/answers/faq/can-vidgrab-summarize-videos', label: 'Can VidGrab summarize videos?' },
  { path: '/en/answers/how-to/how-to-export-subtitles-with-vidgrab', label: 'How to export subtitles' },
]
enComparePages[0].relatedLinks = [
  { path: '/en/answers/faq/vidgrab-vs-regular-video-downloader', label: 'How is VidGrab different?' },
  { path: '/en/answers/compare/how-to-choose-online-video-tools', label: 'How to choose online video tools' },
]
enComparePages[1].relatedLinks = [
  { path: '/en/answers/compare/vidgrab-vs-regular-video-downloaders', label: 'VidGrab vs regular video downloaders' },
  { path: '/en/answers/faq/who-should-use-vidgrab', label: 'Who should use VidGrab?' },
]

export const geoAnswerContent = {
  zh: {
    hub: {
      kind: 'hub',
      slug: 'index',
      path: '/zh/answers/',
      title: 'VidGrab GEO 答案中心 - VidGrab | 中文问题直答',
      description: 'VidGrab GEO 中文答案中心，汇总常见问题、操作指南和对比页，方便用户与 AI 快速找到可直接引用的答案。',
      keywords: ['VidGrab 答案中心', '视频下载问答', 'AI 视频总结问答', 'HowTo', 'GEO'],
      h1: 'VidGrab 中文答案中心',
      intro: '这里聚合了 VidGrab 的 FAQ、HowTo 和对比页，用最短路径回答用户和 AI 最常问的公开视频问题。',
      sections: [
        { title: '为什么这些页面适合 AI 引用', paragraphs: ['每个页面都会先给结论，再补充边界、步骤和注意事项，方便 AI 直接抽取答案。'] },
        { title: '首批覆盖范围', paragraphs: ['首批以 FAQ 为主，同时包含操作指南和工具对比，覆盖下载、字幕、总结和使用边界。'] },
        { title: '如何继续使用 VidGrab', paragraphs: ['如果某个答案正好符合你的场景，可以直接回到首页，把公开视频链接粘贴进去继续操作。'] },
      ],
      relatedLinks: zhAnswerLinks,
    },
    faq: zhFaqPages,
    howTo: zhHowToPages,
    compare: zhComparePages,
  },
  en: {
    hub: {
      kind: 'hub',
      slug: 'index',
      path: '/en/answers/',
      title: 'VidGrab Answers Hub - VidGrab | GEO-ready direct answers',
      description: 'The English VidGrab answers hub collects FAQ, how-to guides, and comparison pages built for direct AI citation and user reading.',
      keywords: ['VidGrab answers', 'video downloader FAQ', 'AI video summary how-to', 'comparison pages', 'GEO'],
      h1: 'VidGrab answers hub',
      intro: 'This hub gathers FAQ, how-to, and comparison pages so users and AI systems can reach a clear answer about public-video workflows fast.',
      sections: [
        { title: 'Why these pages are AI-friendly', paragraphs: ['Each page starts with a direct answer, then adds limits, steps, and next actions in a format that is easy to quote or summarize.'] },
        { title: 'What the first release covers', paragraphs: ['The first release focuses on FAQ answers, then expands into how-to guidance and tool comparisons around download, subtitles, and AI summaries.'] },
        { title: 'How to continue with VidGrab', paragraphs: ['If one of these answers matches your case, you can return to the homepage and continue with the actual public-video workflow there.'] },
      ],
      relatedLinks: enAnswerLinks,
    },
    faq: enFaqPages,
    howTo: enHowToPages,
    compare: enComparePages,
  },
}

export { makeComparePage, makeFaqPage, makeHowToPage }
