'use client'
import { useState, useRef, useCallback, useMemo, useEffect } from 'react'
import { toast } from 'sonner'
import { TextArea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { useStore } from '@/store'
import useAIChatStreamHandler from '@/hooks/useAIStreamHandler'
import { useQueryState } from 'nuqs'
import Icon from '@/components/ui/icon'

const MAX_FILES = 5
const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

const ChatInput = () => {
  const { chatInputRef } = useStore()

  const { handleStreamResponse } = useAIChatStreamHandler()
  const [selectedAgent] = useQueryState('agent')
  const [teamId] = useQueryState('team')
  const [inputMessage, setInputMessage] = useState('')
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  const isStreaming = useStore((state) => state.isStreaming)

  // Stable ObjectURL management via useMemo + useEffect cleanup
  const previewUrls = useMemo(
    () => selectedFiles.map((f) => URL.createObjectURL(f)),
    [selectedFiles]
  )

  useEffect(() => {
    return () => {
      previewUrls.forEach((url) => URL.revokeObjectURL(url))
    }
  }, [previewUrls])

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = Array.from(e.target.files || [])
      const validFiles = files.filter((file) => {
        if (!ALLOWED_TYPES.includes(file.type)) {
          toast.error(`Unsupported file type: ${file.name}`)
          return false
        }
        if (file.size > MAX_FILE_SIZE) {
          toast.error(`File too large (max 10MB): ${file.name}`)
          return false
        }
        return true
      })
      if (validFiles.length > 0) {
        setSelectedFiles((prev) => {
          const combined = [...prev, ...validFiles]
          if (combined.length > MAX_FILES) {
            toast.error(`Up to ${MAX_FILES} images allowed`)
            return combined.slice(0, MAX_FILES)
          }
          return combined
        })
      }
      // Reset input so the same file can be selected again
      e.target.value = ''
    },
    []
  )

  const removeFile = useCallback((index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index))
  }, [])

  const handleSubmit = async () => {
    if (!inputMessage.trim() && selectedFiles.length === 0) return

    const currentMessage = inputMessage
    const currentFiles = [...selectedFiles]
    setInputMessage('')
    setSelectedFiles([])

    try {
      const formData = new FormData()
      formData.append('message', currentMessage)
      currentFiles.forEach((file) => {
        formData.append('files', file)
      })
      await handleStreamResponse(formData)
    } catch (error) {
      toast.error(
        `Error in handleSubmit: ${
          error instanceof Error ? error.message : String(error)
        }`
      )
    }
  }

  return (
    <div className="relative mx-auto mb-1 flex w-full max-w-2xl flex-col items-end justify-center gap-y-2 font-geist">
      {/* Image preview bar */}
      {selectedFiles.length > 0 && (
        <div className="flex w-full gap-2 overflow-x-auto rounded-lg border border-accent bg-primaryAccent p-2">
          {selectedFiles.map((file, index) => (
            <div key={`${file.name}-${index}`} className="group relative flex-shrink-0">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={previewUrls[index]}
                alt={file.name}
                className="h-16 w-16 rounded-md object-cover"
              />
              <button
                type="button"
                onClick={() => removeFile(index)}
                className="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-destructive text-xs text-white opacity-0 transition-opacity group-hover:opacity-100 focus:opacity-100"
                aria-label={`Remove ${file.name}`}
              >
                &times;
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Input row */}
      <div className="flex w-full items-end gap-x-2">
        <input
          type="file"
          accept="image/*"
          multiple
          ref={fileInputRef}
          onChange={handleFileSelect}
          className="hidden"
        />
        <TextArea
          placeholder={'Ask anything'}
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={(e) => {
            if (
              e.key === 'Enter' &&
              !e.nativeEvent.isComposing &&
              !e.shiftKey &&
              !isStreaming
            ) {
              e.preventDefault()
              handleSubmit()
            }
          }}
          className="w-full border border-accent bg-primaryAccent px-4 text-sm text-primary focus:border-accent"
          disabled={!(selectedAgent || teamId)}
          ref={chatInputRef}
        />
        <Button
          onClick={() => fileInputRef.current?.click()}
          disabled={!(selectedAgent || teamId) || isStreaming}
          size="icon"
          variant="ghost"
          className="rounded-xl p-5 text-primary hover:bg-accent"
          aria-label="Attach images"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" />
          </svg>
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={
            !(selectedAgent || teamId) ||
            (!inputMessage.trim() && selectedFiles.length === 0) ||
            isStreaming
          }
          size="icon"
          className="rounded-xl bg-primary p-5 text-primaryAccent"
        >
          <Icon type="send" color="primaryAccent" />
        </Button>
      </div>
    </div>
  )
}

export default ChatInput
