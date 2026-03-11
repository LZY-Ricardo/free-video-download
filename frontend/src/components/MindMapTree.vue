<script setup lang="ts">
import { computed, ref } from 'vue'

import type { MindMapNode } from '@/types'

interface LayoutNode {
  id: string
  label: string
  lines: string[]
  depth: number
  x: number
  y: number
  width: number
  height: number
  color: string
  children: LayoutNode[]
}

interface Link {
  id: string
  from: LayoutNode
  to: LayoutNode
  color: string
}

const props = defineProps<{
  node: MindMapNode
}>()
const svgRef = ref<SVGSVGElement | null>(null)

const PADDING_X = 40
const PADDING_Y = 48
const H_GAP = 250
const V_GAP = 52

const BRANCH_COLORS = ['#3b82f6', '#f97316', '#22c55e', '#a855f7', '#ef4444', '#06b6d4', '#eab308']

const layoutResult = computed(() => {
  if (!props.node) {
    return {
      nodes: [] as LayoutNode[],
      links: [] as Link[],
      width: 900,
      height: 380,
    }
  }

  let leafCursor = 0
  const nodes: LayoutNode[] = []
  const links: Link[] = []

  const buildLayout = (
    current: MindMapNode,
    depth: number,
    branchColor: string,
    siblingIndex: number,
  ): LayoutNode => {
    const color =
      depth === 0
        ? '#2563eb'
        : depth === 1
          ? (BRANCH_COLORS[siblingIndex % BRANCH_COLORS.length] ?? '#3b82f6')
          : branchColor

    const lines = wrapLabel(current.label, depth >= 3 ? 20 : 16, 2)
    const maxLineWidth = Math.max(...lines.map((line) => estimateTextWidth(line)))
    const width = Math.max(80, Math.min(280, maxLineWidth + 22))
    const height = 14 + lines.length * 16

    const children = (current.children || []).map((child, index) =>
      buildLayout(child, depth + 1, color, index),
    )

    let y = 0
    if (!children.length) {
      y = PADDING_Y + leafCursor * V_GAP
      leafCursor += 1
    } else {
      y = children.reduce((sum, child) => sum + child.y, 0) / children.length
    }

    const x = PADDING_X + depth * H_GAP

    const node: LayoutNode = {
      id: current.id || `${depth}-${siblingIndex}-${Math.random().toString(36).slice(2, 8)}`,
      label: current.label,
      lines,
      depth,
      x,
      y,
      width,
      height,
      color,
      children,
    }
    nodes.push(node)

    for (const child of children) {
      links.push({
        id: `${node.id}->${child.id}`,
        from: node,
        to: child,
        color: child.color,
      })
    }

    return node
  }

  const root = buildLayout(props.node, 0, '#2563eb', 0)
  const maxX = Math.max(...nodes.map((node) => node.x + node.width))
  const maxY = Math.max(...nodes.map((node) => node.y + node.height / 2))
  const minY = Math.min(...nodes.map((node) => node.y - node.height / 2))

  const width = Math.max(980, maxX + 120)
  const height = Math.max(410, maxY - minY + 120)

  // 将整体图形垂直居中
  const centerOffset = (height - (maxY - minY)) / 2 - minY
  for (const node of nodes) {
    node.y += centerOffset
  }

  return {
    nodes,
    links,
    width,
    height,
    root,
  }
})

const svgStyle = computed(() => ({
  width: `${layoutResult.value.width}px`,
  height: `${layoutResult.value.height}px`,
}))

const buildCurvePath = (link: Link): string => {
  const startX = link.from.x + link.from.width
  const startY = link.from.y
  const endX = link.to.x
  const endY = link.to.y

  const distance = endX - startX
  const c1x = startX + distance * 0.35
  const c2x = startX + distance * 0.75

  return `M ${startX} ${startY} C ${c1x} ${startY}, ${c2x} ${endY}, ${endX} ${endY}`
}

function wrapLabel(label: string, maxCharsPerLine: number, maxLines: number): string[] {
  const text = (label || '').trim()
  if (!text) {
    return ['']
  }

  const lines: string[] = []
  let currentLine = ''
  let currentUnits = 0

  for (const char of text) {
    const units = char.charCodeAt(0) > 255 ? 1 : 0.55
    if (currentUnits + units > maxCharsPerLine && currentLine) {
      lines.push(currentLine)
      currentLine = char
      currentUnits = units
      if (lines.length >= maxLines) {
        break
      }
    } else {
      currentLine += char
      currentUnits += units
    }
  }

  if (lines.length < maxLines && currentLine) {
    lines.push(currentLine)
  }

  if (lines.length > maxLines) {
    lines.length = maxLines
  }

  const consumedLength = lines.join('').length
  if (consumedLength < text.length && lines.length) {
    const lastIndex = lines.length - 1
    const lastLine = lines[lastIndex]
    if (lastLine !== undefined) {
      lines[lastIndex] = `${lastLine.slice(0, Math.max(1, lastLine.length - 1))}…`
    }
  }
  return lines
}

