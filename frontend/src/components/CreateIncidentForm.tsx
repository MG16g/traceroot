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

    const trimmedId = id.trim()
    const trimmedTitle = title.trim()
    const trimmedDescription = description.trim()
    const trimmedService = service.trim()

    const form = event.currentTarget

    const fields = [
      { value: trimmedId, element: form.elements.namedItem('id') },
      { value: trimmedTitle, element: form.elements.namedItem('title') },
      { value: trimmedService, element: form.elements.namedItem('service') },
      {
        value: trimmedDescription,
        element: form.elements.namedItem('description'),
      },
    ]

    for (const field of fields) {
      if (
        !field.value &&
        field.element instanceof HTMLInputElement
      ) {
        field.element.setCustomValidity(
          'This field cannot contain only spaces.',
        )
        field.element.reportValidity()
        return
      }

      if (
        !field.value &&
        field.element instanceof HTMLTextAreaElement
      ) {
        field.element.setCustomValidity(
          'This field cannot contain only spaces.',
        )
        field.element.reportValidity()
        return
      }
    }

    const payload: IncidentCreateRequest = {
      id: trimmedId,
      title: trimmedTitle,
      description: trimmedDescription,
      service: trimmedService,
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
            name="id"
            value={id}
            placeholder="INC-005"
            minLength={3}
            maxLength={50}
            required
            disabled={isSubmitting}
            onChange={(event) =>{
              event.currentTarget.setCustomValidity('')
              setId(event.target.value)
            }}
          />
        </label>

        <label>
          Title
          <input
            type="text"
            name="title"
            value={title}
            placeholder="Order processing failures"
            minLength={3}
            maxLength={200}
            required
            disabled={isSubmitting}
            onChange={(event) =>{
              event.currentTarget.setCustomValidity('')
              setTitle(event.target.value)
            }}
          />
        </label>

        <label>
          Service
          <input
            type="text"
            name="service"
            value={service}
            placeholder="order-service"
            minLength={2}
            maxLength={100}
            required
            disabled={isSubmitting}
            onChange={(event) =>{
              event.currentTarget.setCustomValidity('')
              setService(event.target.value)
            }}
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
            name="description"
            value={description}
            placeholder="Describe the production impact..."
            minLength={3}
            required
            disabled={isSubmitting}
            onChange={(event) =>{
              event.currentTarget.setCustomValidity('')
              setDescription(event.target.value)
            }}
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