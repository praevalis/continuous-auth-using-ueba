import { useState } from "react";
import { FaUserCheck } from "react-icons/fa";
import { FaUserXmark } from "react-icons/fa6";

import Input from "./Input";

const Prediction = () => {
    const [data, setData] = useState({
        user: "U1",
        computer: "C1",
        timestamp: 0,
    });

    const [result, setResult] = useState(null);
    const [error, setError] = useState("");

    const handleSubmit = async () => {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/infer`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            console.log(`Error while requesting API: ${response.statusText}`);
            setError(response.statusText);
        } else {
            const json = await response.json();
            setResult(json);
        }
    };

    return (
        <div className="h-screen relative">
            <div className="h-1/2 bg-blue-50 absolute top-0 left-0 w-full"></div>
            <section className="flex absolute top-1/2 -translate-y-1/2 left-70 right-70 bg-white shadow-lg rounded-sm">
                <div className="w-1/2 flex flex-col gap-4 px-6 py-10">
                    <Input
                        data={data}
                        setData={setData}
                        name={"user"}
                        type="text"
                        label={"User"}
                    />

                    <Input
                        data={data}
                        setData={setData}
                        name={"computer"}
                        type="text"
                        label={"Computer"}
                    />

                    <Input
                        data={data}
                        setData={setData}
                        name={"timestamp"}
                        type="number"
                        label={"Timestamp"}
                    />

                    <button
                        onClick={handleSubmit}
                        type="button"
                        className="px-3 py-1 mt-4 text-white bg-blue-400 hover:bg-blue-600 rounded-sm"
                    >
                        Submit
                    </button>
                </div>
                <div className="flex flex-col items-center justify-center w-1/2 px-6 py-10">
                    {error && <p className="text-red-600">Error: {error}</p>}

                    {result ? (
                        <div>
                            {result["anomaly"] ? (
                                <div className="flex flex-col items-center gap-3">
                                    <div className="flex items-center gap-2 text-red-500">
                                        <FaUserXmark className="text-5xl" />
                                        <p>
                                            <strong>Anomalous User</strong>
                                        </p>
                                    </div>
                                    <p className="text-gray-500">
                                        Risk Score: {result["risk_score"]}
                                    </p>
                                </div>
                            ) : (
                                <div className="flex flex-col items-center gap-3">
                                    <div className="flex items-center gap-2 text-green-500">
                                        <FaUserCheck className="text-5xl" />
                                        <p>
                                            <strong>Safe User</strong>
                                        </p>
                                    </div>
                                    <p className="text-gray-500">
                                        Risk Score: {result["risk_score"]}
                                    </p>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div>
                            <p className="text-sm text-gray-500">
                                Submit input for prediction.
                            </p>
                        </div>
                    )}
                </div>
            </section>
        </div>
    );
};

export default Prediction;
