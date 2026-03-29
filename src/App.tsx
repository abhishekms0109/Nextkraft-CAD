import { useState } from "react";
import type { FormEvent } from "react";

export default function App() {
  const [lengthMm, setLengthMm] = useState("");
  const [widthMm, setWidthMm] = useState("");
  const [heightMm, setHeightMm] = useState("");
  const [suvPercent, setSuvPercent] = useState("");
  const [sedanPercent, setSedanPercent] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const length = Number(lengthMm);
    const width = Number(widthMm);
    const height = Number(heightMm);
    const suv = Number(suvPercent);
    const sedan = Number(sedanPercent);
    if (
      [length, width, height, suv, sedan].some(
        (n) => Number.isNaN(n) || n <= 0,
      )
    ) {
      setError("Enter positive numbers for all fields.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          length_mm: length,
          width_mm: width,
          height_mm: height,
          suv_percent: suv,
          sedan_percent: sedan,
        }),
      });
      if (!res.ok) {
        const detail = await res
          .json()
          .catch(() => ({ detail: res.statusText }));
        const d = detail?.detail;
        let msg: string;
        if (typeof d === "string") {
          msg = d;
        } else if (Array.isArray(d)) {
          msg = d.map((x: { msg?: string }) => x?.msg ?? "").join(" ");
        } else {
          msg = JSON.stringify(detail);
        }
        throw new Error(msg || `Request failed (${res.status})`);
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "nextkraft-parking.pdf";
      a.rel = "noopener";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1 className="page-title">Nextkraft CAD</h1>
        <p className="page-subtitle">Parameter input</p>
      </header>

      <main className="page-main">
        {error ? (
          <p className="field__hint" style={{ color: "#c44", marginBottom: "1rem" }}>
            {error}
          </p>
        ) : null}
        <form className="param-form" onSubmit={handleSubmit} noValidate>
          <div className="param-form__grid">
            <label className="field">
              <span className="field__label">Length Available</span>
              <span className="field__hint">Parameter values in mm</span>
              <input
                className="field__input"
                type="number"
                name="lengthMm"
                min={0}
                step="any"
                placeholder="e.g. 5000"
                value={lengthMm}
                onChange={(e) => setLengthMm(e.target.value)}
                inputMode="decimal"
                disabled={loading}
              />
            </label>

            <label className="field">
              <span className="field__label">Width Available</span>
              <span className="field__hint">Parameter values in mm</span>
              <input
                className="field__input"
                type="number"
                name="widthMm"
                min={0}
                step="any"
                placeholder="e.g. 2500"
                value={widthMm}
                onChange={(e) => setWidthMm(e.target.value)}
                inputMode="decimal"
                disabled={loading}
              />
            </label>

            <label className="field">
              <span className="field__label">Height Available</span>
              <span className="field__hint">Parameter values in mm</span>
              <input
                className="field__input"
                type="number"
                name="heightMm"
                min={0}
                step="any"
                placeholder="e.g. 2200"
                value={heightMm}
                onChange={(e) => setHeightMm(e.target.value)}
                inputMode="decimal"
                disabled={loading}
              />
            </label>

            <label className="field">
              <span className="field__label">SUV CAR</span>
              <span className="field__hint">Parameter values in %</span>
              <input
                className="field__input"
                type="number"
                name="suvPercent"
                min={0}
                max={100}
                step="any"
                placeholder="e.g. 40"
                value={suvPercent}
                onChange={(e) => setSuvPercent(e.target.value)}
                inputMode="decimal"
                disabled={loading}
              />
            </label>

            <label className="field">
              <span className="field__label">SEDAN Car</span>
              <span className="field__hint">Parameter values in %</span>
              <input
                className="field__input"
                type="number"
                name="sedanPercent"
                min={0}
                max={100}
                step="any"
                placeholder="e.g. 60"
                value={sedanPercent}
                onChange={(e) => setSedanPercent(e.target.value)}
                inputMode="decimal"
                disabled={loading}
              />
            </label>
          </div>

          <div className="param-form__actions">
            <button type="submit" className="btn-submit" disabled={loading}>
              {loading ? "Generating…" : "Submit"}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
