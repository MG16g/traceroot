import type {
  InvestigationComparisonResponse,
  InvestigationHistoryItem,
  InvestigationRequest,
  InvestigationResponse,
  InvestigationStreamEvent,
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

export async function getInvestigationRun(
  investigationId: string,
): Promise<InvestigationResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/investigations/runs/${encodeURIComponent(
      investigationId,
    )}`,
    {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    },
  )

  return parseResponse(response)
}

async function parseHistoryResponse(
  response: Response,
): Promise<InvestigationHistoryItem[]> {
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

  return response.json() as Promise<InvestigationHistoryItem[]>
}

export async function getInvestigationHistory(
  incidentId: string,
): Promise<InvestigationHistoryItem[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/investigations/${encodeURIComponent(
      incidentId,
    )}/history`,
    {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    },
  )

  return parseHistoryResponse(response)
}

export async function getInvestigationComparison(
  baselineId: string,
  comparisonId: string,
): Promise<InvestigationComparisonResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/investigations/compare/${encodeURIComponent(
      baselineId,
    )}/${encodeURIComponent(comparisonId)}`,
    {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    },
  )

  if (!response.ok) {
    let message =
      `Comparison request failed with status ${response.status}`

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

  return response.json() as Promise<InvestigationComparisonResponse>
}

export function streamInvestigation(
  incidentId: string,
  onEvent: (event: InvestigationStreamEvent) => void,
  onError: (message: string) => void,
): EventSource {
  const eventSource = new EventSource(
    `${API_BASE_URL}/api/investigations/stream/${encodeURIComponent(
      incidentId,
    )}`,
  )

  const handleEvent = (rawEvent: MessageEvent) => {
    try {
      const event = JSON.parse(
        rawEvent.data,
      ) as InvestigationStreamEvent

      onEvent(event)
    } catch {
      onError('Received an invalid investigation event.')
      eventSource.close()
    }
  }

  eventSource.addEventListener(
    'started',
    handleEvent,
  )

  eventSource.addEventListener(
    'progress',
    handleEvent,
  )

  eventSource.addEventListener(
    'completed',
    handleEvent,
  )

  eventSource.addEventListener(
    'investigation_error',
    handleEvent,
  )

  eventSource.onerror = () => {
    if (eventSource.readyState === EventSource.CLOSED) {
      return
    }

    onError('Live investigation connection was interrupted.')
    eventSource.close()
  }

  return eventSource
}
