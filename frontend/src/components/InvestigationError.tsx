type InvestigationErrorProps = {
  message: string
  incidentId: string
  onRetry: () => void
}

function InvestigationError({
  message,
  incidentId,
  onRetry,
}: InvestigationErrorProps) {
  return (
    <div
      className="investigation-error"
      role="alert"
    >
      <div className="investigation-error-icon">
        !
      </div>

      <div className="investigation-error-content">
        <div className="investigation-error-heading">
          <strong>Investigation failed</strong>
          <code>{incidentId}</code>
        </div>

        <p>{message}</p>
      </div>

      <button
        type="button"
        className="retry-button"
        onClick={onRetry}
      >
        Retry
        <span aria-hidden="true">→</span>
      </button>
    </div>
  )
}

export default InvestigationError