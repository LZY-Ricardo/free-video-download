export type DownloadDisplayStatus =
  | 'idle'
  | 'fetching'
  | 'ready'
  | 'downloading'
  | 'completed'
  | 'error'

export function getDisplayProgress(currentStatus: DownloadDisplayStatus, rawProgress: number) {
  if (currentStatus === 'completed') {
    return 100
  }
  return rawProgress
}
