import {
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  type FormEvent,
} from "react";
import { Link, useSearchParams } from "react-router-dom";
import manifest from "../../../data/renders/manifest.json";
import {
  getMeta,
  optimizeRoom,
  predictRoom,
  type AffectTarget,
  type MetaResponse,
  type OptimizeRequest,
  type OptimizeResponse,
  type PredictResponse,
  type RoomInput,
} from "../api/client";
import Massing from "../figures/Massing";
import TargetPlane from "../figures/TargetPlane";
import { useResearch, type Room } from "../lib/research";
import { Notice, PageHeading, Value, modelStatusLabel } from "../ui";

type NumericKey = Extract<
  keyof RoomInput,
  | "length"
  | "width"
  | "height"
  | "num_doors"
  | "door_area"
  | "num_windows"
  | "window_area"
  | "daylight_factor"
  | "illuminance"
  | "cct"
  | "walkable_floor_area"
>;
type Group = {
  title: string;
  fields: {
    key: NumericKey;
    label: string;
    unit: string;
    min: number;
    max?: number;
    integer?: boolean;
    required?: boolean;
  }[];
};
const groups: Group[] = [
  {
    title: "Geometry",
    fields: [
      {
        key: "length",
        label: "Length",
        unit: "m",
        min: 0.001,
        max: 100,
        required: true,
      },
      {
        key: "width",
        label: "Width",
        unit: "m",
        min: 0.001,
        max: 100,
        required: true,
      },
      {
        key: "height",
        label: "Height",
        unit: "m",
        min: 0.001,
        max: 30,
        required: true,
      },
      {
        key: "walkable_floor_area",
        label: "Walkable floor area",
        unit: "m²",
        min: 0,
      },
    ],
  },
  {
    title: "Openings",
    fields: [
      {
        key: "num_doors",
        label: "Door count",
        unit: "",
        min: 0,
        integer: true,
      },
      { key: "door_area", label: "Total door area", unit: "m²", min: 0 },
      {
        key: "num_windows",
        label: "Window count",
        unit: "",
        min: 0,
        integer: true,
      },
      { key: "window_area", label: "Total window area", unit: "m²", min: 0 },
    ],
  },
  {
    title: "Lighting",
    fields: [
      {
        key: "daylight_factor",
        label: "Daylight factor",
        unit: "%",
        min: 0,
        max: 100,
      },
      { key: "illuminance", label: "Illuminance", unit: "lux", min: 0 },
      { key: "cct", label: "Colour temperature", unit: "K", min: 0.001 },
    ],
  },
];
const fields = groups.flatMap((group) => group.fields);
const spaceTypes: NonNullable<RoomInput["space_type"]>[] = [
  "General",
  "Bedroom",
  "Living Room",
  "Workplace",
  "Classroom",
  "Cafeteria",
];
const emptyNumbers = Object.fromEntries(
  fields.map((field) => [field.key, ""]),
) as Record<NumericKey, string>;
type Bounds = { minimum: string; maximum: string };
const blankBounds = Object.fromEntries(
  fields.map((field) => [field.key, { minimum: "", maximum: "" }]),
) as Record<NumericKey, Bounds>;
const numberOrNull = (value: string) =>
  value.trim() === "" ? null : Number(value);
const preventWheelChange = (event: React.WheelEvent<HTMLInputElement>) =>
  event.currentTarget.blur();
const renderFor = (id: string | null) =>
  manifest.rooms.find((asset) => asset.id === id);
const supportLabel = (status: string) =>
  ({
    supported: "Within studied support",
    within_studied_support: "Within studied support",
    sparse: "Sparse studied support",
    outside_range: "Outside studied attribute ranges",
    unseen_category: "Unseen room category",
    unavailable: "Support unavailable",
  })[status as "supported"] || status.replaceAll("_", " ");

function presetNumbers(room: Room): Record<NumericKey, string> {
  return Object.fromEntries(
    fields.map((field) => [
      field.key,
      String(room.independent_attributes?.[field.key] ?? ""),
    ]),
  ) as Record<NumericKey, string>;
}

