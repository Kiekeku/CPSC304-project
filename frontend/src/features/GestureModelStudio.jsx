import { useEffect, useMemo, useState } from 'react';
import SectionCard from '../components/SectionCard';
import {
  addGestureLabel,
  createDataset,
  getDataset,
  listDatasets,
  trainDataset,
  uploadGestureVideo
} from '../api/mlApi';

function totalSamples(labelDetails) {
  return labelDetails.reduce((sum, detail) => sum + (detail.sample_count ?? 0), 0);
}

function formatAccuracy(accuracy) {
  return accuracy || accuracy === 0 ? `${accuracy}%` : 'Not scored yet';
}

function buildStorageLabel(datasetId, label) {
  return `backend/gesture_data/${datasetId}/${label}.json`;
}

export default function GestureModelStudio() {
  const [datasets, setDatasets] = useState([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState('');
  const [datasetDetail, setDatasetDetail] = useState(null);
  const [createName, setCreateName] = useState('');
  const [newGestureLabel, setNewGestureLabel] = useState('');
  const [selectedGesture, setSelectedGesture] = useState('');
  const [gestureVideo, setGestureVideo] = useState(null);
  const [loadingList, setLoadingList] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [addingGesture, setAddingGesture] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [training, setTraining] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const labelDetails = datasetDetail?.label_details ?? [];
  const sampleTotal = useMemo(() => totalSamples(labelDetails), [labelDetails]);
  const selectedGestureDetail =
    labelDetails.find((detail) => detail.label === selectedGesture) ?? labelDetails[0] ?? null;

  const loadDatasets = async (preferredId = '') => {
    setLoadingList(true);
    const result = await listDatasets();
    setLoadingList(false);

    if (!result.ok) {
      setErrorMessage(result.body?.detail || 'Unable to load trained models.');
      return;
    }

    const nextDatasets = result.body?.datasets ?? [];
    setDatasets(nextDatasets);

    if (preferredId) {
      setSelectedDatasetId(String(preferredId));
      return;
    }

    if (!nextDatasets.length) {
      setSelectedDatasetId('');
      setDatasetDetail(null);
      return;
    }

    const currentExists = nextDatasets.some(
      (dataset) => String(dataset.dataset_id) === String(selectedDatasetId)
    );

    if (!currentExists) {
      setSelectedDatasetId(String(nextDatasets[0].dataset_id));
    }
  };

  useEffect(() => {
    loadDatasets().catch((error) => {
      setLoadingList(false);
      setErrorMessage(error.message || 'Unable to load trained models.');
    });
  }, []);

  useEffect(() => {
    if (!selectedDatasetId) {
      setDatasetDetail(null);
      return;
    }

    let isMounted = true;

    async function loadDetail() {
      setDetailLoading(true);
      const result = await getDataset(selectedDatasetId);

      if (!isMounted) {
        return;
      }

      setDetailLoading(false);

      if (!result.ok) {
        setErrorMessage(result.body?.detail || 'Unable to load this model.');
        return;
      }

      const nextDetail = result.body;
      setDatasetDetail(nextDetail);
      setSelectedGesture((current) => {
        if (nextDetail.label_details?.some((detail) => detail.label === current)) {
          return current;
        }
        return nextDetail.label_details?.[0]?.label ?? '';
      });
    }

    loadDetail().catch((error) => {
      if (isMounted) {
        setDetailLoading(false);
        setErrorMessage(error.message || 'Unable to load this model.');
      }
    });

    return () => {
      isMounted = false;
    };
  }, [selectedDatasetId]);

  const clearBanners = () => {
    setErrorMessage('');
    setSuccessMessage('');
  };

  const refreshDetail = async (datasetId) => {
    const result = await getDataset(datasetId);
    if (!result.ok) {
      setErrorMessage(result.body?.detail || 'Unable to refresh this model.');
      return;
    }
    setDatasetDetail(result.body);
    setSelectedGesture((current) => {
      if (result.body.label_details?.some((detail) => detail.label === current)) {
        return current;
      }
      return result.body.label_details?.[0]?.label ?? '';
    });
  };

  const handleCreateDataset = async (event) => {
    event.preventDefault();

    if (!createName.trim()) {
      setErrorMessage('Enter a model name before creating a dataset.');
      return;
    }

    clearBanners();
    setCreating(true);
    const result = await createDataset(createName.trim());
    setCreating(false);

    if (!result.ok) {
      setErrorMessage(result.body?.detail || 'Unable to create the trained model record.');
      return;
    }

    setCreateName('');
    setSuccessMessage(`Created model ${result.body.name} with dataset ID ${result.body.dataset_id}.`);
    await loadDatasets(result.body.dataset_id);
  };

  const handleAddGesture = async (event) => {
    event.preventDefault();

    if (!selectedDatasetId) {
      setErrorMessage('Create or select a model first.');
      return;
    }

    if (!newGestureLabel.trim()) {
      setErrorMessage('Enter a gesture name before adding it.');
      return;
    }

    clearBanners();
    setAddingGesture(true);
    const result = await addGestureLabel(selectedDatasetId, newGestureLabel.trim());
    setAddingGesture(false);

    if (!result.ok) {
      setErrorMessage(result.body?.detail || 'Unable to register the gesture label.');
      return;
    }

    setNewGestureLabel('');
    setSelectedGesture(result.body.label);
    setSuccessMessage(`Added "${result.body.label}" to calibrated gesture storage.`);
    await refreshDetail(selectedDatasetId);
  };

  const handleUpload = async (event) => {
    event.preventDefault();

    if (!selectedDatasetId) {
      setErrorMessage('Create or select a model first.');
      return;
    }

    if (!selectedGesture) {
      setErrorMessage('Add or select a gesture label before uploading a video.');
      return;
    }

    if (!gestureVideo) {
      setErrorMessage('Choose a video file to extract hand mappings from.');
      return;
    }

    clearBanners();
    setUploading(true);
    const result = await uploadGestureVideo(selectedDatasetId, selectedGesture, gestureVideo);
    setUploading(false);

    if (!result.ok) {
      setErrorMessage(result.body?.detail || 'Unable to extract landmarks from that clip.');
      return;
    }

    setGestureVideo(null);
    setSuccessMessage(
      result.body?.message ||
        `Stored samples for "${selectedGesture}" in gesture_data/${selectedDatasetId}.`
    );
    await refreshDetail(selectedDatasetId);
  };

  const handleTrain = async () => {
    if (!selectedDatasetId) {
      setErrorMessage('Create or select a model first.');
      return;
    }

    clearBanners();
    setTraining(true);
    const result = await trainDataset(selectedDatasetId);
    setTraining(false);

    if (!result.ok) {
      setErrorMessage(result.body?.detail || 'Unable to train the model.');
      return;
    }

    setSuccessMessage(
      `${result.body.message} ${result.body.sample_count} samples across ${result.body.labels.length} gestures.`
    );
    await loadDatasets(selectedDatasetId);
    await refreshDetail(selectedDatasetId);
  };

  return (
    <SectionCard
      title="Gesture Model Studio"
      description="Build calibrated gesture datasets, store large handmark payloads as JSON files, and sync trained-model metadata back into Oracle."
    >
      <div className="gesture-studio">
        <div className="gesture-studio-hero">
          <div>
            <span className="eyebrow">Storage split</span>
            <h3>Database rows for metadata. JSON files for full landmark payloads.</h3>
            <p>
              Gesture names live in calibrated definition tables, model records stay in trained-model
              tables, and bulky vectors are written to <code>backend/gesture_data/&lt;datasetId&gt;/</code>.
            </p>
          </div>
          <div className="gesture-studio-pills">
            <span>Oracle metadata</span>
            <span>gesture_data JSON</span>
            <span>model.pkl artifact</span>
          </div>
        </div>

        <div className="gesture-studio-grid">
          <form className="gesture-panel" onSubmit={handleCreateDataset}>
            <span className="eyebrow">Step 1</span>
            <h3>Create a model record</h3>
            <label htmlFor="dataset-name">Model name</label>
            <input
              id="dataset-name"
              value={createName}
              onChange={(event) => setCreateName(event.target.value)}
              placeholder="Example: Campus Greetings KNN"
            />
            <button type="submit" disabled={creating}>
              {creating ? 'Creating model...' : 'Create model'}
            </button>
          </form>

          <div className="gesture-panel gesture-panel-accent">
            <span className="eyebrow">Step 2</span>
            <h3>Select a dataset</h3>
            <label htmlFor="dataset-select">Active trained model</label>
            <select
              id="dataset-select"
              value={selectedDatasetId}
              onChange={(event) => {
                clearBanners();
                setSelectedDatasetId(event.target.value);
              }}
            >
              {!datasets.length ? <option value="">No trained models yet</option> : null}
              {datasets.map((dataset) => (
                <option key={dataset.dataset_id} value={dataset.dataset_id}>
                  #{dataset.dataset_id} {dataset.name}
                </option>
              ))}
            </select>
            <p className="supporting-text">
              {loadingList
                ? 'Loading trained-model records...'
                : 'Choose the model you want to add gestures to or retrain.'}
            </p>
          </div>
        </div>

        {successMessage ? <div className="status-banner status-success">{successMessage}</div> : null}
        {errorMessage ? <div className="status-banner status-error">{errorMessage}</div> : null}

        {datasetDetail ? (
          <>
            <div className="gesture-metrics">
              <div className="gesture-metric-card">
                <span className="eyebrow">Model</span>
                <strong>{datasetDetail.name}</strong>
                <small>Dataset ID {datasetDetail.dataset_id}</small>
              </div>
              <div className="gesture-metric-card">
                <span className="eyebrow">Coverage</span>
                <strong>{labelDetails.length} gestures</strong>
                <small>{sampleTotal} extracted samples</small>
              </div>
              <div className="gesture-metric-card">
                <span className="eyebrow">Training</span>
                <strong>{formatAccuracy(datasetDetail.accuracy)}</strong>
                <small>{datasetDetail.trained ? `K = ${datasetDetail.k}` : 'Awaiting model fit'}</small>
              </div>
              <div className="gesture-metric-card">
                <span className="eyebrow">Artifacts</span>
                <strong>{datasetDetail.trained ? 'Ready for inference' : 'JSON only'}</strong>
                <small>{`backend/gesture_data/${datasetDetail.dataset_id}/model.pkl`}</small>
              </div>
            </div>

            <div className="gesture-workbench">
              <form className="gesture-panel" onSubmit={handleAddGesture}>
                <span className="eyebrow">Step 3</span>
                <h3>Register a gesture name</h3>
                <label htmlFor="gesture-label">Gesture label</label>
                <input
                  id="gesture-label"
                  value={newGestureLabel}
                  onChange={(event) => setNewGestureLabel(event.target.value)}
                  placeholder="Example: thank_you"
                />
                <p className="supporting-text">
                  This creates the calibrated gesture row and links it to the selected trained model.
                </p>
                <button type="submit" disabled={addingGesture}>
                  {addingGesture ? 'Saving gesture...' : 'Add gesture'}
                </button>
              </form>

              <form className="gesture-panel" onSubmit={handleUpload}>
                <span className="eyebrow">Step 4</span>
                <h3>Feed the gesture store</h3>
                <label htmlFor="gesture-select">Gesture target</label>
                <select
                  id="gesture-select"
                  value={selectedGesture}
                  onChange={(event) => setSelectedGesture(event.target.value)}
                >
                  {!labelDetails.length ? <option value="">No gesture labels yet</option> : null}
                  {labelDetails.map((detail) => (
                    <option key={detail.def_id} value={detail.label}>
                      {detail.label}
                    </option>
                  ))}
                </select>

                <label htmlFor="gesture-video">Training clip</label>
                <input
                  id="gesture-video"
                  type="file"
                  accept="video/*"
                  onChange={(event) => setGestureVideo(event.target.files?.[0] ?? null)}
                />
                <p className="supporting-text">
                  MediaPipe landmarks from each valid hand frame are appended to the gesture JSON file.
                </p>
                <button type="submit" disabled={uploading}>
                  {uploading ? 'Extracting landmarks...' : 'Ingest video'}
                </button>
              </form>

              <div className="gesture-panel gesture-panel-dark">
                <span className="eyebrow">Step 5</span>
                <h3>Train and publish metadata</h3>
                <p>
                  Training reads all JSON vectors in this dataset folder, fits the classifier, writes
                  `model.pkl`, and updates the trained-model table with accuracy, K, and handmark links.
                </p>
                <button type="button" onClick={handleTrain} disabled={training || detailLoading}>
                  {training ? 'Training model...' : 'Train dataset'}
                </button>
              </div>
            </div>

            <div className="gesture-storage-board">
              <div className="gesture-panel gesture-storage-panel">
                <span className="eyebrow">Gesture Storage</span>
                <h3>Per-label JSON files</h3>
                {detailLoading ? <p>Refreshing dataset details...</p> : null}
                {!labelDetails.length ? (
                  <p className="supporting-text">
                    Add a gesture label to start generating files inside `backend/gesture_data/`.
                  </p>
                ) : (
                  <div className="gesture-storage-list">
                    {labelDetails.map((detail) => (
                      <article
                        key={detail.def_id}
                        className={`gesture-storage-item${
                          detail.label === selectedGestureDetail?.label ? ' gesture-storage-item-active' : ''
                        }`}
                      >
                        <div>
                          <strong>{detail.label}</strong>
                          <p>{buildStorageLabel(datasetDetail.dataset_id, detail.label)}</p>
                        </div>
                        <div className="gesture-storage-badges">
                          <span>{detail.sample_count} samples</span>
                          <span>def_id {detail.def_id}</span>
                        </div>
                      </article>
                    ))}
                  </div>
                )}
              </div>

              <div className="gesture-panel gesture-storage-panel">
                <span className="eyebrow">Selected Target</span>
                <h3>Current ingestion path</h3>
                {selectedGestureDetail ? (
                  <>
                    <div className="artifact-path">{buildStorageLabel(datasetDetail.dataset_id, selectedGestureDetail.label)}</div>
                    <div className="gesture-target-facts">
                      <div>
                        <span className="eyebrow">Gesture</span>
                        <strong>{selectedGestureDetail.label}</strong>
                      </div>
                      <div>
                        <span className="eyebrow">Samples stored</span>
                        <strong>{selectedGestureDetail.sample_count}</strong>
                      </div>
                      <div>
                        <span className="eyebrow">Database link</span>
                        <strong>def_id {selectedGestureDetail.def_id}</strong>
                      </div>
                    </div>
                  </>
                ) : (
                  <p className="supporting-text">
                    Select or create a gesture label to see where its training data will be stored.
                  </p>
                )}
              </div>
            </div>
          </>
        ) : (
          <div className="gesture-empty-state">
            <h3>Start a calibrated gesture model</h3>
            <p>
              Create a dataset first. Each one becomes a trained-model record backed by a dedicated
              <code>gesture_data/&lt;datasetId&gt;/</code> folder for large JSON payloads.
            </p>
          </div>
        )}
      </div>
    </SectionCard>
  );
}
