export function shouldPreferLocalResolver(_input: string) {
  return true
}

export function shouldTryLocalResolverFallback(
  _input: string,
  detail: string,
  statusCode?: number,
) {
  const errorText = (detail || '').toLowerCase()
  const isRiskControlError =
    errorText.includes('412') || errorText.includes('precondition failed') || errorText.includes('风控')

  return isRiskControlError || !statusCode || statusCode >= 500
}

export function resolveInfoFallbackErrorMessage(localError: any, fallbackMessage: string) {
  return localError?.response?.data?.detail || fallbackMessage || '获取视频信息失败'
}

export function resolveInfoPrimaryErrorMessage(primaryError: any, fallbackMessage: string) {
  return primaryError?.response?.data?.detail || fallbackMessage || '获取视频信息失败'
}
