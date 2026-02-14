export default async (request, context) => {
  const url = new URL(request.url);

  // Método 1: Parámetros explícitos (petición inicial del HTML)
  let branch = url.searchParams.get('branch');
  let specPath = url.searchParams.get('path');

  // Método 2: Path relativo (referencias $ref de Swagger UI)
  if (!branch || !specPath) {
    // Extraer el path después de /github-spec-proxy/
    const pathname = url.pathname;
    const match = pathname.match(/\/github-spec-proxy\/(.+)/);

    if (match) {
      const relativePath = match[1]; // Ej: "v1/services/tenants/tenants-create.yml"

      // Determinar branch basado en el Referer header
      const referer = request.headers.get('referer') || '';
      branch = referer.includes('/snapshot/') ? 'develop' : 'main';

      // Construir path completo
      specPath = `tenants/rest/${relativePath}`;
    } else {
      // Sin parámetros ni path válido - usar defaults
      branch = 'main';
      specPath = 'tenants/rest/openapi-rest.yml';
    }
  }

  const owner = 'roldaiateam';
  const repo = 'apis-especifications';
  const githubToken = process.env.REPO_TOKEN;

  if (!githubToken) {
    return new Response(JSON.stringify({
      error: 'GitHub token not configured',
      message: 'REPO_TOKEN environment variable is missing'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  try {
    // GitHub API para obtener contenido raw
    const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${specPath}?ref=${branch}`;

    const response = await fetch(apiUrl, {
      headers: {
        'Authorization': `token ${githubToken}`,
        'Accept': 'application/vnd.github.v3.raw', // Obtiene contenido raw directamente
        'User-Agent': 'Netlify-Proxy'
      }
    });

    if (!response.ok) {
      const errorText = await response.text();
      return new Response(JSON.stringify({
        error: `GitHub API error: ${response.status}`,
        details: errorText,
        requested: { branch, specPath }
      }), {
        status: response.status,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const content = await response.text();

    return new Response(content, {
      status: 200,
      headers: {
        'Content-Type': 'application/yaml',
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'public, max-age=300' // Cache 5 minutos
      }
    });
  } catch (error) {
    return new Response(JSON.stringify({
      error: error.message,
      stack: error.stack
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
