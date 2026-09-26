import type {
  InvestigationRequest,
  InvestigationResponse,
} from '../types/investigation'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

if (!API_BASE_URL) {
  throw new Error(
    'VITE_API_BASE_URL is not configured. Check the frontend environment configuration.',
  )
}

async function parseResponse(
  response: Response,
): Promise<InvestigationResponse> {
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`

    try {
      const errorBody = await response.json()

      if (typeof errorBody?.detail === 'string') {
        message = errorBody.detail
      }
    } catch {
      // Response did not contain JSON error details.
    }

    throw new Error(message)
  }

  return response.json() as Promise<InvestigationResponse>
}

export async function startInvestigation(
  incidentId: string,
): Promise<InvestigationResponse> {
  const requestBody: InvestigationRequest = {
    incident_id: incidentId,
  }

  const response = await fetch(`${API_BASE_URL}/api/investigations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody),
  })

  return parseResponse(response)
}

export async function getInvestigation(
  incidentId: string,
): Promise<InvestigationResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/investigations/${encodeURIComponent(incidentId)}`,
    {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    },
  )

  return parseResponse(response)
}