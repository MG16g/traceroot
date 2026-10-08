import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

type RCAReportProps = {
  report: string | null
  incidentId: string
}

function RCAReport({
  report,
  incidentId,
}: RCAReportProps) {
  return (
    <section className="reasoning-section rca-report-section">
      <div className="reasoning-section-header">
        <div>
          <p className="eyebrow">Incident Documentation</p>
          <h3>Final RCA Report</h3>
        </div>

        <span className="rca-report-id">
          {incidentId}
        </span>
      </div>

      {report ? (
        <article className="rca-report">
          <div className="rca-report-header">
            <div>
              <span className="rca-report-label">
                Root Cause Analysis
              </span>

              <h4>
                {incidentId} — Investigation Report
              </h4>
            </div>

            <span className="rca-generated-badge">
              Generated
            </span>
          </div>

          <div className="rca-report-content rca-markdown">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {report}
            </ReactMarkdown>
          </div>
        </article>
      ) : (
        <div className="root-cause-empty">
          No final RCA report was generated for this investigation.
        </div>
      )}
    </section>
  )
}

export default RCAReport