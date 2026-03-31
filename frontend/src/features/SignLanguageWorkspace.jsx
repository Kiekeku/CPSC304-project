import { useEffect, useState } from 'react';
import { analyzeVideo } from '../api/signLanguageApi';
import { listDatasets } from '../api/mlApi';
import SectionCard from '../components/SectionCard';

export default function SignLanguageWorkspace() {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [resultMessage, setResultMessage] = useState(' ');
    const [transcript, setTranscript] = useState('');

    const [datasets, setDatasets] = useState([]);
    const [selectedModelId, setSelectedModelId] = useState('');
    const [loadingModels, setLoadingModels] = useState(true);

    useEffect(() => {
        async function loadModels() {
            setLoadingModels(true);
            const result = await listDatasets();
            setLoadingModels(false);
            if (result.ok) {
                const trained = (result.body?.datasets ?? []).filter(d => d.trained);
                setDatasets(trained);
                if (trained.length > 0) {
                    setSelectedModelId(String(trained[0].dataset_id));
                }
            }
        }
        loadModels();
    }, []);

    const handleAnalyze = async (event) => {
        event.preventDefault();

        if (!file) {
            setResultMessage('Please select a file.');
            return;
        }

        setLoading(true);
        setResultMessage('');
        setTranscript('');

        try {
            const result = await analyzeVideo(file, selectedModelId || null);

            if (result.ok) {
                const text = result.body?.transcript_text;
                if (text && text !== 'unknown') {
                    setTranscript(text);
                }
                setResultMessage(JSON.stringify(result.body, null, 2));
            } else {
                setResultMessage(`Error ${result.status} occurred: ${JSON.stringify(result.body, null, 2)}.`);
            }
        } catch (e) {
            setResultMessage(`Error ${e.message}.`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <SectionCard
            title="Sign Language Analyzer"
            description="Extracts hand landmarks from uploaded videos using MediaPipe and OpenCV, then runs them through your trained gesture model."
        >
            <form onSubmit={handleAnalyze}>
                {}
                <label htmlFor="model-select">
                    Gesture model to use:
                </label>
                {loadingModels ? (
                    <p>Loading trained models...</p>
                ) : datasets.length === 0 ? (
                    <p style={{ color: '#888' }}>
                        No trained models found. Go to Gesture Model Studio, train a model, then come back.
                        The video will still be analyzed — it just won't produce a transcript.
                    </p>
                ) : (
                    <select
                        id="model-select"
                        value={selectedModelId}
                        onChange={(e) => setSelectedModelId(e.target.value)}
                    >
                        <option value="">-- No model (analyze only) --</option>
                        {datasets.map(d => (
                            <option key={d.dataset_id} value={d.dataset_id}>
                                #{d.dataset_id} {d.name} ({d.accuracy}% accuracy)
                            </option>
                        ))}
                    </select>
                )}

                {}
                <label>
                    Video file:
                    <input
                        id="sl-video-input"
                        type="file"
                        accept="video/*"
                        onChange={(e) => setFile(e.target.files[0])}
                    />
                </label>

                <button type="submit" id="analyze-sl-btn" disabled={loading}>
                    {loading ? 'Analyzing...' : 'Analyze'}
                </button>
            </form>

            {}
            {transcript && (
                <div style={{ margin: '1rem 0', padding: '1rem', background: '#e8f5e9', borderRadius: '8px' }}>
                    <strong>Transcript:</strong>
                    <p style={{ fontSize: '1.2rem', marginTop: '0.5rem' }}>{transcript}</p>
                </div>
            )}

            {resultMessage && <pre className="ml-output">{resultMessage}</pre>}
        </SectionCard>
    );
}