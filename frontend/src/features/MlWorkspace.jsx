import { useEffect, useMemo, useState } from 'react';
import { analyzeVideo } from '../api/signLanguageApi';
import SectionCard from '../components/SectionCard';

function formatFileSize(bytes) {
  if (!bytes) {
    return '0 B';
  }

  const units = ['B', 'KB', 'MB', 'GB'];
  let value = bytes;
  let unitIndex = 0;

  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex += 1;
  }

  return `${value.toFixed(value >= 10 || unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`;
}

function buildSummary(result) {
  if (!result) {
    return [];
  }

  return [
    { label: 'Upload', value: result.filename || 'Unnamed video' },
    { label: 'Total frames', value: result.total_frames ?? 'Unknown' },
    { label: 'Frames sampled', value: result.frames_extracted ?? 'Unknown' },
    { label: 'Frame rate', value: result.fps ? `${result.fps} fps` : 'Unknown' },
    {
      label: 'Duration',
      value: result.duration_seconds ? `${result.duration_seconds.toFixed(2)} s` : 'Unknown'
    },
    { label: 'Recording ID', value: result.recording_id ?? 'Not saved' },
    { label: 'Transcript ID', value: result.transcript_id ?? 'Not saved' }
  ];
}

export default function MlWorkspace() {
  const [file, setFile] = useState(null);
  const [videoPreviewUrl, setVideoPreviewUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [analysis, setAnalysis] = useState(null);

  useEffect(() => {
    if (!file) {
      setVideoPreviewUrl('');
      return undefined;
    }

    const nextUrl = URL.createObjectURL(file);
    setVideoPreviewUrl(nextUrl);

    return () => URL.revokeObjectURL(nextUrl);
  }, [file]);

  const summaryStats = useMemo(() => buildSummary(analysis), [analysis]);

  const handleFileChange = (event) => {
    const nextFile = event.target.files?.[0] ?? null;
    setFile(nextFile);
    setAnalysis(null);
    setSuccessMessage('');
    setErrorMessage('');
  };

  const handleAnalyze = async (event) => {
    event.preventDefault();

    if (!file) {
      setErrorMessage('Select a video file before running analysis.');
      return;
    }

    setLoading(true);
    setErrorMessage('');
    setSuccessMessage('');
    setAnalysis(null);

    try {
      const result = await analyzeVideo(file);

      if (!result.ok) {
        setErrorMessage(
          result.body?.detail || `Video analysis failed with status ${result.status}.`
        );
        return;
      }

      setAnalysis(result.body);
      setSuccessMessage(result.body?.message || 'Video processed successfully.');
    } catch (error) {
      setErrorMessage(error.message || 'Video analysis request failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setAnalysis(null);
    setSuccessMessage('');
    setErrorMessage('');
  };

  return (
    <SectionCard
      title="Video Analysis Workspace"
      description="Upload a sign-language video, send it to the FastAPI pipeline, and inspect the stored analysis result without leaving the app."
    >
      <div className="video-analysis-layout">
        <form className="video-upload-form" onSubmit={handleAnalyze}>
          <div className="video-dropzone">
            <label htmlFor="video-analysis-input">Source video</label>
            <input
              id="video-analysis-input"
              type="file"
              accept="video/*"
              onChange={handleFileChange}
            />
            <p className="supporting-text">
              Supported input depends on the browser and backend codecs. Start with `.mp4`.
            </p>
          </div>

          <div className="video-file-meta">
            <div>
              <span className="eyebrow">Selected file</span>
              <strong>{file?.name || 'No file selected'}</strong>
            </div>
            <div>
              <span className="eyebrow">Size</span>
              <strong>{file ? formatFileSize(file.size) : '0 B'}</strong>
            </div>
            <div>
              <span className="eyebrow">Type</span>
              <strong>{file?.type || 'Unknown'}</strong>
            </div>
          </div>

          <div className="video-actions">
            <button type="submit" disabled={loading}>
              {loading ? 'Analyzing video...' : 'Analyze video'}
            </button>
            <button type="button" className="button-secondary" onClick={handleReset}>
              Clear
            </button>
          </div>

          {errorMessage ? <div className="status-banner status-error">{errorMessage}</div> : null}
          {successMessage ? (
            <div className="status-banner status-success">{successMessage}</div>
          ) : null}
        </form>

        <div className="video-results-panel">
          <div className="video-preview-shell">
            {videoPreviewUrl ? (
              <video className="video-preview" controls src={videoPreviewUrl} />
            ) : (
              <div className="video-preview video-preview-empty">
                Preview appears here after you choose a file.
              </div>
            )}
          </div>

          <div className="analysis-checklist">
            <div className="checklist-row">
              <span>1</span>
              Upload a local sign-language recording.
            </div>
            <div className="checklist-row">
              <span>2</span>
              The backend extracts and preprocesses frames.
            </div>
            <div className="checklist-row">
              <span>3</span>
              Metadata and generated IDs are returned here.
            </div>
          </div>
        </div>
      </div>

      <div className="analysis-results">
        <h3>Analysis summary</h3>
        {summaryStats.length ? (
          <div className="analysis-grid">
            {summaryStats.map((item) => (
              <article className="analysis-stat" key={item.label}>
                <span className="eyebrow">{item.label}</span>
                <strong>{item.value}</strong>
              </article>
            ))}
          </div>
        ) : (
          <p className="supporting-text">
            No analysis has been run yet. Upload a video to inspect frame and storage metadata.
          </p>
        )}
      </div>

      <div className="analysis-results">
        <h3>Raw response</h3>
        <pre className="ml-output">
          {analysis ? JSON.stringify(analysis, null, 2) : 'Run an analysis to view the API response.'}
        </pre>
      </div>
    </SectionCard>
  );
}
