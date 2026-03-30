import DemotableWorkspace from './features/DemotableWorkspace';
import GestureModelStudio from './features/GestureModelStudio';
import MlWorkspace from './features/MlWorkspace';

export default function App() {
  return (
    <main className="container">
      <h1>Database + Video Analysis Studio</h1>
      <p className="intro-text">
        Manage Oracle tables, curate calibrated gesture datasets, and run the sign-language video
        pipeline from one workspace.
      </p>

      <DemotableWorkspace />
      <GestureModelStudio />
      <MlWorkspace />
    </main>
  );
}
