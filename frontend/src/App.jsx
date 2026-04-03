import { useEffect, useMemo, useRef, useState } from 'react';
import { login, register } from './api/authApi';
import {
  addGestureLabel,
  createDataset,
  getDataset,
  listDatasets,
  recognizeGestureFrame,
  trainDataset,
  uploadGestureVideo,
} from './api/mlApi';
import {
  analyzeVideo,
  getVideoAnalysis,
  listVideoAnalyses,
} from './api/signLanguageApi';

function formatAccuracy(value) {
  return value || value === 0 ? `${value}%` : 'Untrained';
}

function formatDuration(value) {
  if (!value && value !== 0) {
    return 'Unknown';
  }

  if (value < 60) {
    return `${value.toFixed(1)}s`;
  }

  const minutes = Math.floor(value / 60);
  const seconds = Math.round(value % 60);
  return `${minutes}m ${seconds}s`;
}

function formatFileSize(bytes) {
  if (!bytes) {
    return '0 B';
  }

  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }

  return `${size.toFixed(size >= 10 || unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`;
}

function formatConfidence(value) {
  if (value == null) {
    return 'Confidence unavailable';
  }

  return `${Math.round(value * 100)}% confidence`;
}

function getSupportedRecordingMimeType() {
  if (typeof MediaRecorder === 'undefined') {
    return '';
  }

  const candidates = [
    'video/webm;codecs=vp9,opus',
    'video/webm;codecs=vp8,opus',
    'video/webm',
    'video/mp4',
  ];

  return candidates.find((type) => MediaRecorder.isTypeSupported(type)) || '';
}

function buildHistorySubtitle(item) {
  const parts = [];

  if (item.duration_seconds || item.duration_seconds === 0) {
    parts.push(formatDuration(item.duration_seconds));
  }

  if (item.frames_extracted || item.frames_extracted === 0) {
    parts.push(`${item.frames_extracted} sampled frames`);
  }

  if (item.frames_with_hands || item.frames_with_hands === 0) {
    parts.push(`${item.frames_with_hands} with hands`);
  }

  return parts.join(' • ');
}

