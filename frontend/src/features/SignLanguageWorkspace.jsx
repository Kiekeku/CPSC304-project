import { useState } from 'react';
import { analyzeVideo } from '../api/signLanguageApi';
import SectionCard from '../components/SectionCard';

export default function SignLanguageWorkspace() {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [resultMessage, setResultMessage] = useState(' ');

    const handleAnalyze = async (event)  => {
        event.preventDefault();

        if (!file) {
            setResultMessage('Please select a file.');
            return;
        }

        setLoading(true);
        setResultMessage('');

        try {
            const result = await analyzeVideo(file);

            if (result.ok) {
                setResultMessage(JSON.stringify(result.body, null, 2));
            } else {
                setResultMessage(`Error ${result.status} occurred: ${JSON.stringify(result.body, null, 2)}.`);
            }
        } catch(e) {
            setResultMessage(`Error ${e.message}.`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <SectionCard
            title="Sign Language Analyzer"
            description="Extracts hand landmarks from uploaded videos using MediaPipe and OpenCV"
            >
                <form onSubmit={handleAnalyze}>
                    <label>
                        Video file:
                        <input
                            id="video-input"
                            type="file"
                            accept="video/*"
                            onChange={(e) => setFile(e.target.files[0])}
                        />
                    </label>
                    <button type="submit" id="analyze-sl-btn" disabled={loading}>
                        {loading ? 'Analyzing...' : 'Analyze'}
                    </button>
                </form>
                {resultMessage && <pre className="ml-output">{resultMessage}</pre>}
            </SectionCard>
    );
}