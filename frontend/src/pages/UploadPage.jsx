import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, ImagePlus, X } from 'lucide-react'
import { api } from '../api/client'

export default function UploadPage() {
  const [files, setFiles] = useState([])
  const [previews, setPreviews] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    return () => {
      previews.forEach((url) => URL.revokeObjectURL(url))
    }
  }, [previews])

  function handleFiles(selected) {
    previews.forEach((url) => URL.revokeObjectURL(url))
    const arr = Array.from(selected).slice(0, 5)
    setFiles(arr)
    setPreviews(arr.map((f) => URL.createObjectURL(f)))
    setError(null)
  }

  function removeFile(idx) {
    URL.revokeObjectURL(previews[idx])
    setFiles(files.filter((_, i) => i !== idx))
    setPreviews(previews.filter((_, i) => i !== idx))
  }

  async function handleParse() {
    setLoading(true)
    setError(null)
    try {
      const draft = await api.parseReceipt(files)
      navigate('/review', { state: { draft } })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="px-4 pt-8 max-w-lg mx-auto">
      <h1 className="text-xl font-bold text-app-green mb-1">Upload Receipt</h1>
      <p className="text-sm text-stone-500 mb-6">Photo or screenshot — up to 5 images</p>

      <label htmlFor="file-input" className="sr-only">Upload receipt images</label>
      <input
        id="file-input"
        data-testid="file-input"
        ref={inputRef}
        type="file"
        accept="image/*"
        multiple
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />

      {previews.length === 0 ? (
        <button
          onClick={() => inputRef.current.click()}
          className="w-full border-2 border-dashed border-stone-200 rounded-xl py-12 flex flex-col items-center gap-2 text-stone-400 hover:border-app-green hover:text-app-green transition-colors"
        >
          <ImagePlus size={36} />
          <span className="text-sm font-medium">Choose images</span>
          <span className="text-xs">JPEG, PNG, HEIC — up to 5 files</span>
        </button>
      ) : (
        <div className="space-y-3 mb-4">
          {previews.map((src, i) => (
            <div key={i} className="relative rounded-xl overflow-hidden shadow-sm">
              <img src={src} alt={`receipt ${i + 1}`} className="w-full object-cover max-h-48" />
              <button
                onClick={() => removeFile(i)}
                aria-label={`Remove image ${i + 1}`}
                className="absolute top-2 right-2 bg-black/50 rounded-full p-1 text-white"
              >
                <X size={14} />
              </button>
            </div>
          ))}
          {files.length < 5 && (
            <button
              onClick={() => inputRef.current.click()}
              className="w-full border border-dashed border-stone-200 rounded-xl py-3 text-sm text-stone-400 flex items-center justify-center gap-2"
            >
              <ImagePlus size={16} /> Add more (max 5)
            </button>
          )}
        </div>
      )}

      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

      <button
        onClick={handleParse}
        disabled={files.length === 0 || loading}
        className="mt-6 w-full bg-app-green text-white rounded-xl py-3 font-medium disabled:opacity-40 flex items-center justify-center gap-2"
      >
        {loading ? (
          <>Parsing with Gemini…</>
        ) : (
          <><Upload size={18} /> Parse receipt{files.length !== 1 ? 's' : ''}</>
        )}
      </button>
    </div>
  )
}
