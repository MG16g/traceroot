import { useState } from 'react'

import type {
  IncidentCreateRequest,
  IncidentSeverity,
} from '../types/incident'

type CreateIncidentFormProps = {
  isSubmitting: boolean
  error: string | null
  onSubmit: (
    payload: IncidentCreateRequest,
  ) => Promise<void>
  onCancel: () => void
}

function CreateIncidentForm({
  isSubmitting,
  error,
  onSubmit,
  onCancel,
}: CreateIncidentFormProps) {
  const [id, setId] = useState('')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [service, setService] = useState('')
  const [severity, setSeverity] =
    useState<IncidentSeverity>('medium')

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    const payload: IncidentCreateRequest = {
      id: id.trim(),
      title: title.trim(),
      description: description.trim(),
      service: service.trim(),
      severity,
      status: 'open',
    }

    await onSubmit(payload)
  }

  return (
    <section className="create-incident-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">
            Incident Ingestion
          </p>

          <h2>Create Incident</h2>

          <p className="section-meta">
            Register a production incident for investigation.
          </p>
        </div>
      </div>

      <form
        className="create-incident-form"
        onSubmit={handleSubmit}
      >
        <label>
          Incident ID
          <input
            type="text"
            value={id}
            placeholder="INC-005"
            minLength={3}
            maxLength={50}
            required
            disabled={isSubmitting}
            onChange={(event) =>
              setId(event.target.value)
            }
          />
        </label>

        <label>
          Title
          <input
            type="text"
            value={title}
            placeholder="Order processing failures"
            minLength={3}
            maxLength={200}
            required
            disabled={isSubmitting}
            onChange={(event) =>
              setTitle(event.target.value)
            }
          />
        </label>

        <label>
          Service
          <input
            type="text"
            value={service}
            placeholder="order-service"
            minLength={2}
            maxLength={100}
            required
            disabled={isSubmitting}
            onChange={(event) =>
              setService(event.target.value)
            }
          />
        </label>

        <label>
          Severity
          <select
            value={severity}
            disabled={isSubmitting}
            onChange={(event) =>
              setSeverity(
                event.target.value as IncidentSeverity,
              )
            }
          >
            <option value="low">Low</option>
            <option value="medium">
              Medium
            </option>
            <option value="high">High</option>
            <option value="critical">
              Critical
            </option>
          </select>
        </label>

        <label className="create-incident-description">
          Description
          <textarea
            value={description}
            placeholder="Describe the production impact..."
            minLength={3}
            required
            disabled={isSubmitting}
            onChange={(event) =>
              setDescription(event.target.value)
            }
          />
        </label>

        {error && (
          <div
            className="create-incident-error"
            role="alert"
          >
            {error}
          </div>
        )}

        <div className="create-incident-actions">
          <button
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting
              ? 'Creating...'
              : 'Create Incident'}
          </button>
        </div>
      </form>
    </section>
  )
}

export default CreateIncidentForm