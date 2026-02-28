"use client"

import { useCallback, useState, useRef } from "react"
import { Upload, FileText, X } from "lucide-react"
import { cn } from "@/lib/utils"

interface EssayUploaderProps {
  onTextLoaded: (text: string, fileName: string) => void
  isProcessing: boolean
}

export function EssayUploader({ onTextLoaded, isProcessing }: EssayUploaderProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [fileName, setFileName] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = useCallback(
    (file: File) => {
      if (!file.name.endsWith(".txt")) {
        alert("Please upload a .txt file")
        return
      }

      const reader = new FileReader()
      reader.onload = (e) => {
        const text = e.target?.result as string
        setFileName(file.name)
        onTextLoaded(text, file.name)
      }
      reader.readAsText(file)
    },
    [onTextLoaded]
  )

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)
      const file = e.dataTransfer.files[0]
      if (file) handleFile(file)
    },
    [handleFile]
  )

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) handleFile(file)
    },
    [handleFile]
  )

  const clearFile = useCallback(() => {
    setFileName(null)
    if (inputRef.current) {
      inputRef.current.value = ""
    }
  }, [])

  return (
    <div className="w-full">
      {!fileName ? (
        <label
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={cn(
            "flex flex-col items-center justify-center w-full min-h-[200px] rounded-xl border-2 border-dashed cursor-pointer transition-all duration-200",
            isDragging
              ? "border-primary bg-primary/5 scale-[1.01]"
              : "border-border bg-card hover:border-primary/50 hover:bg-muted/50"
          )}
        >
          <div className="flex flex-col items-center gap-3 p-8">
            <div className={cn(
              "rounded-full p-4 transition-colors",
              isDragging ? "bg-primary/10" : "bg-muted"
            )}>
              <Upload className={cn(
                "h-6 w-6 transition-colors",
                isDragging ? "text-primary" : "text-muted-foreground"
              )} />
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-foreground">
                {isDragging ? "Drop your essay here" : "Upload your essay"}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Drag and drop a .txt file or click to browse
              </p>
            </div>
          </div>
          <input
            ref={inputRef}
            type="file"
            accept=".txt"
            className="sr-only"
            onChange={handleChange}
            disabled={isProcessing}
          />
        </label>
      ) : (
        <div className="flex items-center gap-3 rounded-xl border border-border bg-card p-4">
          <div className="rounded-lg bg-primary/10 p-2.5">
            <FileText className="h-5 w-5 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-foreground truncate">
              {fileName}
            </p>
            <p className="text-xs text-muted-foreground">Ready for analysis</p>
          </div>
          {!isProcessing && (
            <button
              onClick={clearFile}
              className="rounded-lg p-1.5 text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
              aria-label="Remove file"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      )}
    </div>
  )
}
