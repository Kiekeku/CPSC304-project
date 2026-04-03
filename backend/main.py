import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse, HTMLResponse
from dotenv import load_dotenv

from db import close_pool, init_pool
from routers.demotable_router import router as demotable_router
from routers.ml_router import router as ml_router
from routers.translator_router import router as translator_router
from routers.auth_router import router as auth_router

load_dotenv()

app = FastAPI(title="CPSC304 Python Backend", docs_url=None)
FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_pool()


@app.on_event("shutdown")
def on_shutdown() -> None:
    close_pool()


app.include_router(demotable_router)
app.include_router(ml_router)
app.include_router(translator_router)
app.include_router(auth_router)


@app.get("/docs", include_in_schema=False)
def custom_docs() -> HTMLResponse:
    swagger = get_swagger_ui_html(openapi_url=app.openapi_url, title=f"{app.title} - Docs")
    html = swagger.body.decode("utf-8")
    injected = """
<style>
#docs-query-runner {
  margin: 16px;
  padding: 16px;
  border: 1px solid #d8dee9;
  border-radius: 12px;
  background: #f8fafc;
  font-family: sans-serif;
}
#docs-query-grid {
  margin-top: 16px;
  display: grid;
  gap: 16px;
}
.docs-query-card {
  padding: 14px;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  background: #fff;
}
.docs-query-card h3 {
  margin: 0 0 6px;
}
.docs-query-card p {
  margin: 0 0 12px;
}
.docs-query-form {
  display: grid;
  gap: 10px;
}
.docs-query-field {
  display: grid;
  gap: 4px;
}
.docs-query-field label {
  font-weight: 600;
  font-size: 14px;
}
.docs-query-field input,
.docs-query-field textarea {
  padding: 8px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font: inherit;
}
.docs-query-field textarea {
  min-height: 88px;
  resize: vertical;
}
.docs-query-help {
  font-size: 12px;
  color: #475569;
}
.docs-query-card button {
  padding: 8px 12px;
  border: 0;
  border-radius: 6px;
  background: #2563eb;
  color: #fff;
  cursor: pointer;
}
.docs-query-card button:disabled {
  opacity: 0.6;
  cursor: wait;
}
.docs-query-result {
  margin-top: 12px;
}
.docs-query-result pre {
  overflow-x: auto;
  white-space: pre-wrap;
  background: #0f172a;
  color: #e2e8f0;
  padding: 10px;
  border-radius: 6px;
}
.docs-query-result table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
}
.docs-query-result th,
.docs-query-result td {
  border: 1px solid #cbd5e1;
  padding: 6px 8px;
  text-align: left;
  vertical-align: top;
}
.docs-query-status-error { color: #b91c1c; }
.docs-query-status-success { color: #166534; }
</style>
<script>
window.addEventListener('load', function () {
  const container = document.createElement('section');
  container.id = 'docs-query-runner';
  container.innerHTML = `
    <h2>DB Query Runner</h2>
    <p>Run the 10 query helpers defined in <code>backend/db.py</code>. Write operations execute against the database immediately.</p>
    <div id="docs-query-grid"><div>Loading queries...</div></div>
  `;
  document.body.prepend(container);

  const grid = document.getElementById('docs-query-grid');

  function escapeHtml(value) {
    return String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;');
  }

  function escapeAttribute(value) {
    return escapeHtml(value).replaceAll('"', '&quot;');
  }

  function buildInputField(input) {
    const help = input.helpText
      ? `<div class="docs-query-help">${escapeHtml(input.helpText)}</div>`
      : '';
    const required = input.required ? 'required' : '';
    const placeholder = input.placeholder ? `placeholder="${escapeAttribute(input.placeholder)}"` : '';
    const control = input.type === 'json'
      ? `
        <textarea name="${escapeAttribute(input.name)}" data-input-type="${escapeAttribute(input.type)}" ${placeholder} ${required}></textarea>
      `
      : `
        <input name="${escapeAttribute(input.name)}" data-input-type="${escapeAttribute(input.type)}" type="${input.type === 'number' ? 'number' : 'text'}" ${placeholder} ${required} />
      `;

    return `
      <div class="docs-query-field">
        <label>${escapeHtml(input.label)}</label>
        ${control}
        ${help}
      </div>
    `;
  }

  function renderResult(result) {
    if (result.type === 'table') {
      const columns = Array.isArray(result.columns) && result.columns.length
        ? result.columns
        : (result.rows[0] || []).map((_, index) => `Column ${index + 1}`);
      const emptyColspan = Math.max(columns.length, 1);
      return `
        <div class="docs-query-status-success">Returned ${escapeHtml(result.rowCount ?? 0)} row(s).</div>
        <table>
          <thead>
            <tr>${columns.map((column) => `<th>${escapeHtml(column)}</th>`).join('')}</tr>
          </thead>
          <tbody>
            ${(result.rows || []).map((row) => `<tr>${row.map((cell) => `<td>${escapeHtml(cell ?? '')}</td>`).join('')}</tr>`).join('') || '<tr><td colspan="' + emptyColspan + '">No rows returned.</td></tr>'}
          </tbody>
        </table>
      `;
    }

    return `<div class="docs-query-status-success">${escapeHtml(result.message || 'Query completed.')}</div>`;
  }

  function renderQueryCard(query) {
    const inputs = query.inputs && query.inputs.length
      ? query.inputs.map(buildInputField).join('')
      : '<div class="docs-query-help">This query does not require any inputs.</div>';

    return `
      <article class="docs-query-card" data-query-id="${escapeHtml(query.id)}">
        <h3>${escapeHtml(query.title)}</h3>
        <p>${escapeHtml(query.description || '')}</p>
        <form class="docs-query-form">
          ${inputs}
          <div>
            <button type="submit">Run Query</button>
          </div>
        </form>
        <div class="docs-query-result"></div>
      </article>
    `;
  }

  function collectParams(form) {
    const params = {};
    for (const element of form.querySelectorAll('[name]')) {
      params[element.name] = element.value;
    }
    return params;
  }

  async function loadQueries() {
    try {
      const response = await fetch('/docs-queries');
      const payload = await response.json();
      if (!response.ok || !payload.success) {
        throw new Error(payload.message || 'Failed to load query definitions.');
      }

      grid.innerHTML = payload.queries.map(renderQueryCard).join('');

      for (const card of grid.querySelectorAll('.docs-query-card')) {
        const form = card.querySelector('.docs-query-form');
        const button = form.querySelector('button');
        const resultContainer = card.querySelector('.docs-query-result');
        const queryId = card.dataset.queryId;

        form.addEventListener('submit', async function (event) {
          event.preventDefault();
          button.disabled = true;
          resultContainer.innerHTML = '<div>Running query...</div>';

          try {
            const response = await fetch('/docs-run-query', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                queryId,
                params: collectParams(form),
              }),
            });
            const payload = await response.json();
            if (!response.ok || !payload.success) {
              throw new Error(payload.message || 'Query failed.');
            }
            resultContainer.innerHTML = renderResult(payload.result);
          } catch (error) {
            resultContainer.innerHTML = `<div class="docs-query-status-error">${escapeHtml(error.message || 'Query failed.')}</div>`;
          } finally {
            button.disabled = false;
          }
        });
      }
    } catch (error) {
      grid.innerHTML = `<div class="docs-query-status-error">${escapeHtml(error.message || 'Failed to load query definitions.')}</div>`;
    }
  }

  loadQueries();
});
</script>
"""
    return HTMLResponse(html.replace("</body>", injected + "\n</body>"))

@app.get("/", include_in_schema=False)
def serve_frontend_root():
    index_path = FRONTEND_DIST_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    raise HTTPException(
        status_code=404,
        detail="Frontend build not found. Run './scripts/build-frontend.sh' first.",
    )


@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend(full_path: str):
    if full_path in {"favicon.ico"}:
        file_path = FRONTEND_DIST_DIR / full_path
        if file_path.exists():
            return FileResponse(file_path)
        raise HTTPException(status_code=404, detail="File not found")

    requested_path = FRONTEND_DIST_DIR / full_path
    if requested_path.exists() and requested_path.is_file():
        return FileResponse(requested_path)

    index_path = FRONTEND_DIST_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)

    raise HTTPException(
        status_code=404,
        detail="Frontend build not found. Run './scripts/build-frontend.sh' first.",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
