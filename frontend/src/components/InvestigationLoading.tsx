type InvestigationLoadingProps = {
  incidentId: string
}

function InvestigationLoading({
  incidentId,
}: InvestigationLoadingProps) {
  return (
    <div
      className="investigation-loading"
      role="status"
      aria-live="polite"
    >
      <div className="loading-indicator">
        <span className="loading-spinner" />
      </div>

      <div className="loading-content">
        <div className="loading-heading">
          <strong>Investigation in progress</strong>

          <code>{incidentId}</code>
        </div>

        <p>
          TraceRoot is analyzing telemetry and evaluating
          root-cause candidates.
        </p>
      </div>
    </div>
  )
}

export default InvestigationLoading