export default function App() {
  const [authMode, setAuthMode] = useState('login');
  const [authEmail, setAuthEmail] = useState('');
  const [authName, setAuthName] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authLoading, setAuthLoading] = useState(false);
  const [authMessage, setAuthMessage] = useState('');
  const [authError, setAuthError] = useState('');
  const [currentUser, setCurrentUser] = useState(null);

  const [datasets, setDatasets] = useState([]);
  const [datasetsLoading, setDatasetsLoading] = useState(false);
  const [selectedDatasetId, setSelectedDatasetId] = useState('');
  const [datasetDetail, setDatasetDetail] = useState(null);
  const [datasetDetailLoading, setDatasetDetailLoading] = useState(false);
  const [modelMessage, setModelMessage] = useState('');
  const [modelError, setModelError] = useState('');

  const [createModelName, setCreateModelName] = useState('');
  const [newGestureLabel, setNewGestureLabel] = useState('');
  const [selectedGesture, setSelectedGesture] = useState('');
  const [trainingVideo, setTrainingVideo] = useState(null);
  const [creatingModel, setCreatingModel] = useState(false);
  const [addingGesture, setAddingGesture] = useState(false);
  const [uploadingTrainingVideo, setUploadingTrainingVideo] = useState(false);
  const [trainingModel, setTrainingModel] = useState(false);

  const [analysisModelId, setAnalysisModelId] = useState('');
  const [analysisVideo, setAnalysisVideo] = useState(null);
  const [analysisVideoUrl, setAnalysisVideoUrl] = useState('');
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState('');
  const [analysisMessage, setAnalysisMessage] = useState('');
  const [latestAnalysis, setLatestAnalysis] = useState(null);
  const [analysisVideoSource, setAnalysisVideoSource] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDurationSeconds, setRecordingDurationSeconds] = useState(0);
  const [recordingStatus, setRecordingStatus] = useState('');
  const [recordingError, setRecordingError] = useState('');
  const [livePrediction, setLivePrediction] = useState('');
  const [livePredictionConfidence, setLivePredictionConfidence] = useState(null);
  const [liveHandCount, setLiveHandCount] = useState(null);

  const [historyItems, setHistoryItems] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [selectedHistoryId, setSelectedHistoryId] = useState('');
  const [selectedHistory, setSelectedHistory] = useState(null);
  const [historyError, setHistoryError] = useState('');

  const liveVideoRef = useRef(null);
  const liveCanvasRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const recordingChunksRef = useRef([]);
  const recordingTimerRef = useRef(null);
  const livePredictionTimerRef = useRef(null);
  const livePredictionPendingRef = useRef(false);
  const analysisModelIdRef = useRef('');

  const labelDetails = datasetDetail?.label_details ?? [];
  const trainedDatasets = useMemo(
    () => datasets.filter((dataset) => dataset.trained),
    [datasets]
  );
  const recordingSupported =
    typeof navigator !== 'undefined' &&
    typeof MediaRecorder !== 'undefined' &&
    Boolean(navigator.mediaDevices?.getUserMedia);

  useEffect(() => {
    if (!analysisVideo) {
      setAnalysisVideoUrl('');
      return undefined;
    }

    const nextUrl = URL.createObjectURL(analysisVideo);
    setAnalysisVideoUrl(nextUrl);
    return () => URL.revokeObjectURL(nextUrl);
  }, [analysisVideo]);

  useEffect(() => {
    analysisModelIdRef.current = analysisModelId;
  }, [analysisModelId]);

  useEffect(() => {
    if (!isRecording || !streamRef.current || !liveVideoRef.current) {
      return;
    }

    const liveVideo = liveVideoRef.current;
    liveVideo.srcObject = streamRef.current;
    liveVideo.muted = true;
    liveVideo.playsInline = true;

    const ensurePlayback = async () => {
      if (liveVideo.readyState < 1) {
        await new Promise((resolve) => {
          liveVideo.onloadedmetadata = () => resolve();
        });
      }

      await liveVideo.play().catch(() => {});
    };

    ensurePlayback().catch(() => {});

    return () => {
      liveVideo.onloadedmetadata = null;
    };
  }, [isRecording]);

  useEffect(() => {
    if (recordingTimerRef.current) {
      window.clearInterval(recordingTimerRef.current);
      recordingTimerRef.current = null;
    }

    if (!isRecording) {
      return undefined;
    }

    recordingTimerRef.current = window.setInterval(() => {
      setRecordingDurationSeconds((current) => current + 1);
    }, 1000);

    return () => {
      if (recordingTimerRef.current) {
        window.clearInterval(recordingTimerRef.current);
        recordingTimerRef.current = null;
      }
    };
  }, [isRecording]);

  useEffect(() => {
    if (livePredictionTimerRef.current) {
      window.clearInterval(livePredictionTimerRef.current);
      livePredictionTimerRef.current = null;
    }

    if (!isRecording) {
      return undefined;
    }

    if (!analysisModelId) {
      setLivePrediction('Select a trained model to see live gesture hints.');
      setLivePredictionConfidence(null);
      setLiveHandCount(null);
      return undefined;
    }

    livePredictionTimerRef.current = window.setInterval(() => {
      captureLivePrediction().catch(() => {});
    }, 1200);

    captureLivePrediction().catch(() => {});

    return () => {
      if (livePredictionTimerRef.current) {
        window.clearInterval(livePredictionTimerRef.current);
        livePredictionTimerRef.current = null;
      }
    };
  }, [analysisModelId, isRecording]);

  const clearModelFeedback = () => {
    setModelMessage('');
    setModelError('');
  };

  const stopLiveStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (liveVideoRef.current) {
      liveVideoRef.current.srcObject = null;
    }
  };

  const resetLiveFeedback = () => {
    setLivePrediction('');
    setLivePredictionConfidence(null);
    setLiveHandCount(null);
    livePredictionPendingRef.current = false;
  };

  async function captureLivePrediction() {
    const datasetId = analysisModelIdRef.current;
    const video = liveVideoRef.current;
    const canvas = liveCanvasRef.current;

    if (!datasetId || !video || !canvas || livePredictionPendingRef.current) {
      return;
    }

    if (video.readyState < 2 || !video.videoWidth || !video.videoHeight) {
      return;
    }

    livePredictionPendingRef.current = true;

    try {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      const context = canvas.getContext('2d');
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      const blob = await new Promise((resolve) => {
        canvas.toBlob(resolve, 'image/jpeg', 0.92);
      });

      if (!blob) {
        return;
      }

      const frameFile = new File([blob], 'live-frame.jpg', { type: 'image/jpeg' });
      const result = await recognizeGestureFrame(datasetId, frameFile);

      if (!result.ok) {
        setLivePrediction(result.body?.detail || 'Live prediction unavailable.');
        setLivePredictionConfidence(null);
        setLiveHandCount(null);
        return;
      }

      const body = result.body ?? {};
      setLiveHandCount(body.hand_count ?? null);

      if (body.label) {
        setLivePrediction(body.label);
        setLivePredictionConfidence(body.confidence ?? null);
        return;
      }

      setLivePrediction(body.hand_count ? 'Hand detected, waiting for a clearer pose.' : 'No hands detected.');
      setLivePredictionConfidence(null);
    } finally {
      livePredictionPendingRef.current = false;
    }
  }

  useEffect(() => {
    return () => {
      if (recordingTimerRef.current) {
        window.clearInterval(recordingTimerRef.current);
      }
      if (livePredictionTimerRef.current) {
        window.clearInterval(livePredictionTimerRef.current);
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
      stopLiveStream();
    };
  }, []);

  async function loadDatasets(preferredDatasetId = '') {
    setDatasetsLoading(true);
    const result = await listDatasets();
    setDatasetsLoading(false);

    if (!result.ok) {
      setModelError(result.body?.detail || 'Unable to load models.');
      return [];
    }

    const nextDatasets = result.body?.datasets ?? [];
    setDatasets(nextDatasets);

    const nextSelectedId =
      preferredDatasetId ||
      (nextDatasets.some((item) => String(item.dataset_id) === String(selectedDatasetId))
        ? selectedDatasetId
        : nextDatasets[0]?.dataset_id ?? '');

    setSelectedDatasetId(nextSelectedId ? String(nextSelectedId) : '');
    return nextDatasets;
  }

  async function loadHistory(preferredAnalysisId = '') {
    setHistoryLoading(true);
    const result = await listVideoAnalyses();
    setHistoryLoading(false);

    if (!result.ok) {
      setHistoryError(result.body?.detail || 'Unable to load past analyses.');
      return [];
    }

    const nextHistory = result.body?.analyses ?? [];
    setHistoryItems(nextHistory);

    const nextSelectedId =
      preferredAnalysisId ||
      (nextHistory.some((item) => item.analysis_id === selectedHistoryId)
        ? selectedHistoryId
        : nextHistory[0]?.analysis_id ?? '');

    setSelectedHistoryId(nextSelectedId);
    return nextHistory;
  }

  useEffect(() => {
    if (!currentUser) {
      return;
    }

    loadDatasets().catch((error) => {
      setModelError(error.message || 'Unable to load models.');
    });
    loadHistory().catch((error) => {
      setHistoryError(error.message || 'Unable to load past analyses.');
    });
  }, [currentUser]);

  useEffect(() => {
    if (!selectedDatasetId) {
      setDatasetDetail(null);
      setSelectedGesture('');
      return;
    }

    let active = true;

    async function run() {
      setDatasetDetailLoading(true);
      const result = await getDataset(selectedDatasetId);
      if (!active) {
        return;
      }

      setDatasetDetailLoading(false);

      if (!result.ok) {
        setModelError(result.body?.detail || 'Unable to load model details.');
        return;
      }

      const detail = result.body;
      setDatasetDetail(detail);
      setSelectedGesture((current) => {
        if (detail.label_details?.some((item) => item.label === current)) {
          return current;
        }
        return detail.label_details?.[0]?.label ?? '';
      });
    }

    run().catch((error) => {
      if (active) {
        setDatasetDetailLoading(false);
        setModelError(error.message || 'Unable to load model details.');
      }
    });

    return () => {
      active = false;
    };
  }, [selectedDatasetId]);

  useEffect(() => {
    if (!trainedDatasets.length) {
      setAnalysisModelId('');
      return;
    }

    const currentIsValid = trainedDatasets.some(
      (dataset) => String(dataset.dataset_id) === String(analysisModelId)
    );

    if (!currentIsValid) {
      setAnalysisModelId(String(trainedDatasets[0].dataset_id));
    }
  }, [analysisModelId, trainedDatasets]);

  useEffect(() => {
    if (!selectedHistoryId) {
      setSelectedHistory(null);
      return;
    }

    let active = true;

    async function run() {
      setHistoryError('');
      const result = await getVideoAnalysis(selectedHistoryId);
      if (!active) {
        return;
      }

      if (!result.ok) {
        setHistoryError(result.body?.detail || 'Unable to load that analysis.');
        return;
      }

      setSelectedHistory(result.body);
    }

    run().catch((error) => {
      if (active) {
        setHistoryError(error.message || 'Unable to load that analysis.');
      }
    });

    return () => {
      active = false;
    };
  }, [selectedHistoryId]);

  async function refreshSelectedDataset() {
    if (!selectedDatasetId) {
      return;
    }

    const result = await getDataset(selectedDatasetId);
    if (!result.ok) {
      setModelError(result.body?.detail || 'Unable to refresh model details.');
      return;
    }

    setDatasetDetail(result.body);
    setSelectedGesture((current) => {
      if (result.body.label_details?.some((item) => item.label === current)) {
        return current;
      }
      return result.body.label_details?.[0]?.label ?? '';
    });
  }

  async function handleAuthSubmit(event) {
    event.preventDefault();
    setAuthLoading(true);
    setAuthMessage('');
    setAuthError('');

    const result =
      authMode === 'login'
        ? await login(authEmail, authPassword)
        : await register(authEmail, authName.trim(), authPassword);

    setAuthLoading(false);

    if (!result.ok || !result.body?.success) {
      setAuthError(result.body?.message || 'Unable to authenticate.');
      return;
    }

    if (authMode === 'register') {
      setAuthMessage('Registration successful. You can now sign in.');
      setAuthMode('login');
      return;
    }

    setAuthMessage('Login successful.');

    setCurrentUser({
      name: authName.trim() || authEmail.split('@')[0],
      email: authEmail,
    });
  }

  async function handleCreateModel(event) {
    event.preventDefault();
    if (!createModelName.trim()) {
      setModelError('Enter a model name first.');
      return;
    }

    clearModelFeedback();
    setCreatingModel(true);
    const result = await createDataset(createModelName.trim());
    setCreatingModel(false);

    if (!result.ok) {
      setModelError(result.body?.detail || 'Unable to create the model.');
      return;
    }

    setCreateModelName('');
    setModelMessage(`Created model "${result.body.name}" as dataset ${result.body.dataset_id}.`);
    await loadDatasets(result.body.dataset_id);
  }

  async function handleAddGesture(event) {
    event.preventDefault();
    if (!selectedDatasetId) {
      setModelError('Select a model before adding gestures.');
      return;
    }
    if (!newGestureLabel.trim()) {
      setModelError('Enter a gesture label first.');
      return;
    }

    clearModelFeedback();
    setAddingGesture(true);
    const result = await addGestureLabel(selectedDatasetId, newGestureLabel.trim());
    setAddingGesture(false);

    if (!result.ok) {
      setModelError(result.body?.detail || 'Unable to add that gesture.');
      return;
    }

    setNewGestureLabel('');
    setSelectedGesture(result.body.label);
    setModelMessage(`Added "${result.body.label}" to the active model.`);
    await refreshSelectedDataset();
  }

  async function handleUploadTrainingVideo(event) {
    event.preventDefault();
    if (!selectedDatasetId) {
      setModelError('Select a model before uploading examples.');
      return;
    }
    if (!selectedGesture) {
      setModelError('Choose a gesture label first.');
      return;
    }
    if (!trainingVideo) {
      setModelError('Choose a training video first.');
      return;
    }

    clearModelFeedback();
    setUploadingTrainingVideo(true);
    const result = await uploadGestureVideo(selectedDatasetId, selectedGesture, trainingVideo);
    setUploadingTrainingVideo(false);

    if (!result.ok) {
      setModelError(result.body?.detail || 'Unable to ingest the training video.');
      return;
    }

    setTrainingVideo(null);
    setModelMessage(result.body?.message || 'Training samples added successfully.');
    await refreshSelectedDataset();
  }

  async function handleTrainModel() {
    if (!selectedDatasetId) {
      setModelError('Select a model before training.');
      return;
    }

    clearModelFeedback();
    setTrainingModel(true);
    const result = await trainDataset(selectedDatasetId);
    setTrainingModel(false);

    if (!result.ok) {
      setModelError(result.body?.detail || 'Unable to train the model.');
      return;
    }

    setModelMessage(
      `Model trained on ${result.body.sample_count} samples across ${result.body.labels.length} gestures.`
    );
    await loadDatasets(selectedDatasetId);
    await refreshSelectedDataset();
  }

  async function handleStartRecording() {
    if (isRecording) {
      return;
    }

    if (!recordingSupported) {
      setRecordingError('This browser does not support camera recording.');
      return;
    }

    stopLiveStream();
    setRecordingError('');
    setRecordingStatus('');
    setAnalysisError('');
    setAnalysisMessage('');
    resetLiveFeedback();
    setRecordingDurationSeconds(0);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user' },
        audio: false,
      });

      streamRef.current = stream;
      setIsRecording(true);

      const mimeType = getSupportedRecordingMimeType();
      const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);

      recordingChunksRef.current = [];
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          recordingChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        const blobType = recorder.mimeType || mimeType || 'video/webm';
        const clip = new Blob(recordingChunksRef.current, { type: blobType });

        stopLiveStream();
        setIsRecording(false);

        if (!clip.size) {
          setRecordingError('Recording finished, but no clip data was captured.');
          return;
        }

        const extension = blobType.includes('mp4') ? 'mp4' : 'webm';
        const file = new File([clip], `live-recording-${Date.now()}.${extension}`, { type: blobType });

        setAnalysisVideo(file);
        setAnalysisVideoSource('recording');
        setRecordingStatus('Live recording ready. Review it, then run analysis.');
        setAnalysisMessage('Live recording attached. Use the same Analyze video action as an upload.');
      };

      recorder.start(250);
      setRecordingStatus('Recording in progress. Stop when the signer finishes.');
    } catch (error) {
      stopLiveStream();
      setIsRecording(false);
      setRecordingError(error.message || 'Unable to access the camera.');
    }
  }

  function handleStopRecording() {
    if (!mediaRecorderRef.current || mediaRecorderRef.current.state === 'inactive') {
      stopLiveStream();
      setIsRecording(false);
      return;
    }

    setRecordingStatus('Finalizing recording...');
    mediaRecorderRef.current.stop();
  }

  function handleAnalysisVideoChange(event) {
    const file = event.target.files?.[0] ?? null;
    setAnalysisVideo(file);
    setAnalysisVideoSource(file ? 'upload' : '');
    setAnalysisError('');
    setAnalysisMessage(file ? 'Upload ready. Run analysis when you are ready.' : '');
  }

  async function handleAnalyzeVideo(event) {
    event.preventDefault();
    if (!analysisVideo) {
      setAnalysisError('Choose a video to analyze.');
      return;
    }

    setAnalysisLoading(true);
    setAnalysisError('');
    setAnalysisMessage('');

    try {
      const result = await analyzeVideo(analysisVideo, analysisModelId || null);

      if (!result.ok) {
        setAnalysisError(result.body?.detail || 'Video analysis failed.');
        return;
      }

      setLatestAnalysis(result.body);
      setSelectedHistory(result.body);
      setSelectedHistoryId(result.body.analysis_id);
      setAnalysisMessage('Analysis complete. Transcript saved to history.');
      await loadHistory(result.body.analysis_id);
    } catch (error) {
      setAnalysisError(error.message || 'Video analysis failed.');
    } finally {
      setAnalysisLoading(false);
    }
  }

  const currentTranscript =
    latestAnalysis?.transcript_text ||
    selectedHistory?.transcript_text ||
    'Upload a video and run analysis to generate a transcript.';

  const currentVideoUrl =
    analysisVideoUrl || latestAnalysis?.video_url || selectedHistory?.video_url || '';

  const selectedModelSummary = datasets.find(
    (dataset) => String(dataset.dataset_id) === String(selectedDatasetId)
  );

  if (!currentUser) {
    return (
      <main className="auth-shell">
        <section className="auth-panel">
          <p className="panel-eyebrow">{authMode === 'login' ? 'Welcome back' : 'Create account'}</p>
          <h2>{authMode === 'login' ? 'Sign in' : 'Register'}</h2>
          <form className="auth-form" onSubmit={handleAuthSubmit}>
            {authMode === 'register' ? (
              <label>
                Name
                <input
                  type="text"
                  value={authName}
                  onChange={(event) => setAuthName(event.target.value)}
                  placeholder="Your name"
                  autoComplete="name"
                />
              </label>
            ) : null}
            <label>
              Email
              <input
                type="email"
                value={authEmail}
                onChange={(event) => setAuthEmail(event.target.value)}
                placeholder="you@example.com"
                autoComplete="email"
              />
            </label>
            <label>
              Password
              <input
                type="password"
                value={authPassword}
                onChange={(event) => setAuthPassword(event.target.value)}
                placeholder={authMode === 'login' ? 'Enter your password' : 'Create a password'}
                autoComplete={authMode === 'login' ? 'current-password' : 'new-password'}
              />
            </label>
            {authMessage ? <div className="message-banner message-success">{authMessage}</div> : null}
            {authError ? <div className="message-banner message-error">{authError}</div> : null}
            <button type="submit" className="primary-button" disabled={authLoading}>
              {authLoading
                ? authMode === 'login'
                  ? 'Signing in...'
                  : 'Creating account...'
                : authMode === 'login'
                  ? 'Log in'
                  : 'Create account'}
            </button>
            <button
              type="button"
              className="text-button auth-switch"
              onClick={() => {
                setAuthMode((current) => (current === 'login' ? 'register' : 'login'));
                setAuthMessage('');
                setAuthError('');
              }}
            >
              {authMode === 'login' ? 'Need an account? Register here.' : 'Already registered? Sign in here.'}
            </button>
          </form>
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <section className="app-hero">
        <div className="hero-actions">
          <div className="user-chip">
            <span className="user-chip-label">Signed in as</span>
            <strong>{currentUser.email}</strong>
          </div>
          <button type="button" className="secondary-button" onClick={() => setCurrentUser(null)}>
            Log out
          </button>
        </div>
      </section>

      <section className="summary-strip">
        <article className="summary-card">
          <span className="summary-label">Models</span>
          <strong>{datasets.length}</strong>
          <p>{trainedDatasets.length} ready for translation</p>
        </article>
        <article className="summary-card">
          <span className="summary-label">Active model</span>
          <strong>{selectedModelSummary?.name || 'None selected'}</strong>
          <p>{selectedModelSummary ? `Accuracy ${formatAccuracy(selectedModelSummary.accuracy)}` : 'Create one to begin'}</p>
        </article>
        <article className="summary-card">
          <span className="summary-label">Saved analyses</span>
          <strong>{historyItems.length}</strong>
          <p>{selectedHistory?.transcript_text || 'Latest transcript appears here'}</p>
        </article>
      </section>

      <section className="workspace-grid">
        <div className="workspace-column">
          <section className="panel panel-tall">
            <div className="panel-header">
              <div>
                <p className="panel-eyebrow">Step 1</p>
                <h2>Choose or build a model</h2>
              </div>
              {datasetsLoading ? <span className="panel-tag">Loading</span> : null}
            </div>

            <div className="stack">
              <form className="inline-form" onSubmit={handleCreateModel}>
                <label>
                  New model name
                  <input
                    value={createModelName}
                    onChange={(event) => setCreateModelName(event.target.value)}
                    placeholder="Campus Conversation Model"
                  />
                </label>
                  <button type="submit" className="primary-button" disabled={creatingModel}>
                    {creatingModel ? 'Creating...' : 'Create model'}
                  </button>
              </form>

              <label>
                Existing models
                <select
                  value={selectedDatasetId}
                  onChange={(event) => {
                    clearModelFeedback();
                    setSelectedDatasetId(event.target.value);
                  }}
                >
                  {!datasets.length ? <option value="">No models yet</option> : null}
                  {datasets.map((dataset) => (
                    <option key={dataset.dataset_id} value={dataset.dataset_id}>
                      #{dataset.dataset_id} {dataset.name}
                    </option>
                  ))}
                </select>
              </label>

              {modelMessage ? <div className="message-banner message-success">{modelMessage}</div> : null}
              {modelError ? <div className="message-banner message-error">{modelError}</div> : null}

              {datasetDetail ? (
                <div className="metric-grid">
                  <article className="metric-card">
                    <span className="summary-label">Status</span>
                    <strong>{datasetDetail.trained ? 'Trained' : 'Needs training'}</strong>
                    <p>{formatAccuracy(datasetDetail.accuracy)}</p>
                  </article>
                  <article className="metric-card">
                    <span className="summary-label">Gestures</span>
                    <strong>{labelDetails.length}</strong>
                    <p>Labels in this model</p>
                  </article>
                  <article className="metric-card">
                    <span className="summary-label">Samples</span>
                    <strong>
                      {labelDetails.reduce((sum, item) => sum + (item.sample_count ?? 0), 0)}
                    </strong>
                    <p>Extracted landmark samples</p>
                  </article>
                </div>
              ) : (
                <p className="empty-copy">Create a model to unlock training and translation.</p>
              )}
            </div>
          </section>

          <section className="panel">
            <div className="panel-header">
              <div>
                <p className="panel-eyebrow">Step 2</p>
                <h2>Expand the active model</h2>
              </div>
              {datasetDetailLoading ? <span className="panel-tag">Refreshing</span> : null}
            </div>

            <div className="stack">
              <form className="inline-form" onSubmit={handleAddGesture}>
                <label>
                  Add gesture label
                  <input
                    value={newGestureLabel}
                    onChange={(event) => setNewGestureLabel(event.target.value)}
                    placeholder="thank_you"
                  />
                </label>
                <button type="submit" className="secondary-button" disabled={addingGesture}>
                  {addingGesture ? 'Adding...' : 'Add label'}
                </button>
              </form>

              <form className="training-form" onSubmit={handleUploadTrainingVideo}>
                <label>
                  Gesture to extend
                  <select
                    value={selectedGesture}
                    onChange={(event) => setSelectedGesture(event.target.value)}
                  >
                    {!labelDetails.length ? <option value="">No labels yet</option> : null}
                    {labelDetails.map((item) => (
                      <option key={item.def_id} value={item.label}>
                        {item.label}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Training video
                  <input
                    type="file"
                    accept="video/*"
                    onChange={(event) => setTrainingVideo(event.target.files?.[0] ?? null)}
                  />
                </label>

                <div className="button-row">
                  <button
                    type="submit"
                    className="primary-button"
                    disabled={uploadingTrainingVideo}
                  >
                    {uploadingTrainingVideo ? 'Uploading...' : 'Add video examples'}
                  </button>
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={handleTrainModel}
                    disabled={trainingModel}
                  >
                    {trainingModel ? 'Training...' : 'Train model'}
                  </button>
                </div>

                {!trainingVideo && (
                  <div className="message-banner message-neutral">
                    Select a gesture and training clip before using "Add video examples."
                  </div>
                )}
              </form>

              <div className="tag-list">
                {labelDetails.length ? (
                  labelDetails.map((item) => (
                    <span className="tag" key={item.def_id}>
                      {item.label} • {item.sample_count ?? 0} samples
                    </span>
                  ))
                ) : (
                  <p className="empty-copy">No gesture labels yet. Add one, upload examples, then train.</p>
                )}
              </div>
            </div>
          </section>
        </div>

        <div className="workspace-column">
          <section className="panel panel-tall">
            <div className="panel-header">
              <div>
                <p className="panel-eyebrow">Step 3</p>
                <h2>Analyze and translate a video</h2>
              </div>
              {analysisLoading ? <span className="panel-tag">Running</span> : null}
            </div>

            <form className="stack" onSubmit={handleAnalyzeVideo}>
              <label>
                Model for translation
                <select
                  value={analysisModelId}
                  onChange={(event) => setAnalysisModelId(event.target.value)}
                >
                  {!trainedDatasets.length ? (
                    <option value="">No trained models available</option>
                  ) : null}
                  {trainedDatasets.map((dataset) => (
                    <option key={dataset.dataset_id} value={dataset.dataset_id}>
                      #{dataset.dataset_id} {dataset.name} • {formatAccuracy(dataset.accuracy)}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Video to analyze
                <input
                  type="file"
                  accept="video/*"
                  onChange={handleAnalysisVideoChange}
                  disabled={isRecording}
                />
              </label>

              <section className="live-capture-card">
                <div className="live-capture-header">
                  <div>
                    <span className="summary-label">Live recording</span>
                    <h3>Record instead of upload</h3>
                  </div>
                  <span className={`live-indicator${isRecording ? ' live-indicator-active' : ''}`}>
                    {recordingSupported ? (isRecording ? 'Recording' : 'Camera ready') : 'Unavailable'}
                  </span>
                </div>

                <div className="live-preview-shell">
                  {isRecording ? (
                    <video
                      ref={liveVideoRef}
                      className="video-preview live-video-preview"
                      autoPlay
                      muted
                      playsInline
                    />
                  ) : analysisVideoSource === 'recording' && analysisVideoUrl ? (
                    <video className="video-preview" controls src={analysisVideoUrl} />
                  ) : (
                    <div className="preview-empty">
                      Start a short recording here, then analyze it with the same button you use for uploads.
                    </div>
                  )}
                  <canvas ref={liveCanvasRef} className="live-canvas" />
                </div>

                <div className="live-meta-grid">
                  <div className="metric-card live-meta-card">
                    <span className="summary-label">Elapsed</span>
                    <strong>{formatDuration(recordingDurationSeconds)}</strong>
                    <p>{isRecording ? 'Current take length' : 'Ready for the next take'}</p>
                  </div>
                  <div className="metric-card live-meta-card">
                    <span className="summary-label">Live hint</span>
                    <strong>{livePrediction || 'No live hint yet'}</strong>
                    <p>
                      {livePredictionConfidence != null
                        ? formatConfidence(livePredictionConfidence)
                        : liveHandCount
                          ? `${liveHandCount} hand${liveHandCount === 1 ? '' : 's'} detected`
                          : 'Model-guided webcam preview'}
                    </p>
                  </div>
                </div>

                <div className="button-row">
                  <button
                    type="button"
                    className="primary-button"
                    onClick={isRecording ? handleStopRecording : handleStartRecording}
                    disabled={!recordingSupported}
                  >
                    {isRecording ? 'Stop recording' : 'Start live recording'}
                  </button>
                </div>

                {recordingStatus ? (
                  <div className="message-banner message-success">{recordingStatus}</div>
                ) : null}
                {recordingError ? <div className="message-banner message-error">{recordingError}</div> : null}
                {!recordingSupported ? (
                  <div className="message-banner message-neutral">
                    Camera capture is unavailable in this browser. Upload a video instead.
                  </div>
                ) : null}
              </section>

              {analysisVideo ? (
                <div className="upload-meta">
                  <span>
                    {analysisVideoSource === 'recording' ? 'Live recording selected' : analysisVideo.name}
                  </span>
                  <span>{formatFileSize(analysisVideo.size)}</span>
                </div>
              ) : null}

              {analysisMessage ? <div className="message-banner message-success">{analysisMessage}</div> : null}
              {analysisError ? <div className="message-banner message-error">{analysisError}</div> : null}

              <button type="submit" className="primary-button" disabled={analysisLoading || isRecording}>
                {analysisLoading ? 'Analyzing video...' : isRecording ? 'Stop recording first' : 'Analyze video'}
              </button>

              {!analysisVideo && (
                <div className="message-banner message-neutral">
                  Upload a clip or record one live, then run analysis.
                </div>
              )}
            </form>

            <div className="transcript-stage">
              <div className="transcript-card">
                <span className="summary-label">Transcript</span>
                <p className="transcript-text">{currentTranscript}</p>
              </div>
              <div className="preview-card">
                {currentVideoUrl ? (
                  <video className="video-preview" controls src={currentVideoUrl} />
                ) : (
                  <div className="preview-empty">Your uploaded or selected history video appears here.</div>
                )}
              </div>
            </div>
          </section>

          <section className="panel">
            <div className="panel-header">
              <div>
                <p className="panel-eyebrow">Step 4</p>
                <h2>Past uploads and transcripts</h2>
              </div>
              {historyLoading ? <span className="panel-tag">Loading</span> : null}
            </div>

            {historyError ? <div className="message-banner message-error">{historyError}</div> : null}

            <div className="history-layout">
              <div className="history-list">
                {historyItems.length ? (
                  historyItems.map((item) => (
                    <button
                      key={item.analysis_id}
                      type="button"
                      className={`history-item${
                        item.analysis_id === selectedHistoryId ? ' history-item-active' : ''
                      }`}
                      onClick={() => setSelectedHistoryId(item.analysis_id)}
                    >
                      <strong>{item.filename}</strong>
                      <span>{buildHistorySubtitle(item)}</span>
                    </button>
                  ))
                ) : (
                  <p className="empty-copy">No saved analyses yet. The next run will appear here.</p>
                )}
              </div>

              <div className="history-detail">
                {selectedHistory ? (
                  <>
                    <div className="detail-card">
                      <span className="summary-label">Saved transcript</span>
                      <p className="detail-transcript">
                        {selectedHistory.transcript_text || 'No transcript available.'}
                      </p>
                    </div>
                    <div className="metric-grid">
                      <article className="metric-card">
                        <span className="summary-label">Frames</span>
                        <strong>{selectedHistory.frames_extracted ?? 'Unknown'}</strong>
                        <p>Sampled for analysis</p>
                      </article>
                      <article className="metric-card">
                        <span className="summary-label">Hands found</span>
                        <strong>{selectedHistory.frames_with_hands ?? 'Unknown'}</strong>
                        <p>Frames with detections</p>
                      </article>
                      <article className="metric-card">
                        <span className="summary-label">Model used</span>
                        <strong>{selectedHistory.model_id_used ?? 'None'}</strong>
                        <p>Translation source</p>
                      </article>
                    </div>
                  </>
                ) : (
                  <p className="empty-copy">Select a saved upload to review its transcript.</p>
                )}
              </div>
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
