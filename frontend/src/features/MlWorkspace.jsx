import { useState } from 'react';
import { predict } from '../api/mlApi';
import SectionCard from '../components/SectionCard';

export default function MlWorkspace() {
  const [featureText, setFeatureText] = useState('{"example_feature": 1}');
  const [metadataText, setMetadataText] = useState('{"source": "ui"}');
  const [resultMessage, setResultMessage] = useState('');

  const handlePredict = async (event) => {
    event.preventDefault();

    try {
      const features = JSON.parse(featureText || '{}');
      const metadata = JSON.parse(metadataText || '{}');
      const result = await predict(features, metadata);

      if (result.body?.success) {
        setResultMessage(JSON.stringify(result.body, null, 2));
      } else {
        setResultMessage('Prediction request failed.');
      }
    } catch {
      setResultMessage('Invalid JSON. Update features/metadata input and try again.');
    }
  };

  return (
    <SectionCard
      title="ML Prediction Workspace"
      description="Use this panel to send prediction requests to /ml/predict."
    >
      <form onSubmit={handlePredict}>
        Features JSON:
        <textarea value={featureText} onChange={(e) => setFeatureText(e.target.value)} rows={4} />
        Metadata JSON:
        <textarea value={metadataText} onChange={(e) => setMetadataText(e.target.value)} rows={3} />
        <button type="submit">predict</button>
      </form>
      <pre className="ml-output">{resultMessage}</pre>
    </SectionCard>
  );
}
