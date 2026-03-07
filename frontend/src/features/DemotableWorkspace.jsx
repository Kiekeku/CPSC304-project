import { useEffect, useState } from 'react';
import SectionCard from '../components/SectionCard';
import {
  deleteTableRow,
  fetchDbConnectionStatus,
  fetchTableMetadata,
  fetchTableRows,
  fetchTables,
  initiateDemotable,
  insertTableRow,
  updateTableRow
} from '../api/demotableApi';

export default function DemotableWorkspace() {
  const [dbStatus, setDbStatus] = useState('');
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState('');
  const [metadata, setMetadata] = useState(null);
  const [rows, setRows] = useState([]);
  const [message, setMessage] = useState('');
  const [resetMsg, setResetMsg] = useState('');
  const [newRowValues, setNewRowValues] = useState({});
  const [editingRowIndex, setEditingRowIndex] = useState(-1);
  const [editingValues, setEditingValues] = useState({});

  const rowToObject = (row) => {
    if (!metadata) {
      return {};
    }
    return metadata.columns.reduce((acc, column, index) => {
      acc[column.name] = row[index];
      return acc;
    }, {});
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

  const loadTables = async () => {
    const result = await fetchTables();
    const tableNames = result.body?.tables ?? [];
    setTables(tableNames);
    if (!tableNames.length) {
      setSelectedTable('');
      setMetadata(null);
      setRows([]);
      return;
    }
    if (!selectedTable || !tableNames.includes(selectedTable)) {
      setSelectedTable(tableNames[0]);
    }
  };

  const loadSelectedTable = async (tableName) => {
    if (!tableName) {
      return;
    }

    const [metadataResult, rowsResult] = await Promise.all([
      fetchTableMetadata(tableName),
      fetchTableRows(tableName)
    ]);

    if (!metadataResult.body?.success) {
      setMetadata(null);
      setRows([]);
      setMessage(metadataResult.body?.message || `Unable to load ${tableName}`);
      return;
    }

    setMetadata(metadataResult.body.metadata);
    setRows(rowsResult.body?.data ?? []);
    setNewRowValues({});
    setEditingRowIndex(-1);
    setEditingValues({});
  };

  const refreshSelectedTable = async () => {
    if (!selectedTable) {
      return;
    }
    await loadSelectedTable(selectedTable);
  };

  const handleReset = async () => {
    const result = await initiateDemotable();
    if (result.body?.success) {
      setResetMsg('Schema and seed scripts executed successfully.');
      await loadTables();
      await refreshSelectedTable();
      setMessage('');
      return;
    }
    setResetMsg('Error initializing schema/seed scripts.');
  };

  const handleInsert = async (event) => {
    event.preventDefault();
    if (!selectedTable) {
      return;
    }

    const result = await insertTableRow(selectedTable, newRowValues);
    if (result.body?.success) {
      setMessage(result.body.message || 'Row inserted successfully.');
      setNewRowValues({});
      await refreshSelectedTable();
    } else {
      setMessage(result.body?.message || 'Insert failed.');
    }
  };

  const handleSaveEdit = async (rowIndex) => {
    if (!metadata || !selectedTable) {
      return;
    }
    const originalRow = rows[rowIndex];
    const original = rowToObject(originalRow);
    const keys = metadata.primaryKey.reduce((acc, keyColumn) => {
      acc[keyColumn] = original[keyColumn];
      return acc;
    }, {});

    const result = await updateTableRow(selectedTable, keys, editingValues);
    if (result.body?.success) {
      setMessage(result.body.message || 'Row updated successfully.');
      setEditingRowIndex(-1);
      setEditingValues({});
      await refreshSelectedTable();
    } else {
      setMessage(result.body?.message || 'Update failed.');
    }
  };

  const handleDelete = async (rowIndex) => {
    if (!metadata || !selectedTable) {
      return;
    }
    const row = rowToObject(rows[rowIndex]);
    const keys = metadata.primaryKey.reduce((acc, keyColumn) => {
      acc[keyColumn] = row[keyColumn];
      return acc;
    }, {});
    const result = await deleteTableRow(selectedTable, keys);
    if (result.body?.success) {
      setMessage(result.body.message || 'Row deleted successfully.');
      await refreshSelectedTable();
      return;
    }
    setMessage(result.body?.message || 'Delete failed.');
  };

  useEffect(() => {
    checkDbConnection();
    loadTables();
  }, []);

  useEffect(() => {
    if (selectedTable) {
      loadSelectedTable(selectedTable);
    }
  }, [selectedTable]);

  return (
    <>
      <SectionCard title="Database Connection Status">
        <span>{dbStatus}</span>{' '}
        {loadingStatus ? (
          <img className="loading-gif" src="/loading_100px.gif" alt="Loading..." />
        ) : null}
      </SectionCard>

      <SectionCard
        title="Initialize Tables"
        description="Run schema and seed scripts in backend/sql."
      >
        <button onClick={handleReset}>initialize</button>
        <div>{resetMsg}</div>
      </SectionCard>

      <SectionCard title="Browse Tables">
        <label htmlFor="table-select">Select table</label>
        <select
          id="table-select"
          value={selectedTable}
          onChange={(e) => setSelectedTable(e.target.value)}
        >
          {tables.map((tableName) => (
            <option key={tableName} value={tableName}>
              {tableName}
            </option>
          ))}
        </select>
        {!tables.length ? <p>No tables found. Run initialize first.</p> : null}
        {metadata ? (
          <p>
            Primary key: {metadata.primaryKey.length ? metadata.primaryKey.join(', ') : 'none'}
          </p>
        ) : null}
      </SectionCard>

      <SectionCard title="Table Data">
        <table>
          <thead>
            <tr>
              {metadata?.columns.map((column) => (
                <th key={column.name}>{column.name}</th>
              ))}
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr key={`${selectedTable}-${idx}`}>
                {metadata?.columns.map((column, colIdx) => (
                  <td key={column.name}>
                    {editingRowIndex === idx ? (
                      <input
                        value={editingValues[column.name] ?? ''}
                        onChange={(e) =>
                          setEditingValues((prev) => ({
                            ...prev,
                            [column.name]: e.target.value
                          }))
                        }
                      />
                    ) : (
                      String(row[colIdx] ?? '')
                    )}
                  </td>
                ))}
                <td className="actions-cell">
                  {editingRowIndex === idx ? (
                    <>
                      <button type="button" onClick={() => handleSaveEdit(idx)}>
                        save
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setEditingRowIndex(-1);
                          setEditingValues({});
                        }}
                      >
                        cancel
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        type="button"
                        onClick={() => {
                          setEditingRowIndex(idx);
                          setEditingValues(rowToObject(row));
                        }}
                        disabled={!metadata?.primaryKey?.length}
                      >
                        edit
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDelete(idx)}
                        disabled={!metadata?.primaryKey?.length}
                      >
                        delete
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {message ? <div>{message}</div> : null}
      </SectionCard>

      <SectionCard title="Insert Row">
        <form onSubmit={handleInsert}>
          {metadata?.columns.map((column) => (
            <div key={column.name}>
              <label>{column.name}</label>
              <input
                type="text"
                value={newRowValues[column.name] ?? ''}
                onChange={(e) =>
                  setNewRowValues((prev) => ({
                    ...prev,
                    [column.name]: e.target.value
                  }))
                }
                placeholder={`${column.dataType}${column.nullable ? ' (nullable)' : ' (required)'}`}
              />
            </div>
          ))}
          <button type="submit" disabled={!selectedTable}>
            insert
          </button>
        </form>
      </SectionCard>
    </>
  );
}
