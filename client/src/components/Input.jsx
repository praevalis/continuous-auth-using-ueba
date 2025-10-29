const Input = ({ data, setData, type, name, label }) => {
    const handleChange = (e) => {
        setData((prev) => ({
            ...prev,
            [name]: e.target.value,
        }));
    };

    return (
        <div className="flex flex-col gap-1 w-full relative">
            <label htmlFor={name} className="text-gray-600">
                {label}
            </label>
            <input
                id={name}
                name={name}
                type={type}
                value={data[name]}
                onChange={handleChange}
                className="w-full px-3 py-1 rounded-sm focus:outline-none focus:border bg-white border border-gray-200 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
            />
        </div>
    );
};

export default Input;
