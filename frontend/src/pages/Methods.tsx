import { Link } from "react-router-dom";
import Catalogue from "./Catalogue";
import { useAnalysisProducts } from "../lib/research";
import { repositoryFileUrl } from "../lib/repository";
import { Notice, PageHeading, Value } from "../ui";

// Pushed snapshot containing the approved v1.2 specification, CP-B ledger and cards.
const methodSourceRevision = "63a325d7f0446ccfbfeaee2516e94568a3f23772";

const glossary = [
  [
    "Valence",
    "A signed axis from unpleasant (−1) to pleasant (+1) in the constructed affect plane.",
  ],
  [
    "Arousal",
    "A signed axis from calm (−1) to activated (+1) in the constructed affect plane.",
  ],
  [
    "Physiology-derived",
    "A candidate valence–arousal position constructed from eligible forehead EEG and wrist ECG features under documented assumptions.",
  ],
  [
    "Self-reported",
    "A participant response; Experiment 1 comfort is separate from later valence–arousal ratings.",
  ],
  [
    "Fused",
    "A documented weighted combination of eligible physiology-derived and self-reported coordinates. Missing components remain explicit.",
  ],
  [
    "Neuro-Score",
    "Proximity of a model-predicted fused coordinate to a selected emotional target, displayed from 0 to 100. It is not a health, certainty or design-quality score.",
  ],
  [
    "Held-out room",
    "A room excluded from model fitting when testing transfer to unseen room attributes.",
  ],
];

