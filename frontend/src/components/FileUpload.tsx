import { useRef, useState, useCallback } from 'react';

interface FileUploadProps {
  label: string;
  icon: string;
  file: File | null;
  onFileSelect: (file: File) => void;
  onFileRemove: () => void;
  accept?: string;
  maxSizeMB?: number;
}

export default function FileUpload({
  label,
  icon,
  file,
  onFileSelect,
  onFileRemove,
  accept = '.pdf',
  maxSizeMB = 10,
}: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateFile = useCallback(
    (f: File): string | null => {
      if (!f.name.toLowerCase().endsWith('.pdf')) {
        return 'Only PDF files are supported. Please upload a .pdf file.';
      }
      if (f.size > maxSizeMB * 1024 * 1024) {
        return `File is too large. Maximum size is ${maxSizeMB}MB.`;
      }
      if (f.size === 0) {
        return 'This file appears to be empty. Please choose a different file.';
      }
      return null;
    },
    [maxSizeMB]
  );

  const handleFile = useCallback(
    (f: File) => {
      const validationError = validateFile(f);
      if (validationError) {
        setError(validationError);
        return;
      }
      setError(null);
      onFileSelect(f);
    },
    [validateFile, onFileSelect]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const f = e.dataTransfer.files[0];
      if (f) handleFile(f);
    },
    [handleFile]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const f = e.target.files?.[0];
      if (f) handleFile(f);
      // Reset input so re-uploading same file triggers onChange
      if (inputRef.current) inputRef.current.value = '';
    },
    [handleFile]
  );

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="file-upload-card">
      <div className="file-upload-card-title">
        <span className="card-icon">{icon}</span>
        {label}
      </div>

      {file ? (
        <div className="file-selected">
          <span className="file-selected-icon">📄</span>
          <div className="file-selected-info">
            <div className="file-selected-name">{file.name}</div>
            <div className="file-selected-size">{formatSize(file.size)}</div>
          </div>
          <button
            className="file-remove-btn"
            onClick={() => {
              onFileRemove();
              setError(null);
            }}
            aria-label={`Remove ${label}`}
            title="Remove file"
          >
            ✕
          </button>
        </div>
      ) : (
        <div
          className={`dropzone ${dragOver ? 'drag-over' : ''}`}
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click();
          }}
          role="button"
          tabIndex={0}
          aria-label={`Upload ${label}`}
        >
          <div className="dropzone-icon">📎</div>
          <div className="dropzone-text">
            Drag & drop your file here, or <strong>browse</strong>
          </div>
          <div className="dropzone-hint">PDF only · Max {maxSizeMB}MB</div>
        </div>
      )}

      {error && (
        <div className="file-error">
          <span>⚠️</span>
          {error}
        </div>
      )}

      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleChange}
        style={{ display: 'none' }}
        aria-hidden="true"
      />
    </div>
  );
}
