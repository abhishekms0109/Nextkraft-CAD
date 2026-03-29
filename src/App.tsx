import { useState } from "react";
import type { FormEvent } from "react";

export default function App() {
  const [lengthMm, setLengthMm] = useState("");
  const [widthMm, setWidthMm] = useState("");
  const [heightMm, setHeightMm] = useState("");
  const [suvPercent, setSuvPercent] = useState("");
  const [sedanPercent, setSedanPercent] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1 className="page-title">Nextkraft CAD</h1>
        <p className="page-subtitle">Parameter input</p>
      </header>

      <main className="page-main">
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
              />
            </label>
          </div>

          <div className="param-form__actions">
            <button type="submit" className="btn-submit">
              Submit
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