function estimateTextWidth(text: string): number {
  let width = 0
  for (const char of text) {
    width += char.charCodeAt(0) > 255 ? 13 : 7
  }
  return width
}

const buildSvgMarkup = (): string => {
  const svgEl = svgRef.value
  if (!svgEl) {
    throw new Error('思维导图尚未渲染完成')
  }
  const clone = svgEl.cloneNode(true) as SVGSVGElement
  clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
  clone.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink')
  return new XMLSerializer().serializeToString(clone)
}

const triggerDownload = (blob: Blob, filename: string) => {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

const downloadSvg = (filenameBase = 'mind-map') => {
  const svgMarkup = buildSvgMarkup()
  const blob = new Blob([svgMarkup], { type: 'image/svg+xml;charset=utf-8' })
  triggerDownload(blob, `${filenameBase}.svg`)
}

const downloadPng = async (filenameBase = 'mind-map', scale = 3): Promise<void> => {
  const svgMarkup = buildSvgMarkup()
  const width = layoutResult.value.width
  const height = layoutResult.value.height
  const svgBlob = new Blob([svgMarkup], { type: 'image/svg+xml;charset=utf-8' })
  const svgUrl = URL.createObjectURL(svgBlob)

  try {
    const image = await new Promise<HTMLImageElement>((resolve, reject) => {
      const img = new Image()
      img.onload = () => resolve(img)
      img.onerror = () => reject(new Error('导图渲染失败，无法导出 PNG'))
      img.src = svgUrl
    })

    const safeScale = Math.max(1, Number.isFinite(scale) ? scale : 1)
    const canvas = document.createElement('canvas')
    canvas.width = Math.round(width * safeScale)
    canvas.height = Math.round(height * safeScale)

    const context = canvas.getContext('2d')
    if (!context) {
      throw new Error('当前浏览器不支持 Canvas 导出')
    }

    context.setTransform(safeScale, 0, 0, safeScale, 0, 0)
    context.fillStyle = '#ffffff'
    context.fillRect(0, 0, width, height)
    context.drawImage(image, 0, 0, width, height)

    const pngBlob = await new Promise<Blob>((resolve, reject) => {
      canvas.toBlob((blob) => {
        if (blob) {
          resolve(blob)
          return
        }
        reject(new Error('PNG 生成失败'))
      }, 'image/png')
    })
    triggerDownload(pngBlob, `${filenameBase}.png`)
  } finally {
    URL.revokeObjectURL(svgUrl)
  }
}

defineExpose({
  downloadSvg,
  downloadPng,
})
</script>

<template>
  <div class="mindmap-canvas rounded-lg bg-slate-50 border border-slate-200 overflow-auto w-full h-full">
    <svg
      ref="svgRef"
      :viewBox="`0 0 ${layoutResult.width} ${layoutResult.height}`"
      :style="svgStyle"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g>
        <path
          v-for="link in layoutResult.links"
          :key="link.id"
          :d="buildCurvePath(link)"
          fill="none"
          :stroke="link.color"
          stroke-width="2.2"
          stroke-linecap="round"
          opacity="0.92"
        />

        <circle
          v-for="link in layoutResult.links"
          :key="`${link.id}-dot`"
          :cx="link.to.x"
          :cy="link.to.y"
          r="4.3"
          fill="#ffffff"
          :stroke="link.color"
          stroke-width="1.8"
        />

        <g
          v-for="node in layoutResult.nodes"
          :key="node.id"
          :transform="`translate(${node.x}, ${node.y - node.height / 2})`"
          class="cursor-default"
        >
          <rect
            :width="node.width"
            :height="node.height"
            rx="9"
            ry="9"
            fill="#ffffff"
            :stroke="node.depth === 0 ? '#2563eb' : '#cbd5e1'"
            :stroke-width="node.depth === 0 ? 1.8 : 1.2"
          />

          <title>{{ node.label }}</title>

          <text
            v-for="(line, lineIndex) in node.lines"
            :key="`${node.id}-line-${lineIndex}`"
            :x="11"
            :y="16 + lineIndex * 16"
            :fill="node.depth === 0 ? '#1d4ed8' : '#334155'"
            :font-size="node.depth === 0 ? 14 : 12.5"
            :font-weight="node.depth === 0 ? 600 : 500"
            font-family="Outfit, sans-serif"
          >
            {{ line }}
          </text>
        </g>
      </g>
    </svg>
  </div>
</template>

<style scoped>
.mindmap-canvas {
  min-height: 320px;
}
</style>
