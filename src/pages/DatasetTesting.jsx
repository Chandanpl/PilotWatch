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

        if (!selectedFile.name.toLowerCase().endsWith(".zip")) {
            setError("Please select a ZIP dataset file.");
            setFile(null);
            return;
        }

        setFile(selectedFile);
    };


    const uploadDataset = async () => {

        if (!file) {
            setError("Please select a dataset ZIP file.");
            return;
        }

        setUploading(true);
        setError("");
        setResult(null);

        const formData = new FormData();

        formData.append("file", file);

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
                    data.detail || "Dataset upload failed"
                );
            }

            setResult(data);

        } catch (err) {

            setError(err.message);

        } finally {

            setUploading(false);

        }
    };


    return (
        <div
            style={{
                minHeight: "100vh",
                padding: "40px",
                background: "#f4f7fb",
                fontFamily: "Arial, sans-serif"
            }}
        >

            <div
                style={{
                    maxWidth: "900px",
                    margin: "0 auto"
                }}
            >

                <h1
                    style={{
                        marginBottom: "8px",
                        color: "#172033"
                    }}
                >
                    Dataset Testing
                </h1>

                <p
                    style={{
                        color: "#64748b",
                        marginBottom: "30px"
                    }}
                >
                    Upload a YOLO-compatible railway dataset for
                    validation and model training.
                </p>


                {/* Upload Card */}

                <div
                    style={{
                        background: "#ffffff",
                        padding: "30px",
                        borderRadius: "14px",
                        border: "1px solid #e2e8f0",
                        marginBottom: "25px"
                    }}
                >

                    <h2
                        style={{
                            marginTop: 0,
                            color: "#1e293b"
                        }}
                    >
                        Upload Dataset
                    </h2>

                    <p
                        style={{
                            color: "#64748b"
                        }}
                    >
                        Select your complete dataset as a ZIP file.
                    </p>


                    <input
                        type="file"
                        accept=".zip"
                        onChange={handleFileChange}
                    />


                    {file && (
                        <div
                            style={{
                                marginTop: "20px",
                                padding: "15px",
                                background: "#f1f5f9",
                                borderRadius: "8px"
                            }}
                        >
                            <strong>Selected Dataset:</strong>

                            <div>
                                {file.name}
                            </div>

                            <div
                                style={{
                                    color: "#64748b",
                                    fontSize: "14px",
                                    marginTop: "5px"
                                }}
                            >
                                Size:{" "}
                                {(file.size / (1024 * 1024)).toFixed(2)}
                                {" "}MB
                            </div>
                        </div>
                    )}


                    <button
                        onClick={uploadDataset}
                        disabled={!file || uploading}
                        style={{
                            marginTop: "20px",
                            padding: "12px 24px",
                            border: "none",
                            borderRadius: "8px",
                            background:
                                !file || uploading
                                    ? "#94a3b8"
                                    : "#1d4ed8",
                            color: "#ffffff",
                            cursor:
                                !file || uploading
                                    ? "not-allowed"
                                    : "pointer",
                            fontSize: "15px",
                            fontWeight: "600"
                        }}
                    >
                        {uploading
                            ? "Uploading Dataset..."
                            : "Upload Dataset"}
                    </button>


                    {error && (
                        <div
                            style={{
                                marginTop: "20px",
                                padding: "12px",
                                borderRadius: "8px",
                                background: "#fee2e2",
                                color: "#b91c1c"
                            }}
                        >
                            {error}
                        </div>
                    )}

                </div>


                {/* Result */}

                {result && (

                    <div
                        style={{
                            background: "#ffffff",
                            padding: "30px",
                            borderRadius: "14px",
                            border: "1px solid #e2e8f0"
                        }}
                    >

                        <h2
                            style={{
                                marginTop: 0,
                                color: "#1e293b"
                            }}
                        >
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
                                title="Train"
                                value={
                                    result.train_available
                                        ? "Available"
                                        : "Missing"
                                }
                            />

                            <InfoCard
                                title="Validation"
                                value={
                                    result.validation_available
                                        ? "Available"
                                        : "Missing"
                                }
                            />

                            <InfoCard
                                title="Test"
                                value={
                                    result.test_available
                                        ? "Available"
                                        : "Missing"
                                }

                            />

                        </div>


                        <div
                            style={{
                                marginTop: "25px",
                                padding: "18px",
                                borderRadius: "10px",
                                background:
                                    result.ready_for_training
                                        ? "#dcfce7"
                                        : "#fef3c7",
                                color:
                                    result.ready_for_training
                                        ? "#166534"
                                        : "#92400e"
                            }}
                        >

                            <strong>
                                {result.ready_for_training
                                    ? "✓ Dataset Ready for Training"
                                    : "⚠ Dataset Requires Validation"}
                            </strong>

                            <p
                                style={{
                                    marginBottom: 0
                                }}
                            >
                                {result.data_yaml
                                    ? `Configuration file: ${result.data_yaml}`
                                    : "data.yaml was not found."}
                            </p>

                        </div>

                    </div>

                )}

            </div>

        </div>
    );
}


function InfoCard({ title, value }) {

    return (

        <div
            style={{
                padding: "18px",
                background: "#f8fafc",
                borderRadius: "10px",
                border: "1px solid #e2e8f0"
            }}
        >

            <div
                style={{
                    fontSize: "13px",
                    color: "#64748b",
                    marginBottom: "7px"
                }}
            >
                {title}
            </div>

            <div
                style={{
                    fontSize: "20px",
                    fontWeight: "700",
                    color: "#0f172a"
                }}
            >
                {value}
            </div>

        </div>
    );
}