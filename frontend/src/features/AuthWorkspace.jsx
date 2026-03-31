import { useState } from 'react';
import { login, register } from '../api/authApi';

export default function AuthWorkspace({ onLogin }) {
  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  async function handleSubmit() {
    setError('');
    const result = mode === 'login'
      ? await login(email, password)
      : await register(email, name, password);

    if (result.ok && result.body.success) {
      onLogin({ email, password });  // pass credentials -> App
    } else {
      setError(result.body?.message || 'Something went wrong');
    }
  }

  return (
    <div>
      <h2>{mode === 'login' ? 'Login' : 'Register'}</h2>
      {mode === 'register' && (
        <input placeholder="Name" value={name} onChange={e => setName(e.target.value)} />
      )}
      <input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
      <input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
      <button onClick={handleSubmit}>{mode === 'login' ? 'Login' : 'Register'}</button>
      <button onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
        Switch to {mode === 'login' ? 'Register' : 'Login'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}