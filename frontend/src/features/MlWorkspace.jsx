import { useEffect, useMemo, useState } from 'react';
import {
  analyzeVideo,
  getVideoAnalysis,
  listVideoAnalyses,
} from '../api/signLanguageApi';
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

function formatTimestamp(seconds) {
  if (seconds === null || seconds === undefined) {
    return 'Unknown';
  }

  return `${seconds.toFixed(3)} s`;
}

function buildSummary(result) {
  if (!result) {
    return [];
  }

  return [
    { label: 'Upload', value: result.filename || 'Unnamed video' },
    { label: 'Total frames', value: result.total_frames ?? 'Unknown' },
    { label: 'Frames sampled', value: result.frames_extracted ?? 'Unknown' },
    { label: 'Frames with hands', value: result.frames_with_hands ?? 'Unknown' },
    { label: 'Frame rate', value: result.fps ? `${result.fps} fps` : 'Unknown' },
    {
      label: 'Duration',
      value:
        result.duration_seconds !== null && result.duration_seconds !== undefined
          ? `${Number(result.duration_seconds).toFixed(2)} s`
          : 'Unknown'
    },
    { label: 'Recording ID', value: result.recording_id ?? 'Not saved' },
    { label: 'Transcript ID', value: result.transcript_id ?? 'Not saved' }
  ];
}

function buildAnalysisLabel(item) {
  const handsLabel =
    item.frames_with_hands !== null && item.frames_with_hands !== undefined
      ? `${item.frames_with_hands} mapped`
      : 'No mappings';
  return `${item.filename} (${item.frames_extracted ?? 0} sampled, ${handsLabel})`;
}

