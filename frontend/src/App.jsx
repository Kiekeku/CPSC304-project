import { useState } from 'react'; 
import AuthWorkspace from './features/AuthWorkspace'; 
import DemotableWorkspace from './features/DemotableWorkspace';
import GestureModelStudio from './features/GestureModelStudio';
import MlWorkspace from './features/MlWorkspace';
import SignLanguageWorkspace from './features/SignLanguageWorkspace';

export default function App() {
  const [currentUser, setCurrentUser] = useState(null);  // add this

  if (!currentUser) {
    return (
      <main className="container">
        <AuthWorkspace onLogin={setCurrentUser} />
      </main>
    );
  }

  return (
    <main className="container">
      <h1>Database + Video Analysis Studio</h1>
      <p className="intro-text">
        Manage Oracle tables, curate calibrated gesture datasets, and run the sign-language video
        pipeline from one workspace.
      </p>
      <button onClick={() => setCurrentUser(null)}>Logout</button>  {/* add this */}

      <DemotableWorkspace />
      <GestureModelStudio />
      <MlWorkspace />
      <SignLanguageWorkspace />
    </main>
  );
}