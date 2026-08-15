import { useState } from 'react';
import FileUpload from './FileUpload';
import TextInput from './TextInput';

interface UploadSectionProps {
  resumeFile: File | null;
  jdFile: File | null;
  jdText: string;
  onResumeSelect: (file: File) => void;
  onResumeRemove: () => void;
  onJdFileSelect: (file: File) => void;
  onJdFileRemove: () => void;
  onJdTextChange: (text: string) => void;
  onLoadSample: () => void;
}

export default function UploadSection({
  resumeFile,
  jdFile,
  jdText,
  onResumeSelect,
  onResumeRemove,
  onJdFileSelect,
  onJdFileRemove,
  onJdTextChange,
  onLoadSample,
}: UploadSectionProps) {
  const [jdMode, setJdMode] = useState<'upload' | 'paste'>('upload');

  return (
    <section className="upload-section" id="upload">
      <div className="upload-header-row">
        <h2 className="upload-section-title">
          📄 Upload your documents to get started
        </h2>
        <button
          type="button"
          className="sample-data-btn"
          onClick={() => {
            setJdMode('paste');
            onLoadSample();
          }}
          title="Load pre-filled sample resume and job description to test instantly"
        >
          ✨ Try with Sample Data
        </button>
      </div>

      <div className="upload-grid">
        {/* Resume Upload */}
        <FileUpload
          label="Resume"
          icon="📋"
          file={resumeFile}
          onFileSelect={onResumeSelect}
          onFileRemove={onResumeRemove}
        />

        {/* Job Description */}
        <div className="file-upload-card">
          <div className="file-upload-card-title">
            <span className="card-icon">💼</span>
            Job Description
          </div>

          {/* Toggle: Upload / Paste */}
          <div className="jd-input-toggle">
            <button
              className={`jd-toggle-btn ${jdMode === 'upload' ? 'active' : ''}`}
              onClick={() => setJdMode('upload')}
            >
              📎 Upload PDF
            </button>
            <button
              className={`jd-toggle-btn ${jdMode === 'paste' ? 'active' : ''}`}
              onClick={() => setJdMode('paste')}
            >
              📝 Paste Text
            </button>
          </div>

          {jdMode === 'upload' ? (
            <FileUpload
              label="Job Description"
              icon="💼"
              file={jdFile}
              onFileSelect={onJdFileSelect}
              onFileRemove={onJdFileRemove}
            />
          ) : (
            <TextInput value={jdText} onChange={onJdTextChange} />
          )}
        </div>
      </div>
    </section>
  );
}