function completePreset(room: Room): boolean {
  return (
    room.experiment === 3 &&
    fields.every(
      (field) =>
        typeof room.independent_attributes?.[field.key] === "number" &&
        Number.isFinite(room.independent_attributes[field.key]),
    ) &&
    room.independent_attributes?.space_type != null &&
    room.independent_attributes?.day_or_night != null
  );
}

function verifyCandidates(
  response: OptimizeResponse,
  request: OptimizeRequest,
) {
  for (const candidate of response.candidates) {
    for (const field of request.locked_fields || []) {
      if (
        (candidate.room as Record<string, unknown>)[field] !==
        (request.base_room as Record<string, unknown>)[field]
      )
        throw new Error(
          `The returned candidate did not preserve locked ${field}.`,
        );
    }
    for (const [field, bounds] of Object.entries(
      request.allowed_ranges || {},
    )) {
      const value = (candidate.room as Record<string, unknown>)[field];
      if (
        typeof value !== "number" ||
        value < bounds.minimum - 1e-9 ||
        value > bounds.maximum + 1e-9
      )
        throw new Error(
          `The returned candidate is outside the allowed ${field} range.`,
        );
    }
  }
}

function CandidateParameters({
  candidate,
  index,
}: {
  candidate: OptimizeResponse["candidates"][number];
  index: number;
}) {
  return (
    <details className="candidate-parameters" open={index === 0}>
      <summary>
        Candidate {index + 1} · complete room parameters and fused position
      </summary>
      <div className="candidate-parameter-groups">
        {groups.map((group) => (
          <section key={group.title}>
            <h4>{group.title}</h4>
            <dl>
              {group.fields.map((field) => (
                <div key={field.key}>
                  <dt>{field.label}</dt>
                  <dd>
                    {String(candidate.room[field.key])}
                    {field.unit ? ` ${field.unit}` : ""}
                  </dd>
                </div>
              ))}
            </dl>
          </section>
        ))}
        <section>
          <h4>Context and fused output</h4>
          <dl>
            <div>
              <dt>Time of day</dt>
              <dd>{candidate.room.day_or_night}</dd>
            </div>
            <div>
              <dt>Space type</dt>
              <dd>{candidate.room.space_type}</dd>
            </div>
            <div>
              <dt>Fused valence</dt>
              <dd>
                <Value value={candidate.prediction.valence} />
              </dd>
            </div>
            <div>
              <dt>Fused arousal</dt>
              <dd>
                <Value value={candidate.prediction.arousal} />
              </dd>
            </div>
          </dl>
        </section>
      </div>
    </details>
  );
}

