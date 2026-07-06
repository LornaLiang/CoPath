import { useCallback, useEffect, useRef, useState } from 'react'

function useAsyncData(loader, dependencies = []) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const requestId = useRef(0)

  const reload = useCallback(async () => {
    const currentRequestId = ++requestId.current
    setLoading(true)
    setError(null)
    try {
      const result = await loader()
      if (requestId.current === currentRequestId) setData(result)
      return result
    } catch (requestError) {
      if (requestId.current === currentRequestId) setError(requestError)
      throw requestError
    } finally {
      if (requestId.current === currentRequestId) setLoading(false)
    }
  }, dependencies)

  useEffect(() => {
    reload().catch(() => {})
    return () => {
      requestId.current += 1
    }
  }, [reload])

  return { data, loading, error, reload, setData }
}

export default useAsyncData
