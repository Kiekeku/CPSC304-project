import { requestJson, requestText } from './http';

export async function fetchDbConnectionStatus() {
  return requestText('/check-db-connection');
}

export async function fetchDemotable() {
  return requestJson('/demotable');
}

export async function initiateDemotable() {
  return requestJson('/initiate-demotable', { method: 'POST' });
}

export async function insertDemotable(id, name) {
  return requestJson('/insert-demotable', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id, name })
  });
}

export async function updateNameDemotable(oldName, newName) {
  return requestJson('/update-name-demotable', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ oldName, newName })
  });
}

export async function countDemotable() {
  return requestJson('/count-demotable');
}
