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
#demotable-query-preview {
  margin: 16px;
  padding: 16px;
  border: 1px solid #d8dee9;
  border-radius: 8px;
  background: #f8fafc;
  font-family: sans-serif;
}
#demotable-query-preview button {
  margin-top: 8px;
  padding: 8px 12px;
  border: 0;
  border-radius: 6px;
  background: #2563eb;
  color: #fff;
  cursor: pointer;
}
#demotable-query-preview button:disabled {
  opacity: 0.6;
  cursor: wait;
}
#demotable-query-output {
  margin-top: 16px;
  display: grid;
  gap: 12px;
}
.demotable-query-card {
  padding: 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #fff;
}
.demotable-query-card pre {
  overflow-x: auto;
  white-space: pre-wrap;
  background: #0f172a;
  color: #e2e8f0;
  padding: 10px;
  border-radius: 6px;
}
.demotable-query-card table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
}
.demotable-query-card th,
.demotable-query-card td {
  border: 1px solid #cbd5e1;
  padding: 6px 8px;
  text-align: left;
  vertical-align: top;
}
.demotable-status-error { color: #b91c1c; }
.demotable-status-success { color: #166534; }
.demotable-status-skipped { color: #92400e; }
</style>
<script>
window.addEventListener('load', function () {
  const container = document.createElement('section');
  container.id = 'demotable-query-preview';
  container.innerHTML = `
    <h2>Demotable Query Preview</h2>
    <p>Runs the statements from <code>backend/sql/demotable_queries.sql</code> with preview bind values and rolls back any changes after execution.</p>
    <button id="run-demotable-queries-button" type="button">Run demotable queries</button>
    <div id="demotable-query-output"></div>
  `;
  document.body.prepend(container);

  const button = document.getElementById('run-demotable-queries-button');
  const output = document.getElementById('demotable-query-output');

  function escapeHtml(value) {
    return String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;');
  }

  function formatResult(result) {
    const statusClass = `demotable-status-${result.status}`;
    const binds = result.binds && Object.keys(result.binds).length
      ? `<div><strong>Binds:</strong> <code>${escapeHtml(JSON.stringify(result.binds))}</code></div>`
      : '';

    const dataTable = Array.isArray(result.columns) && result.columns.length
      ? `
        <table>
          <thead>
            <tr>${result.columns.map((column) => `<th>${escapeHtml(column)}</th>`).join('')}</tr>
          </thead>
          <tbody>
            ${(result.rows || []).map((row) => `<tr>${row.map((cell) => `<td>${escapeHtml(cell ?? '')}</td>`).join('')}</tr>`).join('')}
          </tbody>
        </table>
      `
      : '';

    const fallback = result.message
      ? `<div>${escapeHtml(result.message)}</div>`
      : `<div>Rows affected: ${escapeHtml(result.rowCount ?? 0)}</div>`;

    return `
      <article class="demotable-query-card">
        <div><strong>Statement ${escapeHtml(result.index)}</strong> <span class="${statusClass}">(${escapeHtml(result.status)})</span></div>
        <div><strong>Type:</strong> ${escapeHtml(result.type || 'UNKNOWN')}</div>
        ${binds}
        <pre>${escapeHtml(result.statement)}</pre>
        ${dataTable || fallback}
      </article>
    `;
  }

  button.addEventListener('click', async function () {
    button.disabled = true;
    output.innerHTML = '<div>Running queries...</div>';
    try {
      const response = await fetch('/run-demotable-queries', { method: 'POST' });
      const payload = await response.json();
      if (!response.ok || !payload.success) {
        throw new Error(payload.message || 'Failed to run demotable queries.');
      }
      output.innerHTML = payload.results.map(formatResult).join('');
    } catch (error) {
      output.innerHTML = `<div class="demotable-status-error">${escapeHtml(error.message || 'Failed to run demotable queries.')}</div>`;
    } finally {
      button.disabled = false;
    }
  });
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