export default function MlWorkspace() {
  const [file, setFile] = useState(null);
  const [videoPreviewUrl, setVideoPreviewUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [analyses, setAnalyses] = useState([]);
  const [selectedAnalysisId, setSelectedAnalysisId] = useState('');
  const [selectedFramePosition, setSelectedFramePosition] = useState(0);

  useEffect(() => {
    let isMounted = true;

    async function loadAnalyses() {
      const result = await listVideoAnalyses();
      if (!isMounted || !result.ok) {
        return;
      }

      const nextAnalyses = result.body?.analyses ?? [];
      setAnalyses(nextAnalyses);
      if (!selectedAnalysisId && nextAnalyses.length) {
        setSelectedAnalysisId(nextAnalyses[0].analysis_id);
      }
    }

    loadAnalyses().catch(() => {});

    return () => {
      isMounted = false;
    };
  }, [selectedAnalysisId]);

  useEffect(() => {
    if (!file) {
      setVideoPreviewUrl('');
      return undefined;
    }

    const nextUrl = URL.createObjectURL(file);
    setVideoPreviewUrl(nextUrl);

    return () => URL.revokeObjectURL(nextUrl);
  }, [file]);

  useEffect(() => {
    if (!selectedAnalysisId) {
      setAnalysis(null);
      setSelectedFramePosition(0);
      return;
    }

    let isMounted = true;

    async function loadAnalysis() {
      const result = await getVideoAnalysis(selectedAnalysisId);
      if (!isMounted) {
        return;
      }

      if (!result.ok) {
        setErrorMessage(result.body?.detail || 'Unable to load the saved analysis.');
        return;
      }

      setAnalysis(result.body);
      setSelectedFramePosition(
        Math.max(
          0,
          result.body?.frames?.find((frame) => frame.hand_count > 0)?.frame_position ?? 0
        )
      );
    }

    loadAnalysis().catch((error) => {
      if (isMounted) {
        setErrorMessage(error.message || 'Unable to load the saved analysis.');
      }
    });

    return () => {
      isMounted = false;
    };
  }, [selectedAnalysisId]);

  const summaryStats = useMemo(() => buildSummary(analysis), [analysis]);
  const selectedFrame =
    analysis?.frames?.find((frame) => frame.frame_position === selectedFramePosition) ?? null;
  const frames = analysis?.frames ?? [];

  const handleFileChange = (event) => {
    const nextFile = event.target.files?.[0] ?? null;
    setFile(nextFile);
    setSuccessMessage('');
    setErrorMessage('');
  };

  const refreshAnalyses = async (nextSelectedId = '') => {
    const result = await listVideoAnalyses();
    if (!result.ok) {
      return;
    }

    const nextAnalyses = result.body?.analyses ?? [];
    setAnalyses(nextAnalyses);
    if (nextSelectedId) {
      setSelectedAnalysisId(nextSelectedId);
    } else if (nextAnalyses.length && !selectedAnalysisId) {
      setSelectedAnalysisId(nextAnalyses[0].analysis_id);
    }
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

    try {
      const result = await analyzeVideo(file);

      if (!result.ok) {
        setErrorMessage(
          result.body?.detail || `Video analysis failed with status ${result.status}.`
        );
        return;
      }

      setAnalysis(result.body);
      setSelectedAnalysisId(result.body.analysis_id);
      setSelectedFramePosition(
        Math.max(0, result.body?.frames?.find((frame) => frame.hand_count > 0)?.frame_position ?? 0)
      );
      setSuccessMessage(result.body?.message || 'Video processed successfully.');
      await refreshAnalyses(result.body.analysis_id);
    } catch (error) {
      setErrorMessage(error.message || 'Video analysis request failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setSuccessMessage('');
    setErrorMessage('');
  };

  return (
    <SectionCard
      title="Video Analysis Workspace"
      description="Upload a sign-language video, then reopen saved analyses to verify MediaPipe hand mappings frame by frame."
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
              Upload a video, then select it below to inspect the annotated frames and landmark
              coordinates.
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

          <div className="saved-analysis-picker">
            <label htmlFor="saved-analysis-select">Saved uploads</label>
            <select
              id="saved-analysis-select"
              value={selectedAnalysisId}
              onChange={(event) => {
                setSelectedAnalysisId(event.target.value);
                setErrorMessage('');
                setSuccessMessage('');
              }}
            >
              <option value="">Select an uploaded video</option>
              {analyses.map((item) => (
                <option key={item.analysis_id} value={item.analysis_id}>
                  {buildAnalysisLabel(item)}
                </option>
              ))}
            </select>
          </div>

          {errorMessage ? <div className="status-banner status-error">{errorMessage}</div> : null}
          {successMessage ? (
            <div className="status-banner status-success">{successMessage}</div>
          ) : null}
        </form>

        <div className="video-results-panel">
          <div className="video-preview-shell">
            {videoPreviewUrl || analysis?.video_url ? (
              <video
                className="video-preview"
                controls
                src={videoPreviewUrl || analysis?.video_url}
              />
            ) : (
              <div className="video-preview video-preview-empty">
                Preview appears here after you choose a file or reopen a saved upload.
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
              The backend samples frames and runs MediaPipe hand mapping.
            </div>
            <div className="checklist-row">
              <span>3</span>
              Reopen the saved upload to verify each annotated frame.
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
            No saved analysis is selected. Upload a video or choose an existing upload to inspect its
            frame mappings.
          </p>
        )}
      </div>

      <div className="analysis-results">
        <h3>Frame verification</h3>
        {selectedFrame ? (
          <div className="frame-review-layout">
            <div className="frame-viewer">
              <img
                className="annotated-frame-image"
                src={selectedFrame.image_url}
                alt={`Annotated frame ${selectedFrame.frame_position}`}
              />
              <div className="frame-meta-grid">
                <div>
                  <span className="eyebrow">Frame</span>
                  <strong>{selectedFrame.original_frame_index}</strong>
                </div>
                <div>
                  <span className="eyebrow">Timestamp</span>
                  <strong>{formatTimestamp(selectedFrame.timestamp_seconds)}</strong>
                </div>
                <div>
                  <span className="eyebrow">Hands</span>
                  <strong>{selectedFrame.hand_count}</strong>
                </div>
                <div>
                  <span className="eyebrow">Landmarks</span>
                  <strong>{selectedFrame.landmarks_detected}</strong>
                </div>
              </div>
            </div>

            <div className="frame-sidebar">
              <div className="frame-selector-list">
                {frames.map((frame) => (
                  <button
                    key={frame.frame_position}
                    type="button"
                    className={`frame-chip ${
                      frame.frame_position === selectedFramePosition ? 'frame-chip-active' : ''
                    }`}
                    onClick={() => setSelectedFramePosition(frame.frame_position)}
                  >
                    <strong>Frame {frame.original_frame_index}</strong>
                    <span>{frame.hand_count} hands detected</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <p className="supporting-text">
            No frame data is available yet. Run an analysis to generate MediaPipe mappings.
          </p>
        )}
      </div>

      <div className="analysis-results">
        <h3>Landmark mappings</h3>
        {selectedFrame?.hands?.length ? (
          <div className="hands-grid">
            {selectedFrame.hands.map((hand) => (
              <article className="hand-card" key={hand.hand_index}>
                <h4>Hand {hand.hand_index + 1}</h4>
                <div className="landmark-table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>X</th>
                        <th>Y</th>
                        <th>Z</th>
                      </tr>
                    </thead>
                    <tbody>
                      {hand.landmarks.map((landmark) => (
                        <tr key={`${hand.hand_index}-${landmark.index}`}>
                          <td>{landmark.name}</td>
                          <td>{landmark.x}</td>
                          <td>{landmark.y}</td>
                          <td>{landmark.z}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <p className="supporting-text">
            The selected frame did not contain a detected hand mapping. Pick another sampled frame.
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
