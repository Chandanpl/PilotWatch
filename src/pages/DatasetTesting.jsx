import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

export default function DatasetTesting() {

    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");

    const handleFileChange = (event) => {

        const selectedFile = event.target.files[0];

        setError("");
        setResult(null);

        if (!selectedFile) {
            setFile(null);
            return;
        }

        if (
            !selectedFile.name
                .toLowerCase()
                .endsWith(".zip")
        ) {
            setError(
                "Please select a ZIP dataset file."
            );

            setFile(null);
            return;
        }

        setFile(selectedFile);
    };


    const uploadDataset = async () => {

        if (!file) {
            setError(
                "Please select a dataset ZIP file."
            );
            return;
        }

        setUploading(true);
        setError("");
        setResult(null);

        const formData = new FormData();

        formData.append(
            "file",
            file
        );

        try {

            const response = await fetch(
                `${API_URL}/dataset/upload`,
                {
                    method: "POST",
                    body: formData
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail ||
                    "Dataset upload failed"
                );
            }

            setResult(data);

        } catch (err) {

            setError(
                err.message
            );

        } finally {

            setUploading(false);
        }
    };


    const formatSize = (bytes) => {

        if (!bytes) return "--";

        const mb =
            Number(bytes) /
            (1024 * 1024);

        return `${mb.toFixed(2)} MB`;
    };


    return (
        <div
            style={{
                padding: "30px",
                maxWidth: "1100px",
                margin: "auto"
            }}
        >

            <h1>
                Dataset Testing
            </h1>

            <p>
                Upload and validate a YOLO
                dataset before model training.
            </p>


            {/* Upload Section */}

            <div
                style={{
                    marginTop: "25px",
                    padding: "25px",
                    border: "1px solid #ddd",
                    borderRadius: "12px"
                }}
            >

                <h2>
                    Upload Dataset
                </h2>

                <input
                    type="file"
                    accept=".zip"
                    onChange={handleFileChange}
                />

                {file && (
                    <p>
                        Selected:
                        <strong>
                            {" "}{file.name}
                        </strong>
                    </p>
                )}

                <button
                    onClick={uploadDataset}
                    disabled={
                        !file ||
                        uploading
                    }
                    style={{
                        marginTop: "15px",
                        padding: "10px 20px",
                        cursor:
                            !file || uploading
                                ? "not-allowed"
                                : "pointer"
                    }}
                >
                    {uploading
                        ? "Uploading & Validating..."
                        : "Validate Dataset"}
                </button>

            </div>


            {/* Error */}

            {error && (
                <div
                    style={{
                        marginTop: "20px",
                        padding: "15px",
                        background: "#ffe5e5",
                        borderRadius: "8px"
                    }}
                >
                    ❌ {error}
                </div>
            )}


            {/* Result */}

            {result && (
                <div
                    style={{
                        marginTop: "30px"
                    }}
                >

                    <h2>
                        Dataset Information
                    </h2>


                    <div
                        style={{
                            display: "grid",
                            gridTemplateColumns:
                                "repeat(auto-fit, minmax(180px, 1fr))",
                            gap: "15px"
                        }}
                    >

                        <InfoCard
                            title="Images"
                            value={result.images}
                        />

                        <InfoCard
                            title="Labels"
                            value={result.labels}
                        />

                        <InfoCard
                            title="ZIP Size"
                            value={formatSize(result.size)}
                        />

                        <InfoCard
                            title="Structure"
                            value={
                                result.dataset_structure
                            }
                        />

                    </div>


                    {/* Dataset validation */}

                    <div
                        style={{
                            marginTop: "25px",
                            padding: "25px",
                            border: "1px solid #ddd",
                            borderRadius: "12px"
                        }}
                    >

                        <h2>
                            Dataset Validation
                        </h2>

                        <ValidationRow
                            name="data.yaml"
                            passed={
                                result.validation
                                    ?.data_yaml_found
                            }
                        />

                        <ValidationRow
                            name="Images"
                            passed={
                                result.validation
                                    ?.images_found
                            }
                        />

                        <ValidationRow
                            name="Labels"
                            passed={
                                result.validation
                                    ?.labels_found
                            }
                        />

                        <ValidationRow
                            name="Train split"
                            passed={
                                result.validation
                                    ?.train_found
                            }
                        />

                        <ValidationRow
                            name="Validation split"
                            passed={
                                result.validation
                                    ?.validation_found
                            }
                        />

                        <ValidationRow
                            name="Test split"
                            passed={
                                result.validation
                                    ?.test_found
                            }
                        />

                        <ValidationRow
                            name="Image ↔ Label matching"
                            passed={
                                result.validation
                                    ?.image_label_match
                            }
                        />

                    </div>


                    {/* Problems */}

                    {(result.missing_label_count > 0 ||
                        result.unmatched_label_count > 0) && (

                            <div
                                style={{
                                    marginTop: "25px",
                                    padding: "20px",
                                    border:
                                        "1px solid #f0ad4e",
                                    borderRadius: "12px"
                                }}
                            >

                                <h2>
                                    ⚠ Dataset Issues
                                </h2>

                                <p>
                                    Missing labels:
                                    <strong>
                                        {" "}
                                        {
                                            result.missing_label_count
                                        }
                                    </strong>
                                </p>

                                <p>
                                    Unmatched labels:
                                    <strong>
                                        {" "}
                                        {
                                            result.unmatched_label_count
                                        }
                                    </strong>
                                </p>

                                {result.unmatched_labels?.length > 0 && (
                                    <div>
                                        <strong>
                                            Example unmatched labels:
                                        </strong>

                                        <ul>
                                            {result.unmatched_labels
                                                .slice(0, 10)
                                                .map(
                                                    (item, index) => (
                                                        <li
                                                            key={index}
                                                        >
                                                            {item}
                                                        </li>
                                                    )
                                                )}
                                        </ul>
                                    </div>
                                )}

                            </div>
                        )}


                    {/* Final status */}

                    <div
                        style={{
                            marginTop: "25px",
                            padding: "25px",
                            borderRadius: "12px",
                            border: "2px solid",
                            borderColor:
                                result.ready_for_training
                                    ? "green"
                                    : "red"
                        }}
                    >

                        <h2>
                            {result.ready_for_training
                                ? "🟢 Dataset READY for Training"
                                : "🔴 Dataset NOT Ready for Training"}
                        </h2>

                        <p>
                            {result.ready_for_training
                                ? "All required YOLO dataset components are valid."
                                : "Fix the dataset issues before starting training."}
                        </p>


                        {result.ready_for_training && (
                            <button
                                style={{
                                    marginTop: "10px",
                                    padding:
                                        "12px 25px",
                                    cursor: "pointer"
                                }}
                            >
                                Train YOLO Model
                            </button>
                        )}

                    </div>


                    {/* Drive */}

                    {result.drive_link && (
                        <div
                            style={{
                                marginTop: "20px"
                            }}
                        >

                            <a
                                href={
                                    result.drive_link
                                }
                                target="_blank"
                                rel="noreferrer"
                            >
                                Open Dataset in Google Drive
                            </a>

                        </div>
                    )}

                </div>
            )}

        </div>
    );
}


/* -------------------------------- */
/* Info Card */
/* -------------------------------- */

function InfoCard({
    title,
    value
}) {

    return (
        <div
            style={{
                padding: "20px",
                border: "1px solid #ddd",
                borderRadius: "10px"
            }}
        >

            <div>
                {title}
            </div>

            <h2>
                {value}
            </h2>

        </div>
    );
}


/* -------------------------------- */
/* Validation Row */
/* -------------------------------- */

function ValidationRow({
    name,
    passed
}) {

    return (
        <div
            style={{
                display: "flex",
                justifyContent:
                    "space-between",
                padding: "10px 0",
                borderBottom:
                    "1px solid #eee"
            }}
        >

            <span>
                {name}
            </span>

            <strong>
                {passed
                    ? "✓ PASS"
                    : "✗ FAIL"}
            </strong>

        </div>
    );
}