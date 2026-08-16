import { useEffect, useRef, useState } from 'react'

interface Props {
  stream: ReadableStream<Uint8Array> | null
  onFinal?: (text: string) => void
  onImage?: (url: string) => void
  onDownload?: (url: string) => void
  onDone?: () => void
}

export default function StreamOutput({
  stream,
  onFinal,
  onImage,
  onDownload,
  onDone,
}: Props) {
  const [lines, setLines] = useState<string[]>([])
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!stream) return
    setLines([])

    const reader = stream.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    async function pump() {
      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          buffer += decoder.decode(value, { stream: true })

          // SSE events are separated by double newlines
          const parts = buffer.split('\n\n')
          buffer = parts.pop() ?? ''

          for (const part of parts) {
            for (const line of part.split('\n')) {
              if (!line.startsWith('data: ')) continue
              const data = line.slice(6)

              if (data.startsWith('[FINAL] ')) {
                onFinal?.(data.slice(8).replace(/\\n/g, '\n'))
              } else if (data.startsWith('[IMAGE] ')) {
                onImage?.(data.slice(8))
              } else if (data.startsWith('[DOWNLOAD] ')) {
                onDownload?.(data.slice(11))
              } else {
                setLines((prev) => [...prev, data.replace(/\\n/g, '\n')])
              }
            }
          }
        }
      } finally {
        onDone?.()
      }
    }

    pump()
  }, [stream])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [lines])

  if (!stream && lines.length === 0) return null

  return (
    <div className="bg-black rounded-lg border border-gray-700 p-4 h-72 overflow-y-auto font-mono text-sm text-green-400 leading-relaxed">
      {lines.length === 0 && (
        <span className="animate-pulse text-gray-500">Connecting to agent...</span>
      )}
      {lines.map((line, i) => (
        <div key={i} className="whitespace-pre-wrap break-words">
          {line}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
