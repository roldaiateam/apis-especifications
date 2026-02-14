export default async (request, context) => {
  const url = new URL(request.url);
  const branch = url.searchParams.get('branch') || 'main';
  const specPath = url.searchParams.get('path') || 'tenants/rest/openapi-rest.yml';

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
