import { requestJson, requestText } from './http';

export async function fetchDbConnectionStatus() {
  return requestText('/check-db-connection');
}

export async function fetchTables() {
  return requestJson('/tables');
}

export async function fetchTableMetadata(tableName) {
  return requestJson(`/table-metadata/${encodeURIComponent(tableName)}`);
}

export async function fetchTableRows(tableName) {
  return requestJson(`/table-rows/${encodeURIComponent(tableName)}`);
}

export async function initiateDemotable() {
  return requestJson('/initiate-demotable', { method: 'POST' });
}

export async function insertTableRow(tableName, values) {
  return requestJson('/table-insert', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tableName, values })
  });
}

export async function updateTableRow(tableName, keys, values) {
  return requestJson('/table-update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tableName, keys, values })
  });
}

export async function deleteTableRow(tableName, keys) {
  return requestJson('/table-delete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tableName, keys })
  });
}