function MethodsEvidence() {
  const state = useAnalysisProducts(["Methods"]);
  const product = state.products.find((item) => item.id === "Methods");
  const evidence = product?.methods_evidence;
  const ledgerUrl =
    evidence &&
    repositoryFileUrl(evidence.review.ledger_path, methodSourceRevision);
  const categories = [
    ...new Set(evidence?.settings.map((setting) => setting.category) || []),
  ];
  const settingSources = [
    ...new Set(evidence?.settings.map((setting) => setting.source) || []),
  ];

  return (
    <section className="methods-evidence" aria-label="Approved method evidence">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Approved v1.2 analysis</p>
          <h2>Settings and review decisions</h2>
        </div>
      </div>
      <p>
        These values come from the versioned Methods export. The sampling rate
        remains a conditional assumption, and QC thresholds are operational
        screens rather than clinical cutoffs. Review decisions can withhold a
        signal component while leaving other eligible components available.
      </p>
      {state.status === "loading" && !evidence && (
        <p role="status">Loading approved method evidence…</p>
      )}
      {state.status === "error" && (
        <Notice title="Method evidence unavailable" warning>
          <p>{state.message}</p>
        </Notice>
      )}
      {evidence && (
        <>
          <p className="small-text">
            Approved numerical settings:{" "}
            {settingSources.map((source, index) => {
              const url = repositoryFileUrl(source, methodSourceRevision);
              return (
                <span key={source}>
                  {index > 0 && ", "}
                  {url ? (
                    <a href={url} target="_blank" rel="noreferrer">
                      {source} ↗
                    </a>
                  ) : (
                    <code>{source}</code>
                  )}
                </span>
              );
            })}
            .
          </p>
          <div className="method-settings">
            {categories.map((category) => (
              <div key={category}>
                <h3>{category.replaceAll("_", " ")}</h3>
                <dl>
                  {evidence.settings
                    .filter((setting) => setting.category === category)
                    .map((setting) => (
                      <div key={`${setting.category}:${setting.label}`}>
                        <dt>{setting.label}</dt>
                        <dd>
                          <strong>
                            {String(setting.value).replaceAll("_", " ")}
                          </strong>
                          {setting.unit && ` ${setting.unit}`}
                        </dd>
                      </div>
                    ))}
                </dl>
              </div>
            ))}
          </div>
          <div className="methods-review">
            <h3>Delegated CP-B signal review</h3>
            <p>
              Decision:{" "}
              <strong>{evidence.review.verdict.replaceAll("_", " ")}</strong>.
              Reviewed on {evidence.review.reviewed_at_utc}. Reviewers:{" "}
              {evidence.review.reviewers.join(", ")}. The complete decision
              ledger is{" "}
              {ledgerUrl ? (
                <a href={ledgerUrl} target="_blank" rel="noreferrer">
                  {evidence.review.ledger_path} ↗
                </a>
              ) : (
                <code>{evidence.review.ledger_path}</code>
              )}
              .
            </p>
            <div className="method-counts">
              <dl>
                {Object.entries(evidence.review.decision_counts).map(
                  ([decision, count]) => (
                    <div key={decision}>
                      <dt>{decision.replaceAll("_", " ")} decisions</dt>
                      <dd>{count}</dd>
                    </div>
                  ),
                )}
              </dl>
              <dl>
                {Object.entries(
                  evidence.review.reviewed_eligibility_counts,
                ).map(([component, count]) => (
                  <div key={component}>
                    <dt>{component.replaceAll("_", " ")} eligible</dt>
                    <dd>{count}</dd>
                  </div>
                ))}
              </dl>
            </div>
            <p>
              <Link to="/explore">
                Inspect trial-level automated and reviewed QC ↗
              </Link>
            </p>
          </div>
          <div className="methods-sensitivity">
            <h3>Existing fusion-weight sensitivity</h3>
            <p>
              Exported experiment summaries show how the descriptive fused
              coordinates change across the prespecified physiology weight α.
              Trial counts are repeated observations; these values do not
              estimate a causal weight or select a new method.
            </p>
            <div className="table-wrap">
              <table className="data-table">
                <caption>
                  Computed fusion sensitivity from eligible source trials,
                  grouped by experiment and prespecified weight.
                </caption>
                <thead>
                  <tr>
                    <th scope="col">Experiment</th>
                    <th scope="col">Physiology weight α</th>
                    <th scope="col">Eligible trials</th>
                    <th scope="col">Mean valence</th>
                    <th scope="col">Mean arousal</th>
                  </tr>
                </thead>
                <tbody>
                  {evidence.sensitivity.map((row) => (
                    <tr key={`${row.experiment}:${row.alpha}`}>
                      <th scope="row">{row.experiment}</th>
                      <td>{row.alpha}</td>
                      <td>{row.n}</td>
                      <td>
                        <Value value={row.mean_valence} />
                      </td>
                      <td>
                        <Value value={row.mean_arousal} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <div className="method-references">
            <h3>Versioned sources and context</h3>
            <p>
              Methods version {product.provenance.method_version}; approved
              specification SHA-256{" "}
              <code>{product.provenance.approved_spec_sha256}</code>. The linked
              repository snapshot identifies the governing specification,
              decisions and data/model context for this generated result.
            </p>
            <dl>
              {evidence.references.map((reference) => {
                const url = repositoryFileUrl(
                  reference.path,
                  methodSourceRevision,
                );
                return (
                  <div key={reference.path}>
                    <dt>{reference.label}</dt>
                    <dd>
                      {url ? (
                        <a href={url} target="_blank" rel="noreferrer">
                          {reference.path} ↗
                        </a>
                      ) : (
                        <code>{reference.path}</code>
                      )}
                    </dd>
                  </div>
                );
              })}
            </dl>
          </div>
        </>
      )}
    </section>
  );
}

export default function Methods() {
  return (
    <>
      <PageHeading
        eyebrow="07 / Method and context"
        title="Methods & Research Context"
        intro="The atlas carries an evolving analysis of an earlier architectural thesis. This page distinguishes the source experiments, current reproducible methods and historical design demonstrations."
      />
      <section className="methods-columns">
        <div>
          <p className="eyebrow">Source study</p>
          <h2>What was recorded</h2>
          <p>
            Thirty rendered rooms, repeated participant exposures, approximate
            bilateral forehead EEG, wrist ECG and available ratings form the
            source record. Source protocol and metadata define what can be
            linked; they do not establish a measured neutral baseline,
            calibrated headset illuminance or verified hardware sample rate.
          </p>
          <p>
            Experiment 1 supplied comfort. Experiments 2 and 3 supplied
            valence–arousal ratings under different elicitation procedures.
            Their observations are separated before any combined view.
          </p>
        </div>
        <div>
          <p className="eyebrow">Current analysis</p>
          <h2>What is constructed</h2>
          <p>
            Quality checks determine which signal features can be used.
            Documented mappings propose physiology-derived coordinates; reports
            remain their own component. Fusion is a descriptive hypothesis,
            compared with both parts. Predictions are evaluated on held-out
            people and rooms against simple baselines.
          </p>
          <p>
            The public research charts are generated from versioned exports. An
            unavailable value carries its reason, and trial counts are
            distinguished from independent participants and rooms.
          </p>
        </div>
      </section>
      <MethodsEvidence />
      <section className="prototype-story">
        <div>
          <p className="eyebrow">Thesis demonstrations · historical context</p>
          <h2>From evidence to a designer's canvas</h2>
          <p>
            The thesis demonstrated a Grasshopper connection that sent Rhino
            room attributes to a backend and displayed predicted coordinates and
            a score in the canvas. A separate AI rendering demonstration used a
            Rhino camera and an attribute/prediction prompt. These are
            documented proof-of-concept workflows from the thesis, rather than
            live features of this atlas.
          </p>
          <p>
            The current <Link to="/studio">Design Studio</Link> uses a schematic
            room volume, a fitted experimental model when available and clearly
            labeled renders of studied rooms for comparison.
          </p>
        </div>
        <div
          className="method-diagram"
          role="img"
          aria-label="Room attributes flow through a model to a predicted fused position and user-target Neuro-Score; studied room imagery remains reference material"
        >
          <span>ROOM ATTRIBUTES</span>
          <i aria-hidden="true">↓</i>
          <span>EXPERIMENTAL MODEL</span>
          <i aria-hidden="true">↓</i>
          <span>FUSED POSITION</span>
          <i aria-hidden="true">↓</i>
          <span>TARGET PROXIMITY</span>
        </div>
      </section>
      <section className="glossary">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Reading guide</p>
            <h2>Terms used across the atlas</h2>
          </div>
          <Link to="/explore">Inspect records ↗</Link>
        </div>
        <dl>
          {glossary.map(([term, meaning]) => (
            <div key={term}>
              <dt>{term}</dt>
              <dd>{meaning}</dd>
            </div>
          ))}
        </dl>
      </section>
      <Catalogue ids={["Methods"]} title="Versioned method record" />
    </>
  );
}
