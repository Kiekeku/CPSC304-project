import { useEffect, useState } from 'react';
import SectionCard from '../components/SectionCard';
import {
  countDemotable,
  fetchDbConnectionStatus,
  fetchDemotable,
  initiateDemotable,
  insertDemotable,
  updateNameDemotable
} from '../api/demotableApi';

export default function DemotableWorkspace() {
  const [dbStatus, setDbStatus] = useState('');
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [rows, setRows] = useState([]);

  const [insertId, setInsertId] = useState('');
  const [insertName, setInsertName] = useState('');
  const [insertMsg, setInsertMsg] = useState('');

  const [oldName, setOldName] = useState('');
  const [newName, setNewName] = useState('');
  const [updateMsg, setUpdateMsg] = useState('');

  const [resetMsg, setResetMsg] = useState('');
  const [countMsg, setCountMsg] = useState('');

  const refreshTable = async () => {
    const result = await fetchDemotable();
    setRows(result.body?.data ?? []);
  };

  const checkDbConnection = async () => {
    try {
      const result = await fetchDbConnectionStatus();
      setDbStatus(result.text || 'unable to connect');
    } catch {
      setDbStatus('connection timed out');
    } finally {
      setLoadingStatus(false);
    }
  };

  const handleReset = async () => {
    const result = await initiateDemotable();
    if (result.body?.success) {
      setResetMsg('demotable initiated successfully!');
      refreshTable();
      return;
    }
    alert('Error initiating table!');
  };

  const handleInsert = async (event) => {
    event.preventDefault();

    const result = await insertDemotable(Number(insertId), insertName);
    if (result.body?.success) {
      setInsertMsg('Data inserted successfully!');
      setInsertId('');
      setInsertName('');
      refreshTable();
    } else {
      setInsertMsg('Error inserting data!');
    }
  };

  const handleUpdate = async (event) => {
    event.preventDefault();

    const result = await updateNameDemotable(oldName, newName);
    if (result.body?.success) {
      setUpdateMsg('Name updated successfully!');
      setOldName('');
      setNewName('');
      refreshTable();
    } else {
      setUpdateMsg('Error updating name!');
    }
  };

  const handleCount = async () => {
    const result = await countDemotable();
    if (result.body?.success) {
      setCountMsg(`The number of tuples in demotable: ${result.body.count}`);
      return;
    }
    alert('Error in count demotable!');
  };

  useEffect(() => {
    checkDbConnection();
    refreshTable();
  }, []);

  return (
    <>
      <SectionCard title="Database Connection Status">
        <span>{dbStatus}</span>{' '}
        {loadingStatus ? (
          <img className="loading-gif" src="/loading_100px.gif" alt="Loading..." />
        ) : null}
      </SectionCard>

      <SectionCard title="Show Demotable">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr key={`${row[0]}-${idx}`}>
                <td>{row[0]}</td>
                <td>{row[1]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </SectionCard>

      <SectionCard
        title="Reset Demotable"
        description="If this is your first run, click reset to initialize schema/data scripts."
      >
        <button onClick={handleReset}>reset</button>
        <div>{resetMsg}</div>
      </SectionCard>

      <SectionCard title="Insert Values into DemoTable">
        <form onSubmit={handleInsert}>
          ID:
          <input
            type="number"
            value={insertId}
            onChange={(e) => setInsertId(e.target.value)}
            placeholder="Enter ID"
            required
          />
          Name:
          <input
            type="text"
            value={insertName}
            onChange={(e) => setInsertName(e.target.value)}
            placeholder="Enter Name"
            maxLength={20}
          />
          <button type="submit">insert</button>
        </form>
        <div>{insertMsg}</div>
      </SectionCard>

      <SectionCard
        title="Update Name in DemoTable"
        description="Values are case-sensitive."
      >
        <form onSubmit={handleUpdate}>
          Old Name:
          <input
            type="text"
            value={oldName}
            onChange={(e) => setOldName(e.target.value)}
            placeholder="Enter Old Name"
            required
          />
          New Name:
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Enter New Name"
            maxLength={20}
          />
          <button type="submit">update</button>
        </form>
        <div>{updateMsg}</div>
      </SectionCard>

      <SectionCard title="Count the Tuples in DemoTable">
        <button onClick={handleCount}>count</button>
        <div>{countMsg}</div>
      </SectionCard>
    </>
  );
}