export default function Studio() {
  const research = useResearch();
  const [searchParams] = useSearchParams();
  const linkedRoom = searchParams.get("room");
  const [meta, setMeta] = useState<MetaResponse | null>(null);
  const [readiness, setReadiness] = useState<
    "checking" | "ready" | "unavailable"
  >("checking");
  const [numbers, setNumbers] = useState<Record<NumericKey, string>>({
    ...emptyNumbers,
  });
  const [bounds, setBounds] = useState<Record<NumericKey, Bounds>>({
    ...blankBounds,
  });
  const [locks, setLocks] = useState<NumericKey[]>([]);
  const [spaceType, setSpaceType] = useState<RoomInput["space_type"]>(null);
  const [dayNight, setDayNight] = useState<RoomInput["day_or_night"]>(null);
  const [target, setTarget] = useState<AffectTarget>({
    valence: 0,
    arousal: 0,
  });
  const [requestedScore, setRequestedScore] = useState("65");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [prediction, setPrediction] = useState<PredictResponse | null>(null);
  const [generation, setGeneration] = useState<OptimizeResponse | null>(null);
  const [selectedPreset, setSelectedPreset] = useState("");
  const requestRevision = useRef(0);
  const resultHeading = useRef<HTMLHeadingElement>(null);
  const loadedLinkedRoom = useRef<string | null>(null);

  useLayoutEffect(() => {
    requestRevision.current += 1;
    setPrediction(null);
    setGeneration(null);
    setError("");
  }, [numbers, bounds, locks, spaceType, dayNight, target, requestedScore]);

  function checkReadiness() {
    setReadiness("checking");
    getMeta()
      .then((value) => {
        setMeta(value);
        setReadiness(value.ready ? "ready" : "unavailable");
      })
      .catch(() => {
        setMeta(null);
        setReadiness("unavailable");
      });
  }
  useEffect(() => {
    checkReadiness();
  }, []);
  useEffect(() => {
    if (
      !linkedRoom ||
      research.status !== "ready" ||
      loadedLinkedRoom.current === linkedRoom
    )
      return;
    loadedLinkedRoom.current = linkedRoom;
    const found = research.data.rooms.find(
      (room) => room.id === linkedRoom && completePreset(room),
    );
    if (!found) return;
    setSelectedPreset(found.id);
    setNumbers(presetNumbers(found));
    setSpaceType(
      (found.independent_attributes?.space_type as RoomInput["space_type"]) ||
        null,
    );
    setDayNight(
      (found.independent_attributes
        ?.day_or_night as RoomInput["day_or_night"]) || null,
    );
  }, [linkedRoom, research]);
  useEffect(() => {
    if (!prediction && !generation && !error) return;
    resultHeading.current?.focus({ preventScroll: true });
    if (window.matchMedia("(max-width: 760px)").matches)
      resultHeading.current?.scrollIntoView({
        behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
          ? "auto"
          : "smooth",
        block: "start",
      });
  }, [prediction, generation, error]);

  function buildRoom(): RoomInput {
    const room = Object.fromEntries(
      fields.map((field) => [field.key, numberOrNull(numbers[field.key])]),
    ) as Record<NumericKey, number | null>;
    if (room.length == null || room.width == null || room.height == null)
      throw new Error("Enter room length, width and height.");
    const missing = fields
      .filter((field) => room[field.key] == null)
      .map((field) => field.label);
    if (!spaceType) missing.push("Space type");
    if (!dayNight) missing.push("Time of day");
    if (missing.length)
      throw new Error(
        `The current E3 model needs complete room inputs: ${missing.join(", ")}. Use a complete studied-room preset or enter these source attributes.`,
      );
    return {
      ...room,
      length: room.length,
      width: room.width,
      height: room.height,
      space_type: spaceType,
      day_or_night: dayNight,
    };
  }

  function buildRanges(): NonNullable<OptimizeRequest["allowed_ranges"]> {
    const ranges: NonNullable<OptimizeRequest["allowed_ranges"]> = {};
    for (const field of fields) {
      const value = bounds[field.key];
      if (!value.minimum && !value.maximum) continue;
      if (value.minimum === "" || value.maximum === "")
        throw new Error(`Enter both bounds for ${field.label}.`);
      const minimum = Number(value.minimum),
        maximum = Number(value.maximum);
      if (
        !Number.isFinite(minimum) ||
        !Number.isFinite(maximum) ||
        minimum > maximum
      )
        throw new Error(`Check the allowed ${field.label} range.`);
      ranges[field.key] = { minimum, maximum };
    }
    return ranges;
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (readiness !== "ready") {
      setError(
        "The prediction service is unavailable. Check readiness before submitting.",
      );
      return;
    }
    const action =
      (event.nativeEvent as SubmitEvent).submitter?.getAttribute("value") ||
      "predict";
    const revision = requestRevision.current;
    setBusy(true);
    setError("");
    setPrediction(null);
    setGeneration(null);
    try {
      const room = buildRoom();
      if (action === "generate") {
        const score = Number(requestedScore);
        if (
          requestedScore.trim() === "" ||
          !Number.isFinite(score) ||
          score < 0 ||
          score > 100
        )
          throw new Error("Choose a requested Neuro-Score between 0 and 100.");
        const request: OptimizeRequest = {
          target,
          requested_score: score,
          base_room: room,
          locked_fields: locks,
          allowed_ranges: buildRanges(),
          space_type: spaceType,
          day_or_night: dayNight,
          budget: 500,
          n_candidates: 5,
          seed: 2718,
        };
        const response = await optimizeRoom(request);
        verifyCandidates(response, request);
        if (revision === requestRevision.current) setGeneration(response);
      } else {
        const response = await predictRoom(room, target);
        if (revision === requestRevision.current) setPrediction(response);
      }
    } catch (caught) {
      if (revision === requestRevision.current)
        setError(
          caught instanceof Error
            ? caught.message
            : "The prediction service is unavailable.",
        );
    } finally {
      setBusy(false);
    }
  }

  const baseGeometry = [numbers.length, numbers.width, numbers.height].every(
    (value) => Number(value) > 0,
  )
    ? {
        length: Number(numbers.length),
        width: Number(numbers.width),
        height: Number(numbers.height),
      }
    : null;
  const shownGeometry = generation?.candidates[0]?.room || baseGeometry;
  const geometry = shownGeometry
    ? {
        length: shownGeometry.length,
        width: shownGeometry.width,
        height: shownGeometry.height,
      }
    : null;
  const studied = renderFor(
    prediction?.support.nearest_room_id ||
      generation?.candidates[0]?.support.nearest_room_id ||
      null,
  );
  const presetRooms =
    research.status === "ready"
      ? research.data.rooms.filter(completePreset)
      : [];
  const linkedRoomUnavailable = Boolean(
    linkedRoom &&
      research.status === "ready" &&
      !presetRooms.some((room) => room.id === linkedRoom),
  );

  return (
    <>
      <PageHeading
        eyebrow="05 / Experimental design tool"
        title="Design Studio"
        intro="Enter a room, choose an emotional target and inspect a predicted fused response. Or ask the search for a feasible room whose Neuro-Score is closest to a separate requested number. This is an experimental model interface, not a measured experience."
      />
      <div className={`readiness ${readiness}`} role="status">
        <strong>
          Live model:{" "}
          {readiness === "checking"
            ? "checking…"
            : readiness === "ready"
              ? "ready for experimental requests"
              : "offline or unavailable"}
        </strong>
        <span>
          {meta
            ? `Model status: ${modelStatusLabel(meta.model_status)}.`
            : "Static room references and research pages remain available."}
        </span>
        <button type="button" className="subtle" onClick={checkReadiness}>
          Check again
        </button>
      </div>
      {meta?.model_status === "baseline_only" && (
        <Notice title="Baseline-only model" warning>
          <p>
            The current fitted model returns a baseline fused position and does
            not respond to spatial geometry. Changing the emotional target
            changes the proximity score; changing room attributes does not
            establish a learned spatial effect. Closest-score search still
            checks physical constraints and reports the returned candidate
            honestly.
          </p>
        </Notice>
      )}
      <div className="studio-layout">
        <div className="studio-form">
          <form onSubmit={submit}>
            <section>
              <div className="section-heading">
                <div>
                  <p className="eyebrow">01 · Input</p>
                  <h2>Describe a room</h2>
                </div>
              </div>
              <p>
                Use a studied-room preset as a starting point or enter your own
                independent room attributes. The current E3 model requires every
                listed attribute. Complete Experiment 3 presets fill them from
                source records; enter all fields for a custom room.
              </p>
              <label className="field preset-select">
                Studied-room preset
                <select
                  value={selectedPreset}
                  onChange={(event) => {
                    const found = presetRooms.find(
                      (room) => room.id === event.target.value,
                    );
                    setSelectedPreset(event.target.value);
                    if (found) {
                      setNumbers(presetNumbers(found));
                      setSpaceType(
                        (found.independent_attributes
                          ?.space_type as RoomInput["space_type"]) || null,
                      );
                      setDayNight(
                        (found.independent_attributes
                          ?.day_or_night as RoomInput["day_or_night"]) || null,
                      );
                    }
                  }}
                >
                  <option value="">Custom room</option>
                  {presetRooms.map((room) => (
                    <option key={room.id} value={room.id}>
                      {room.id} · Experiment {room.experiment}
                    </option>
                  ))}
                </select>
              </label>
              {linkedRoomUnavailable && (
                <p className="small-text">
                  The linked room is not a complete Experiment 3 model preset.
                  Choose a listed preset or enter all required attributes.
                </p>
              )}
              <div className="room-field-groups">
                {groups.map((group) => (
                  <fieldset key={group.title}>
                    <legend>{group.title}</legend>
                    <div className="studio-fields">
                      {group.fields.map((field) => (
                        <div className="studio-field" key={field.key}>
                          <label className="field">
                            {field.label}{" "}
                            {field.unit && <small>{field.unit}</small>}
                            <input
                              type="number"
                              aria-label={field.label}
                              value={numbers[field.key]}
                              min={field.min}
                              max={field.max}
                              step={field.integer ? "1" : "any"}
                              required={field.required}
                              onWheel={preventWheelChange}
                              onChange={(event) => {
                                setNumbers((current) => ({
                                  ...current,
                                  [field.key]: event.target.value,
                                }));
                                setSelectedPreset("");
                              }}
                            />
                          </label>
                          <label className="lock-label">
                            <input
                              type="checkbox"
                              checked={locks.includes(field.key)}
                              onChange={(event) =>
                                setLocks((current) =>
                                  event.target.checked
                                    ? [...current, field.key]
                                    : current.filter(
                                        (key) => key !== field.key,
                                      ),
                                )
                              }
                            />
                            Lock for generation
                          </label>
                        </div>
                      ))}
                    </div>
                  </fieldset>
                ))}
              </div>
              <div className="form-grid">
                <label className="field">
                  Time of day
                  <select
                    value={dayNight || ""}
                    onChange={(event) =>
                      setDayNight(
                        (event.target.value as RoomInput["day_or_night"]) ||
                          null,
                      )
                    }
                  >
                    <option value="">Unspecified</option>
                    <option value="Day">Day</option>
                    <option value="Night">Night</option>
                  </select>
                </label>
                <label className="field">
                  Space type
                  <select
                    value={spaceType || ""}
                    onChange={(event) =>
                      setSpaceType(
                        (event.target.value as RoomInput["space_type"]) || null,
                      )
                    }
                  >
                    <option value="">Unspecified</option>
                    {spaceTypes.map((value) => (
                      <option key={value}>{value}</option>
                    ))}
                  </select>
                </label>
              </div>
            </section>
            <section>
              <p className="eyebrow">02 · Target</p>
              <h2>Choose an emotional target</h2>
              <p>
                The target is a point on the signed valence–arousal plane. Both
                Studio actions use the same target; it remains separate from the
                requested numeric score.
              </p>
              <TargetPlane
                target={target}
                onChange={setTarget}
                predicted={
                  prediction?.prediction ||
                  generation?.candidates[0]?.prediction ||
                  null
                }
              />
              <div className="form-grid">
                <label className="field">
                  Target valence
                  <input
                    type="number"
                    value={target.valence}
                    min="-1"
                    max="1"
                    step="0.01"
                    required
                    onWheel={preventWheelChange}
                    onChange={(event) =>
                      setTarget((current) => ({
                        ...current,
                        valence: Number(event.target.value),
                      }))
                    }
                  />
                </label>
                <label className="field">
                  Target arousal
                  <input
                    type="number"
                    value={target.arousal}
                    min="-1"
                    max="1"
                    step="0.01"
                    required
                    onWheel={preventWheelChange}
                    onChange={(event) =>
                      setTarget((current) => ({
                        ...current,
                        arousal: Number(event.target.value),
                      }))
                    }
                  />
                </label>
              </div>
            </section>
            <section>
              <p className="eyebrow">03 · Explore</p>
              <div className="studio-actions">
                <div>
                  <h2>Predict this room</h2>
                  <p>
                    Estimate fused valence and arousal, then score proximity to
                    your emotional target.
                  </p>
                  <button
                    type="submit"
                    value="predict"
                    disabled={busy || readiness !== "ready"}
                  >
                    Predict fused response
                  </button>
                </div>
                <div>
                  <h2>Generate close to a score</h2>
                  <p>
                    Search feasible configurations that approach your chosen
                    number. A request for 65 seeks the closest score, not a
                    minimum of 65.
                  </p>
                  <label className="field">
                    Requested Neuro-Score (0–100)
                    <input
                      type="number"
                      value={requestedScore}
                      min="0"
                      max="100"
                      step="0.1"
                      onWheel={preventWheelChange}
                      onChange={(event) =>
                        setRequestedScore(event.target.value)
                      }
                    />
                  </label>
                  <details className="range-controls">
                    <summary>Allowed ranges for generation</summary>
                    <p className="small-text">
                      Enter both bounds for any attribute you want to constrain.
                      Locks preserve the entered value exactly.
                    </p>
                    <div className="range-grid">
                      {fields.map((field) => (
                        <div key={field.key}>
                          <span>
                            {field.label} {field.unit}
                          </span>
                          <label>
                            Minimum
                            <input
                              aria-label={`${field.label} range minimum`}
                              type="number"
                              min={field.min}
                              max={field.max}
                              step={field.integer ? "1" : "any"}
                              value={bounds[field.key].minimum}
                              onWheel={preventWheelChange}
                              onChange={(event) =>
                                setBounds((current) => ({
                                  ...current,
                                  [field.key]: {
                                    ...current[field.key],
                                    minimum: event.target.value,
                                  },
                                }))
                              }
                            />
                          </label>
                          <label>
                            Maximum
                            <input
                              aria-label={`${field.label} range maximum`}
                              type="number"
                              min={field.min}
                              max={field.max}
                              step={field.integer ? "1" : "any"}
                              value={bounds[field.key].maximum}
                              onWheel={preventWheelChange}
                              onChange={(event) =>
                                setBounds((current) => ({
                                  ...current,
                                  [field.key]: {
                                    ...current[field.key],
                                    maximum: event.target.value,
                                  },
                                }))
                              }
                            />
                          </label>
                        </div>
                      ))}
                    </div>
                  </details>
                  <button
                    type="submit"
                    value="generate"
                    className="subtle"
                    disabled={busy || readiness !== "ready"}
                  >
                    Generate closest-score rooms
                  </button>
                </div>
              </div>
            </section>
          </form>
        </div>
        <aside className="studio-output">
          <Massing geometry={geometry} />
          <div className="studio-result">
            <p className="eyebrow">Experimental output</p>
            <h2 tabIndex={-1} ref={resultHeading}>
              What the model returned
            </h2>
            <p role="status" className="small-text">
              {prediction
                ? `Prediction ready. Neuro-Score ${(prediction.prediction.neuro_score * 100).toFixed(1)} of 100.`
                : generation
                  ? generation.candidates.length
                    ? `${generation.candidates.length} closest-score candidates ready.`
                    : "No feasible candidate for this request."
                  : busy
                    ? "Calculating with the live model…"
                    : ""}
            </p>
            {busy && <p role="status">Calculating with the live model…</p>}
            {error && (
              <p role="alert" className="status error">
                {error}
              </p>
            )}
            {prediction && (
              <>
                <div className="score-readout">
                  <strong>
                    {(prediction.prediction.neuro_score * 100).toFixed(1)}
                  </strong>
                  <span>
                    Neuro-Score / 100
                    <br />
                    proximity to your target
                  </span>
                </div>
                <dl>
                  <div>
                    <dt>Predicted fused valence</dt>
                    <dd>
                      <Value value={prediction.prediction.valence} />
                    </dd>
                  </div>
                  <div>
                    <dt>Predicted fused arousal</dt>
                    <dd>
                      <Value value={prediction.prediction.arousal} />
                    </dd>
                  </div>
                  <div>
                    <dt>Studied support</dt>
                    <dd>{supportLabel(prediction.support.status)}</dd>
                  </div>
                </dl>
                <p className="small-text">
                  Model: {modelStatusLabel(prediction.model_status)}.{" "}
                  {prediction.prediction.projected
                    ? "The raw output was projected into the declared affect domain before scoring."
                    : "The raw output was inside the declared affect domain."}
                </p>
                {prediction.limitations.map((limit, index) => (
                  <p className="small-text" key={index}>
                    {limit}
                  </p>
                ))}
              </>
            )}
            {generation &&
              (generation.candidates.length ? (
                <>
                  <p>
                    Requested score:{" "}
                    <strong>
                      <Value
                        value={generation.candidates[0].requested_score}
                        unit="/ 100"
                      />
                    </strong>
                  </p>
                  <div className="table-wrap">
                    <table className="data-table">
                      <caption>
                        Generated candidates ordered by absolute distance to the
                        requested Neuro-Score.
                      </caption>
                      <thead>
                        <tr>
                          <th scope="col">Candidate</th>
                          <th scope="col">Achieved / 100</th>
                          <th scope="col">Difference</th>
                          <th scope="col">Dimensions (m)</th>
                          <th scope="col">Support</th>
                        </tr>
                      </thead>
                      <tbody>
                        {generation.candidates.map((candidate, index) => (
                          <tr key={index}>
                            <th scope="row">{index + 1}</th>
                            <td>
                              <Value value={candidate.achieved_score} />
                            </td>
                            <td>
                              <Value value={candidate.absolute_difference} />
                            </td>
                            <td>
                              {candidate.room.length.toFixed(2)} ×{" "}
                              {candidate.room.width.toFixed(2)} ×{" "}
                              {candidate.room.height.toFixed(2)}
                            </td>
                            <td>
                              {supportLabel(candidate.support.status)}
                              {candidate.support.nearest_room_id
                                ? ` · ${candidate.support.nearest_room_id}`
                                : ""}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div className="candidate-parameters-list">
                    {generation.candidates.map((candidate, index) => (
                      <CandidateParameters
                        key={index}
                        candidate={candidate}
                        index={index}
                      />
                    ))}
                  </div>
                  <p className="small-text">
                    The highlighted schematic uses the closest returned
                    candidate. {generation.samples_evaluated} feasible samples
                    evaluated in this bounded search.
                  </p>
                  {generation.limitations.map((limit, index) => (
                    <p className="small-text" key={index}>
                      {limit}
                    </p>
                  ))}
                </>
              ) : (
                <Notice title="No feasible candidate">
                  <p>
                    {generation.reason ||
                      "No candidate met the current locks and ranges within the search budget."}
                  </p>
                </Notice>
              ))}
            {!busy && !error && !prediction && !generation && (
              <p className="small-text">
                A live fused prediction or candidate search will appear here
                when the model is ready.
              </p>
            )}
          </div>
          {studied && (
            <div className="studied-reference">
              <img
                src={studied.preview}
                alt={`Original render of studied room ${studied.id}`}
              />
              <div>
                <strong>Closest studied-room reference: {studied.id}</strong>
                <p>
                  This is a source render of a studied room. It is not an image
                  of the entered or generated room.
                </p>
                <Link to={`/rooms?room=${studied.id}`}>
                  View studied room ↗
                </Link>
              </div>
            </div>
          )}
        </aside>
      </div>
      <div className="studio-footer">
        <p>
          Neuro-Score measures proximity of a predicted fused point to your
          chosen emotional target. It is not model confidence, a physiological
          measurement or a general room-quality grade.
        </p>
        <Link to="/prediction">See the held-out model evidence ↗</Link>
      </div>
    </>
  );
}
