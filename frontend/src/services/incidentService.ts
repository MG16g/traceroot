import type { Incident } from '../types/incident'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

if (!API_BASE_URL) {
  throw new Error(
    'VITE_API_BASE_URL is not configured. Check the frontend environment configuration.',
  )
}

export async function getIncidents(): Promise<Incident[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/incidents`,
    {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    },
  )

  if (!response.ok) {
    let message =
      `Unable to load incidents (${response.status}).`

    try {
      const errorBody = (await response.json()) as {
        detail?: string
      }

      if (typeof errorBody.detail === 'string') {
        message = errorBody.detail
      }
    } catch {
      // Response did not contain JSON error details.
    }

    throw new Error(message)
  }

  return response.json() as Promise<Incident[]>
}