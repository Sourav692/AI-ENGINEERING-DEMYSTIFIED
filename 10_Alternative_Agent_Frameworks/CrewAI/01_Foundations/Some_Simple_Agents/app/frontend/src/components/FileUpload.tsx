import { useRef } from 'react'

interface Props {
  label?: string
  accept?: string
  file: File | null
  onFile: (file: File | null) => void
}

export default function FileUpload({
  label = 'Click or drag a file here',
  accept,
  file,
  onFile,
}: Props) {
  const inputRef = useRef<HTMLInputElement>(null)

  return (
    <div
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault()
        onFile(e.dataTransfer.files[0] ?? null)
      }}
      className="border-2 border-dashed border-gray-600 rounded-lg p-6 text-center cursor-pointer hover:border-indigo-500 transition-colors"
    >
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept={accept}
        onChange={(e) => onFile(e.target.files?.[0] ?? null)}
      />
      {file ? (
        <div className="text-indigo-400 text-sm">
          <span className="font-semibold">{file.name}</span>
          <span className="text-gray-500 ml-2">({(file.size / 1024).toFixed(1)} KB)</span>
        </div>
      ) : (
        <p className="text-gray-500 text-sm">{label}</p>
      )}
    </div>
  )
}
