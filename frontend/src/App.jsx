import DemotableWorkspace from './features/DemotableWorkspace';
import MlWorkspace from './features/MlWorkspace';

export default function App() {
  return (
    <main className="container">
      <h1>Database Application</h1>
      <p className="intro-text">Demotable operations and ML prediction workspace.</p>

      <DemotableWorkspace />
      <MlWorkspace />
    </main>
  );
}
