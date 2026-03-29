/**
 * Reference only — the API uses generated qcad_run_job_gen.js with the job JSON
 * embedded (JSON.parse(...)) so QCAD never reads job.json via QFile.
 */

include("scripts/File/Print/Print.js");

function main() {
    qWarning("Use qcad_run_job_gen.js from the API temp folder, not this file.");
}

main();
