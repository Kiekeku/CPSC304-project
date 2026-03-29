import DemotableWorkspace from './features/DemotableWorkspace';
import MlWorkspace from './features/MlWorkspace';

export default function App() {
  return (
    <main className="container">
      <h1>Database + Video Analysis Studio</h1>
      <p className="intro-text">
        Manage Oracle tables and run the sign-language video pipeline directly from the main
        interface.
      </p>

      <DemotableWorkspace />
      <MlWorkspace />
    </main>
  );
}
