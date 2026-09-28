import type {
  InvestigationStreamEvent,
} from '../types/investigation'

type InvestigationTimelineProps = {
  incidentId: string
  events: InvestigationStreamEvent[]
}

function InvestigationTimeline({
  incidentId,
  events,
}: InvestigationTimelineProps) {
  return (
    <section className="live-investigation">
      <div className="live-investigation-header">
        <div>
          <p className="eyebrow">
            Live Agent Activity
          </p>

          <h3>Investigation Progress</h3>
        </div>

        <code>{incidentId}</code>
      </div>

      <ol className="live-event-list">
        {events.map((event, index) => (
          <li
            key={`${event.event}-${event.step}-${event.iteration}-${index}`}
            className={`live-event live-event-${event.event}`}
          >
            <div className="live-event-marker">
              <span />
            </div>

            <div className="live-event-content">
              <div className="live-event-title">
                <strong>
                    {event.message}
                </strong>

                {event.iteration != null &&
                  event.iteration > 0 && (
                    <span>
                      Iteration {event.iteration}
                    </span>
                  )}
              </div>

              {event.step && (
                <code>{event.step}</code>
              )}
            </div>
          </li>
        ))}
      </ol>
    </section>
  )
}

export default InvestigationTimeline